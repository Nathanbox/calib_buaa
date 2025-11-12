#!/usr/bin/env python

import rospy
import rosbag
import numpy as np
from sensor_msgs.msg import PointCloud2, PointField
import sensor_msgs.point_cloud2 as pc2
import std_msgs.msg
import argparse
import os
import time

def convert_custom_msg_to_pointcloud2(custom_msg):
    """
    将 livox_ros_driver/CustomMsg 转换为 sensor_msgs/PointCloud2
    """
    header = custom_msg.header
    
    # 定义 PointCloud2 消息的字段
    fields = [
        PointField(name='x', offset=0, datatype=PointField.FLOAT32, count=1),
        PointField(name='y', offset=4, datatype=PointField.FLOAT32, count=1),
        PointField(name='z', offset=8, datatype=PointField.FLOAT32, count=1),
        PointField(name='intensity', offset=12, datatype=PointField.UINT8, count=1),
        PointField(name='tag', offset=13, datatype=PointField.UINT8, count=1),
        PointField(name='line', offset=14, datatype=PointField.UINT8, count=1),
        # 添加1字节填充以使offset_time在4字节边界上对齐
        PointField(name='offset_time', offset=16, datatype=PointField.UINT32, count=1)
    ]
    
    # 从自定义消息中提取点
    points = []
    
    for point in custom_msg.points:
        # 创建带有所有必需字段的点
        points.append([
            point.x, 
            point.y, 
            point.z, 
            point.reflectivity,  # 在PointCloud2中映射为'intensity'
            point.tag, 
            point.line, 
            point.offset_time
        ])
    
    # 创建PointCloud2消息
    pc2_msg = pc2.create_cloud(header, fields, points)
    
    return pc2_msg

def convert_bag(input_bag_path, output_bag_path):
    """
    转换输入bag文件中的消息到输出bag文件，保留所有原始话题
    """
    print("正在打开输入bag文件...")
    try:
        input_bag = rosbag.Bag(input_bag_path, 'r')
    except Exception as e:
        print(f"打开输入bag文件时出错: {e}")
        return
    
    print("正在创建输出bag文件...")
    try:
        output_bag = rosbag.Bag(output_bag_path, 'w')
    except Exception as e:
        input_bag.close()
        print(f"创建输出bag文件时出错: {e}")
        return
    
    total_messages = input_bag.get_message_count()
    converted_count = 0
    start_time = time.time()
    
    print(f"正在处理 {total_messages} 条消息...")
    
    try:
        for i, (topic, msg, t) in enumerate(input_bag.read_messages()):
            # 每1000条消息或每10秒打印一次进度
            if i % 1000 == 0 or time.time() - start_time > 10:
                print(f"已处理 {i}/{total_messages} 条消息 ({i/total_messages*100:.1f}%)...")
                start_time = time.time()
            
            # 首先将原始消息写入新的bag文件
            output_bag.write(topic, msg, t)
            
            # 如果是/livox/lidar话题，则额外创建一个转换后的消息
            if topic == '/livox/lidar':
                try:
                    # 转换消息
                    new_msg = convert_custom_msg_to_pointcloud2(msg)
                    # 写入新的话题名称
                    output_bag.write('/livox/points', new_msg, t)
                    converted_count += 1
                except Exception as e:
                    print(f"在时间 {t} 转换消息时出错: {e}")
    
    except Exception as e:
        print(f"bag转换过程中出错: {e}")
    
    finally:
        input_bag.close()
        output_bag.close()
    
    print(f"转换完成。已转换 {converted_count} 条消息，同时保留了所有原始话题。")

def main():
    parser = argparse.ArgumentParser(description='将Livox CustomMsg转换为PointCloud2并保留原始话题')
    parser.add_argument('input_bag', help='输入rosbag文件')
    parser.add_argument('--output_bag', help='输出rosbag文件（默认：input_bag_converted.bag）')
    
    args = parser.parse_args()
    
    # 如果没有指定输出bag，则设置默认值
    if args.output_bag is None:
        base_name = os.path.splitext(args.input_bag)[0]
        args.output_bag = base_name + '_converted.bag'
    
    print(f"正在将 {args.input_bag} 转换为 {args.output_bag}（保留所有原始话题）...")
    convert_bag(args.input_bag, args.output_bag)

if __name__ == '__main__':
    main()