#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import TwistStamped


class DualServoTwistPublisher(Node):

    def __init__(self):
        super().__init__('dual_servo_twist_publisher')

        self.right_pub = self.create_publisher(
            TwistStamped,
            '/right_servo_node/right_delta_twist_cmds',
            10
        )

        self.left_pub = self.create_publisher(
            TwistStamped,
            '/left_servo_node/left_delta_twist_cmds',
            10
        )

        self.timer = self.create_timer(0.03, self.timer_callback)  # 10 Hz

        self.get_logger().info('Dual Servo Twist Publisher started')

    def timer_callback(self):
        now = self.get_clock().now().to_msg()

        # Right arm
        right_msg = TwistStamped()
        right_msg.header.stamp = now
        right_msg.header.frame_id = 'right_tcp'
        right_msg.twist.linear.x = -0.09
        right_msg.twist.linear.y = -0.02

        # Left arm
        left_msg = TwistStamped()
        left_msg.header.stamp = now
        left_msg.header.frame_id = 'left_tcp'
        left_msg.twist.linear.z = 0.1

        self.right_pub.publish(right_msg)
        #self.left_pub.publish(left_msg)


def main(args=None):
    rclpy.init(args=args)
    node = DualServoTwistPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
