import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.lang.ref.WeakReference;
import java.net.ServerSocket;
import java.net.Socket;
import java.net.SocketException;
import java.nio.ByteBuffer;
import java.util.HashMap;

public class Server
{

    private Thread workerThread;
    private SocketWorker worker;
    
    public static final int STATE_CONNECTING     = 0;
    public static final int STATE_RECV_COMMAND   = 1;
    public static final int STATE_AWAIT_RESPONSE = 2;
    public static final int STATE_SEND_RESPONSE  = 3;
    public static final int STATE_CLOSED         = 4;
    public static final String[] statuses = {
            "Connecting", "Receive Command", "Await Response", "Send Response", "Closed"
    };
    
    public static final int CMD_ECHO             = 0x00;
    public static final int CMD_CLOSE            = 0xFF;
    public static final int RESP_MULTI           = 0xFE;
    
    private HashMap<Integer, CommandProcessor> processors;
    
    private static final String TAG = "Data Server";
    
    public Server(int port)
    {
        processors = new HashMap<>();
        worker = new SocketWorker(port);
        workerThread = new Thread(worker);
    }
    
    public void registerProcessor(int id, CommandProcessor processor)
    {
        if (id < 0 || id > 255)
            throw new IllegalArgumentException("Command must be between 0 and 255");
        if (id == CMD_ECHO || id == CMD_CLOSE || id == RESP_MULTI)
            throw new IllegalArgumentException(String.format("Reserved command ID %d", id));
        processors.put(id, processor);
    }
    
    public void startServer()
    {
        workerThread.start();
    }
    
    public String getStatus()
    {
        return statuses[worker.state];
    }
    
    public void close()
    {
        try
        {
            ServerSocket server = worker.server.get();
            if (server != null && !server.isClosed())
            {
                System.out.println("Closing server");
                server.close();
            }
            if (worker.connection != null)
            {
                Socket conn = worker.connection.get();
                if (conn != null && !conn.isClosed())
                {
                    System.out.println("Closing connection");
                    conn.close();
                }
            }
        }
        catch (IOException e)
        {
            System.out.println("Unable to close server");
        }
    }
    
    public interface CommandProcessor
    {
        public void onRecv(int command, ByteBuffer payload, Responder resp);
    }
    
    private static class CmdEcho implements CommandProcessor
    {
        @Override
        public void onRecv(int command, ByteBuffer payload, Responder resp)
        {
            resp.respond(payload);
        }
    }
    
    public static class Responder
    {
        private SocketWorker worker;
        private Responder(SocketWorker worker)
        {
            this.worker = worker;
        }
        
        public void respond(ByteBuffer data)
        {
            int size = data.limit();
            if (size > 65535) worker.largeResponse = data;
            else worker.sendBuffer.put(data);
        }
    }
    
    // forced to use a thread here since async sockets are only available in the next Android version
    private class SocketWorker implements Runnable
    {
        
        private int port;
        private WeakReference<ServerSocket> server;
        private WeakReference<Socket> connection;
        /*
           Protocol: Command/response format
           - user sends a command (1 byte + some payload)
           - server sends a response (the command byte + some response payload)
           Each frame consists of:
           | 0x00 | uint8_t command byte
           | 0x01 | uint16_t payload size
           | 0x03 | payload (0-65535 bytes)
           
           After sending a command, the client should not send another command before it completely
           receives a response.
           
           Special commands:
           0x00 -- Ping: The server will simply send the payload contents (i.e. 'GNU Terry Pratchett') back to the client
           0xFF -- Close: Cleanly disconnects the client without causing an error on the server end.
                          The server responds with 0xFF before disconnecting the client.
           Special responses:
           0xFE -- Multiple Frames: If the payload is more than 65535 bytes, it will be sent in multiple frames.
                                    The payload of this response is two (unsigned) bytes, the first
                                    being the number of responses that the client should expect,
                                    and the second being the command ID that is being responded to.
                                    If the number of responses is 0, an error has occurred on the
                                    server's end and the programmer should be notified of it immediately.
                                    For each following response sent, the command ID byte is replaced by
                                    the packet number in the sequence.
         */
        private volatile int command;
        private ByteBuffer recvBuffer;
        
        private volatile int response;
        private ByteBuffer sendBuffer;
        
