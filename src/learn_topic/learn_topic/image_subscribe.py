"""
订阅图像话题
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import numpy as np

lower_orange = np.array([5, 80, 80])
upper_orange = np.array([30, 255, 255])

class ImageSubscriber(Node):
    def __init__(self, name):
        super().__init__(name)
        self.sub = self.create_subscription(Image, 'raw_image', self.listener_callback, 10)
        self.cv_bridge = CvBridge()

    def object_image(self, image):
        # BGR转HSV
        hsv_img = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # 提取橙色区域
        mask_orange = cv2.inRange(
            hsv_img, lower_orange, upper_orange
        )

        # 显示二值化图像，方便调试
        cv2.imshow("mask", mask_orange)

        # 提取轮廓
        contours, hierarchy = cv2.findContours(
            mask_orange,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        for cnt in contours:
            area = cv2.contourArea(cnt)

            if area < 50:
                continue

            x, y, w, h = cv2.boundingRect(cnt)

            # 绘制红色轮廓
            cv2.drawContours(image, [cnt], -1, (0, 0, 255), 2)

            # 绘制绿色中心点
            cv2.circle(
                image,
                (x + w // 2, y + h // 2),
                5, (0, 255, 0), -1
            )

        cv2.imshow("object", image)
        cv2.waitKey(1)

    def listener_callback(self, data):
        self.get_logger().info('Receiving video frame')
        image = self.cv_bridge.imgmsg_to_cv2(data, 'bgr8')
        self.object_image(image)

def main(args=None):
    rclpy.init(args=args)
    node = ImageSubscriber("topic_image_sub")
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()