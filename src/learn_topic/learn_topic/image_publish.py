"""
图像识别并发布
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2

class ImagePublisher(Node):
    def __init__(self, name):
        super().__init__(name)                                                  # Ros2父节点初始化
        self.publisher_ = self.create_publisher(Image, "raw_image", 10)         # 创建发布者对象
        self.timer = self.create_timer(0.1, self.timer_callback)                # 创建定时任务
        self.cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
        
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
        self.cap.set(cv2.CAP_PROP_FPS, 30)

        # 检查摄像头状态
        if not self.cap.isOpened():
            self.get_logger().error("Failed to open camera")
        else:
            self.get_logger().info("Camera opened successfully")                                          # 捕捉画面
        self.cv_bridge = CvBridge()                                             # 图像转化，OpenCV图像转为ROS的图像消息

    def timer_callback(self):
        ret, frame = self.cap.read()

        if not ret:
            self.get_logger().warn("Failed to read camera frame")
            return

        self.publisher_.publish(
            self.cv_bridge.cv2_to_imgmsg(frame, 'bgr8')
        )

        self.get_logger().info("Publishing video frame")                  #输出日志信息


def main(args=None):                                                            # ROS2节点主入口main函数
    rclpy.init(args=args)                                                       # ROS2 Python接口初始化
    node = ImagePublisher("topic_image_pub")                                    # 创建ROS2节点并初始化
    rclpy.spin(node)                                                            # 循环等待ROS2退出
    node.destroy_node()                                                         # 销毁节点对象
    rclpy.shutdown()                                                            # 关闭Ros2 Python接口