package server;
import java.nio.ByteBuffer;

public class TestServer{
    private static double j = 0.0;
    private static double f = 0.0;
    private static double g = 0.0;

    public static void main(String[] args) throws InterruptedException{
        Server server = new Server(18888);
        server.registerProcessor(0x1, (cmd, payload, resp) -> {
            ByteBuffer buf = ByteBuffer.allocate(100);
            buf.putDouble(j);
            buf.putDouble(f);
            buf.putDouble(g);
            buf.flip();

            resp.respond(buf);
        });
        server.startServer();

        for(int i = 0; i < 50; i++){
            j += 50;
            Thread.sleep(200);
        }
        for(int i = 0; i < 50; i++){
            f += 70;
            Thread.sleep(200);
        }
        for(int i = 0; i < 50; i++){
            g -= 50;
            Thread.sleep(200);
        }
    }
}