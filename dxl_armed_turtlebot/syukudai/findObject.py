#!/usr/bin/env python
# -*- coding: utf-8 -*-
import rospy
from opencv_apps.msg import RotatedRectStamped
from geometry_msgs.msg import Twist


class track_box_to_cmd_vel:
    rect = None  ## メンバ変数として定義
    pub = None

    def __init__(self):
        self.rect = RotatedRectStamped()
        rospy.init_node('client')
        ## コールバック関数を self.cb として，メンバ関数を登録
        rospy.Subscriber('/camshift/track_box', RotatedRectStamped, self.cb)
        self.pub = rospy.Publisher('/cmd_vel', Twist)

    def cb(self, msg):
        ## 画像処理の結果を取得
        area = msg.rect.size.width * msg.rect.size.height
        rospy.loginfo("area = {}, center = ({}, {})".format(
            area, msg.rect.center.x, msg.rect.center.y))
        # if area > 100 * 100:  # 認識結果面積が一定値以上のときは rect に登録
        self.rect = msg # 探索の為にareaによらず rect に登録

    def loop(self):
        rate = rospy.Rate(10)
        while not rospy.is_shutdown():
            cmd_vel = Twist()
            ## 古い rect = 認識結果は利用しない
            rect_arrived = rospy.Time.now() - self.rect.header.stamp
            if rect_arrived.to_sec() < 1.0:  ## 最大 1 秒前の認識結果を利用
                ## 認識結果の領域の中心の x 座標が 320 より小さければ，左回転する
                if self.rect.rect.center.x < 320:
                    cmd_vel.angular.z = 0.1
                else:
                    cmd_vel.angular.z = -0.1

            rospy.loginfo("\t\t\t\t\t\tpublish {}".format(cmd_vel.angular.z))
            self.pub.publish(cmd_vel)
            rate.sleep()


if __name__ == '__main__':
    try:
        obj = track_box_to_cmd_vel()  # track_box_to_cmd_vel オブジェクトを生成
        obj.loop()  # obj.loop() メンバ関数内で無限ループとなる．
    except rospy.ROSInterruptException:
        pass