        private ByteBuffer largeResponse;
        
        private volatile int state;
        
        private Responder resp;
        
        public SocketWorker(int port)
        {
            this.port = port;
            resp = new Responder(this);
        }
        
        @Override
        public void run()
        {
            recvBuffer = ByteBuffer.allocate(65535);
            sendBuffer = ByteBuffer.allocate(65535);
            try (ServerSocket server = new ServerSocket(port))
            {
                // GC the server when it is closed
                this.server = new WeakReference<>(server);
                while (true)
                {
                    state = STATE_CONNECTING;
                    try (Socket sock = server.accept())
                    {
                        connection = new WeakReference<>(sock);
                        InputStream in = sock.getInputStream();
                        OutputStream out = sock.getOutputStream();
                        boolean closeConnection = false;
                        // event loop
                        while (!closeConnection)
                        {
                            // receive a command
                            state = STATE_RECV_COMMAND;
                            int command = in.read();
                            int payloadSizeH = in.read();
                            int payloadSizeL = in.read();
                            if (command < 0 || payloadSizeH < 0 || payloadSizeL < 0)
                            {
                                break;
                            }
                            int payloadSize = (payloadSizeH << 8) | payloadSizeL;
                            if (payloadSize > 0)
                            {
                                recvBuffer.clear();
                                int read = in.read(recvBuffer.array(), 0, payloadSize);
                                if (read < payloadSize)
                                {
                                    System.out.println("Connection lost [could not receive full payload]");
                                    break;
                                }
                                recvBuffer.position(payloadSize);
                            }
                            recvBuffer.flip();
                            sendBuffer.clear();
                            response = command;
                            CommandProcessor processor;
                            if (command == CMD_ECHO)
                            {
                                processor = new CmdEcho();
                            }
                            else if (command == CMD_CLOSE)
                            {
                                closeConnection = true;
                                processor = null;
                            }
                            else
                            {
                                processor = processors.get(command);
                                if (processor == null)
                                {
                                    System.out.println("No processor for command %d; echoing request");
                                    processor = new CmdEcho();
                                }
                            }
                            state = STATE_AWAIT_RESPONSE;
                            if (processor != null) processor.onRecv(command, recvBuffer, resp);
                            
                            state = STATE_SEND_RESPONSE;
                            if (largeResponse != null)
                            {
                                int size = largeResponse.limit();
                                // integer ceiling-divide; make sure there are enough packets sent to fit the entire response
                                int packetCount = size/65535 + ((size % 65535 > 0) ? 1 : 0);
                                if (packetCount > 255)
                                {
                                    System.out.println("Packet size MUCH too large: %d");
                                    packetCount = 0;
                                }
                                byte[] resp_packet = {
                                        (byte)RESP_MULTI,  // response
                                        (byte)0x00,        // size MSB
                                        (byte)0x02,        // size LSB
                                        (byte)packetCount, // packet count
                                        (byte)response     // command ID
                                };
                                out.write(resp_packet);
                                int ptr = 0;
                                for (int i = 0; i < packetCount; i++)
                                {
                                    int packetSize = Math.min(65535, size - ptr);
                                    byte[] head = {
                                            (byte)i,
                                            (byte)((packetSize >> 8) & 0xFF),
                                            (byte)(packetSize & 0xFF)
                                    };
                                    out.write(head);
                                    out.write(largeResponse.array(), ptr, packetSize);
                                    ptr += packetSize;
                                }
                                largeResponse = null; // we done with this
                            }
                            else
                            {
                                sendBuffer.flip();
                                int size = sendBuffer.limit();
                                byte[] head = {
                                        (byte)response,
                                        (byte)((size >> 8) & 0xFF),
                                        (byte)(size & 0xFF)
                                };
                                out.write(head);
                                out.write(sendBuffer.array(), 0, sendBuffer.limit());
                            }
                        }
                    }
                    catch (SocketException e)
                    {
                        if (server.isClosed()) // closed from separate thread
                        {
                            System.out.println("Server closed: %s");
                            break;
                        }
                        System.out.println("Connection failed -- listening for new connections");
                    }
                }
            } catch (IOException e)
            {
                System.out.println("Error creating server");
            }
            finally
            {
                state = STATE_CLOSED;
            }
        }
    }
}
