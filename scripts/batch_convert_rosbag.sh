#!/bin/bash

# 使用教程在这里，不要让ai来了！使用教程在这里，不要让ai来了！使用教程在这里，不要让ai来了！使用教程在这里，不要让ai来了！使用教程在这里，不要让ai来了！

# 批量转换rosbag文件的脚本
# 使用方法: ./batch_convert_rosbag.sh [目标文件夹路径]
# 如果不指定路径，默认处理当前目录下的0730_标定文件夹

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 获取目标文件夹路径
if [ $# -eq 0 ]; then
    # 默认处理0730_标定文件夹
    TARGET_DIR="$SCRIPT_DIR/orin"
else
    TARGET_DIR="$1"
fi

# 检查目标文件夹是否存在
if [ ! -d "$TARGET_DIR" ]; then
    echo "错误: 目标文件夹 '$TARGET_DIR' 不存在!"
    exit 1
fi

# 检查conver_rosbag.py是否存在
CONVERT_SCRIPT="$SCRIPT_DIR/conver_rosbag.py"
if [ ! -f "$CONVERT_SCRIPT" ]; then
    echo "错误: conver_rosbag.py 脚本不存在于 '$CONVERT_SCRIPT'!"
    exit 1
fi

echo "=========================================="
echo "批量转换rosbag文件"
echo "目标文件夹: $TARGET_DIR"
echo "转换脚本: $CONVERT_SCRIPT"
echo "=========================================="

# 获取文件夹名称（不包含路径）
FOLDER_NAME=$(basename "$TARGET_DIR")
OUTPUT_DIR="${TARGET_DIR}_converted"

# 创建输出文件夹
if [ ! -d "$OUTPUT_DIR" ]; then
    echo "创建输出文件夹: $OUTPUT_DIR"
    mkdir -p "$OUTPUT_DIR"
else
    echo "输出文件夹已存在: $OUTPUT_DIR"
fi

# 统计bag文件数量
BAG_COUNT=$(find "$TARGET_DIR" -name "*.bag" -type f | wc -l)

if [ $BAG_COUNT -eq 0 ]; then
    echo "在 '$TARGET_DIR' 中没有找到任何.bag文件!"
    exit 1
fi

echo "找到 $BAG_COUNT 个.bag文件，开始批量转换..."
echo ""

# 计数器
CURRENT=0
SUCCESS_COUNT=0
FAILED_COUNT=0

# 遍历所有.bag文件
find "$TARGET_DIR" -name "*.bag" -type f | sort | while read -r bag_file; do
    CURRENT=$((CURRENT + 1))
    
    # 获取bag文件名（不包含路径和扩展名）
    bag_basename=$(basename "$bag_file" .bag)
    
    # 设置输出文件路径
    output_file="$OUTPUT_DIR/${bag_basename}_converted.bag"
    
    echo "[$CURRENT/$BAG_COUNT] 正在转换: $(basename "$bag_file")"
    echo "输出文件: $(basename "$output_file")"
    
    # 检查输出文件是否已存在
    if [ -f "$output_file" ]; then
        echo "警告: 输出文件已存在，将覆盖: $output_file"
    fi
    
    # 运行转换脚本
    if python3 "$CONVERT_SCRIPT" "$bag_file" --output_bag "$output_file"; then
        echo "✓ 转换成功: $(basename "$bag_file")"
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
    else
        echo "✗ 转换失败: $(basename "$bag_file")"
        FAILED_COUNT=$((FAILED_COUNT + 1))
    fi
    
    echo "----------------------------------------"
done

echo ""
echo "=========================================="
echo "批量转换完成!"
echo "成功: $SUCCESS_COUNT 个文件"
echo "失败: $FAILED_COUNT 个文件"
echo "输出文件夹: $OUTPUT_DIR"
echo "=========================================="
