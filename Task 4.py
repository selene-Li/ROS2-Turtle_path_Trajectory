import rclpy
from rclpy.node import Node
from turtlesim.srv import Spawn, SetPen, Kill
from turtlesim.msg import Pose
from geometry_msgs.msg import Twist
import math
import time

class ShapeTrajectoryPID(Node):
    def __init__(self):
        super().__init__('shape_trajectory_pid_node')
        
        self.poses = {"turtle_R": None, "turtle_O": None, "turtle_S": None}

        self.kill_default_turtle()
        self.spawn_turtle("turtle_R", 1.0, 3.0)
        self.set_turtle_color("turtle_R", 255, 0, 0)
        self.spawn_turtle("turtle_O", 7.0, 5.0)
        self.set_turtle_color("turtle_O", 0, 255, 0)
        self.spawn_turtle("turtle_S", 8.0, 3.5)
        self.set_turtle_color("turtle_S", 0, 0, 255)

        self.pub_R = self.create_publisher(Twist, '/turtle_R/cmd_vel', 10)
        self.pub_O = self.create_publisher(Twist, '/turtle_O/cmd_vel', 10)
        self.pub_S = self.create_publisher(Twist, '/turtle_S/cmd_vel', 10)

        self.create_subscription(Pose, '/turtle_R/pose', lambda msg: self.pose_callback("turtle_R", msg), 10)
        self.create_subscription(Pose, '/turtle_O/pose', lambda msg: self.pose_callback("turtle_O", msg), 10)
        self.create_subscription(Pose, '/turtle_S/pose', lambda msg: self.pose_callback("turtle_S", msg), 10)

        self.kp_linear = 1.0
        self.kp_angular = 7.0

    def pose_callback(self, name, msg):
        self.poses[name] = msg

    def pid_move_to(self, pub, turtle_name, target_x, target_y, tolerance=0.1):
        while rclpy.ok() and self.poses[turtle_name] is None:
            self.get_logger().info(f'Waiting for {turtle_name} pose signal...')
            rclpy.spin_once(self, timeout_sec=0.1)

        msg = Twist()
        while rclpy.ok():
            rclpy.spin_once(self, timeout_sec=0.01)
            curr = self.poses[turtle_name]
            
            dist_error = math.sqrt((target_x - curr.x)**2 + (target_y - curr.y)**2)
            
            if dist_error < tolerance:
                break
            
            desired_angle = math.atan2(target_y - curr.y, target_x - curr.x)
            angle_error = desired_angle - curr.theta
            while angle_error > math.pi: angle_error -= 2.0 * math.pi
            while angle_error < -math.pi: angle_error += 2.0 * math.pi

            if abs(angle_error) > 0.2: 
                msg.linear.x = 0.0
                msg.angular.z = self.kp_angular * angle_error
            else:
                msg.linear.x = self.kp_linear * dist_error
                msg.angular.z = self.kp_angular * angle_error
            
            pub.publish(msg)

        pub.publish(Twist())

    def run(self):
        self.execute_R_trajectory()
        self.execute_O_trajectory()
        self.execute_S_trajectory()

    def execute_R_trajectory(self):
        self.get_logger().info("Drawing R...")
        r_path = [(1.0, 7.0), (3.0, 7.0), (3.0, 5.0), (1.0, 5.0), (3.0, 3.0)]  
        for x, y in r_path: 
            self.pid_move_to(self.pub_R, "turtle_R", x, y)

    def execute_O_trajectory(self):
        self.get_logger().info("Drawing O...")
        cx, cy, r = 5.5, 5.0, 1.5
        for angle in range(0, 370, 10):
            tx = cx + r * math.cos(math.radians(angle))
            ty = cy + r * math.sin(math.radians(angle))
            self.pid_move_to(self.pub_O, "turtle_O", tx, ty)

    def execute_S_trajectory(self):
        self.get_logger().info("Drawing S...")
        s_path = [(10.0, 3.5), (10.0, 5.5), (8.0, 5.5), (8.0, 7.5), (10.0, 7.5)]
        for x, y in s_path: 
            self.pid_move_to(self.pub_S, "turtle_S", x, y)

    def kill_default_turtle(self):
        client = self.create_client(Kill, '/kill')
        while not client.wait_for_service(timeout_sec=1.0): pass
        req = Kill.Request()
        req.name = "turtle1"
        client.call_async(req)
        time.sleep(0.5)

    def spawn_turtle(self, name, x, y):
        client = self.create_client(Spawn, '/spawn')
        while not client.wait_for_service(timeout_sec=1.0): pass
        req = Spawn.Request()
        req.name, req.x, req.y, req.theta = name, x, y, 0.0
        client.call_async(req)
        time.sleep(0.5)

    def set_turtle_color(self, name, r, g, b):
        client = self.create_client(SetPen, f"/{name}/set_pen")
        while not client.wait_for_service(timeout_sec=1.0): pass
        req = SetPen.Request()
        req.r, req.g, req.b, req.width, req.off = r, g, b, 4, 0
        client.call_async(req)

def main(args=None):
    rclpy.init(args=args)
    node = ShapeTrajectoryPID()
    try:
        node.run()
    except KeyboardInterrupt:
        node.get_logger().info("Program interrupted by user")
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
