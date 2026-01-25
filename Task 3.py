import rclpy
from rclpy.node import Node
from turtlesim.srv import Spawn, SetPen, Kill
from geometry_msgs.msg import Twist
import math
import time

class ShapeTrajectory(Node):
    def __init__(self):
        super().__init__('shape_trajectory_node')
        
        self.kill_default_turtle()
        
        self.spawn_turtle("turtle_R", 1.0, 3.0)
        self.set_turtle_color("turtle_R", 255, 0, 0)
        
        self.spawn_turtle("turtle_O", 5.2, 3.8)
        self.set_turtle_color("turtle_O", 0, 255, 0)
        
        self.spawn_turtle("turtle_S", 8.0, 3.5)
        self.set_turtle_color("turtle_S", 0, 0, 255)

        self.pub_R = self.create_publisher(Twist, '/turtle_R/cmd_vel', 10)
        self.pub_O = self.create_publisher(Twist, '/turtle_O/cmd_vel', 10)
        self.pub_S = self.create_publisher(Twist, '/turtle_S/cmd_vel', 10)

        self.execute_R_trajectory()
        self.execute_O_trajectory()
        self.execute_S_trajectory()

    def kill_default_turtle(self):
        client = self.create_client(Kill, '/kill')
        while not client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for /kill service (delete default turtle1)...')
        req = Kill.Request()
        req.name = "turtle1"
        client.call_async(req)
        time.sleep(0.5)

    def spawn_turtle(self, name, x, y):
        client = self.create_client(Spawn, '/spawn')
        while not client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info(f'Waiting for /spawn service (spawn {name})...')
        req = Spawn.Request()
        req.name = name
        req.x = x
        req.y = y
        req.theta = 0.0
        client.call_async(req)
        time.sleep(0.5)

    def set_turtle_color(self, name, r, g, b):
        client = self.create_client(SetPen, f"/{name}/set_pen")
        while not client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info(f'Waiting for /{name}/set_pen service (set color)...')
        req = SetPen.Request()
        req.r = r
        req.g = g
        req.b = b
        req.width = 4
        req.off = 0    
        client.call_async(req)
        time.sleep(0.5)

    def move_turtle(self, pub, linear, angular, duration):
        twist = Twist()
        twist.linear.x = linear
        twist.angular.z = angular
        
        start = time.time()
        while (time.time() - start) < duration:
            pub.publish(twist)
            time.sleep(0.01)
        
        twist.linear.x = 0.0
        twist.angular.z = 0.0
        pub.publish(twist)

    def execute_R_trajectory(self):
        self.get_logger().info("Start drawing R trajectory (red turtle, double width)")
        
        self.move_turtle(self.pub_R, 0.0, 1.5, 1.0)
        
        self.move_turtle(self.pub_R, 0.8, 0.0, 5.0)
        
        self.move_turtle(self.pub_R, 0.0, -1.57, 1.0)
        
        self.move_turtle(self.pub_R, 0.5, 0.0, 2.0)
        
        self.move_turtle(self.pub_R, 0.5, -0.5, 6.28)

        self.move_turtle(self.pub_R, 0.5, 0.0, 2.0)
        
        self.move_turtle(self.pub_R, 0.0, -1.57, 2.5)
        
        self.move_turtle(self.pub_R, 0.5, 0.0, 5.66)

    def execute_O_trajectory(self):
        self.get_logger().info("Start drawing O trajectory (green turtle)")
        self.move_turtle(self.pub_O, 0.5, 0.38, 18.0)

    def execute_S_trajectory(self):
        self.get_logger().info("Start drawing S trajectory (blue turtle)")
        self.move_turtle(self.pub_S, 0.0, -1.57, 0.66)
        
        self.move_turtle(self.pub_S, 0.5, 0.5, 7.7)
        
        self.move_turtle(self.pub_S, 0.85, 0.0, 1.0)
        
        self.move_turtle(self.pub_S, 0.5, -0.5, 7.7)

def main(args=None):
    rclpy.init(args=args)
    node = ShapeTrajectory()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
