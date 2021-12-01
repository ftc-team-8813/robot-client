public class blah{
    public static void main(String[] args) {
        double delta_y = 60 - 0; // Flipped to change power direction
        double delta_x = 0 - 20;
        double heading = 0;
        
        double relative_heading = Math.atan2(delta_y, delta_x) * (180/Math.PI) + heading;
        double vector = Math.sqrt(Math.pow(delta_y, 2) + Math.pow(delta_x, 2));
        double strafe_distance = Math.sin(relative_heading * (Math.PI/180)) * vector;
        double forward_distance = Math.cos(relative_heading * (Math.PI/180)) * vector;

        System.out.println(strafe_distance);
        System.out.println(forward_distance);
    }
}