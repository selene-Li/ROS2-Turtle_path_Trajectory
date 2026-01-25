import rclpy
from rclpy.node import Node
from turtlesim.srv import Spawn, SetPen, Kill
from geometry_msgs.msg import Twist
import sys
import select
import tty
import termios
import signal

ORIG_TERMIOS = termios.tcgetattr(sys.stdin)
CMD_MAP = {
    'w': (2.0, 0.0),
    's': (-2.0, 0.0),
    'a': (0.0, 1.5),
    'd': (0.0, -1.5),
    'q': None
}

def signal_handler(sig, frame):
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, ORIG_TERMIOS)
    print("\nProgram exited, terminal mode restored")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

class TurtleController(Node):
    def __init__(self):
        super().__init__('turtle_controller')
        self.kill_default_turtle()
        self.turtles = {
            "1": {"name": "turtle1", "x": 2.0, "y": 2.0, "color": (255, 0, 0)},
            "2": {"name": "turtle2", "x": 5.5, "y": 2.0, "color": (0, 255, 0)},
            "3": {"name": "turtle3", "x": 9.0, "y": 2.0, "color": (0, 0, 255)}
        }
        self.current_turtle = None
        self.vel_publishers = {}
        self.spawn_all_turtles()
        self.init_vel_publishers()
        self.run_control()

    def kill_default_turtle(self):
        client = self.create_client(Kill, '/kill')
        while not client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('/kill service not available, waiting...')
        req = Kill.Request()
        req.name = "turtle1"
        future = client.call_async(req)
        rclpy.spin_until_future_complete(self, future)
        self.get_logger().info("Default turtle1 deleted")

    def spawn_all_turtles(self):
        for idx, turtle in self.turtles.items():
            client_spawn = self.create_client(Spawn, '/spawn')
            while not client_spawn.wait_for_service(timeout_sec=1.0):
                self.get_logger().info('/spawn service not available, waiting...')
            req_spawn = Spawn.Request()
            req_spawn.x = turtle["x"]
            req_spawn.y = turtle["y"]
            req_spawn.theta = 0.0
            req_spawn.name = turtle["name"]
            future_spawn = client_spawn.call_async(req_spawn)
            rclpy.spin_until_future_complete(self, future_spawn)
            self.get_logger().info(f"Created {turtle['name']} at ({turtle['x']}, {turtle['y']})")

            client_pen = self.create_client(SetPen, f"/{turtle['name']}/set_pen")
            while not client_pen.wait_for_service(timeout_sec=1.0):
                self.get_logger().info(f"/{turtle['name']}/set_pen service not available, waiting...")
            req_pen = SetPen.Request()
            req_pen.r, req_pen.g, req_pen.b = turtle["color"]
            req_pen.width = 3
            req_pen.off = 0
            future_pen = client_pen.call_async(req_pen)
            rclpy.spin_until_future_complete(self, future_pen)
            self.get_logger().info(f"{turtle['name']} color set to RGB{turtle['color']}")

    def init_vel_publishers(self):
        for idx, turtle in self.turtles.items():
            self.vel_publishers[idx] = self.create_publisher(
                Twist, f"/{turtle['name']}/cmd_vel", 10
            )
        self.get_logger().info("All velocity publishers initialized")

    def get_key_no_enter(self):
        key = ''
        try:
            tty.setraw(sys.stdin.fileno())
            rlist, _, _ = select.select([sys.stdin], [], [], 0.01)
            if rlist:
                key = sys.stdin.read(1)
            return key
        finally:
            pass

    def select_turtle(self):
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, ORIG_TERMIOS)
        self.get_logger().info("\nEnter turtle number to control (1/2/3), or 'exit' to quit:")
        turtle_idx = input("> ").strip()
        if turtle_idx == "exit":
            self.get_logger().info("Exiting program...")
            return None
        if turtle_idx not in ["1", "2", "3"]:
            self.get_logger().info("Invalid number! Please enter 1/2/3 or 'exit'")
            return self.select_turtle()
        return turtle_idx

    def control_turtle(self, turtle_idx):
        self.get_logger().info(f"\nControlling {self.turtles[turtle_idx]['name']} now:")
        self.get_logger().info("Key control (no enter needed): w=forward s=backward a=left d=right | q=switch turtle | Ctrl+C=quit")
        while rclpy.ok():
            key = self.get_key_no_enter()
            if not key:
                continue
            if key == 'q':
                twist = Twist()
                twist.linear.x = 0.0
                twist.angular.z = 0.0
                self.vel_publishers[turtle_idx].publish(twist)
                self.get_logger().info(f"\n{self.turtles[turtle_idx]['name']} stopped, ready to switch turtle")
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, ORIG_TERMIOS)
                return
            if key not in CMD_MAP:
                continue
            twist = Twist()
            twist.linear.x, twist.angular.z = CMD_MAP[key]
            self.vel_publishers[turtle_idx].publish(twist)
            cmd_desc = {'w': "forward", 's': "backward", 'a': "left", 'd': "right"}
            self.get_logger().info(f"{self.turtles[turtle_idx]['name']} → {cmd_desc[key]}")

    def run_control(self):
        self.get_logger().info("\n===== Turtle Control Program =====")
        self.get_logger().info("Rule: Enter number with enter, control with keys (no enter)")
        self.get_logger().info("====================================")
        while rclpy.ok():
            turtle_idx = self.select_turtle()
            if turtle_idx is None:
                break
            self.control_turtle(turtle_idx)

def main(args=None):
    rclpy.init(args=args)
    node = TurtleController()
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, ORIG_TERMIOS)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
