#!/bin/bash
# HROS 自动持续提升脚本

LOG_DIR=ros_logs
mkdir -p $LOG_DIR

echo "========================================"
echo "🚀 HROS 自动持续提升 - 启动"
echo "========================================"
echo "时间：$(date)"
echo ""

# 1. 运行核心循环
echo "📋 步骤 1: 运行核心循环..."
python3 ros_cycle.py >> $LOG_DIR/auto_cycle.log 2>&1
echo "  ✅ 循环完成"

# 2. 运行自学习引擎
echo "🧠 步骤 2: 运行自学习引擎..."
python3 ros_self_learner.py >> $LOG_DIR/auto_learning.log 2>&1
echo "  ✅ 自学习完成"

# 3. 运行评估基准
echo "📊 步骤 3: 运行评估基准..."
python3 ros_eval.py >> $LOG_DIR/auto_eval.log 2>&1
echo "  ✅ 评估完成"

# 4. 运行测试验证
echo "🧪 步骤 4: 运行测试验证..."
python3 ros_test.py >> $LOG_DIR/auto_test.log 2>&1
echo "  ✅ 测试完成"

echo ""
echo "========================================"
echo "✅ HROS 自动提升完成"
echo "========================================"
echo "日志位置：$LOG_DIR/auto_*.log"
echo "报告位置：ros_meta/"
echo ""

# 检查是否有优化机会
if grep -q "学习机会" $LOG_DIR/auto_learning.log; then
    OPPORTUNITIES=$(grep "共发现" $LOG_DIR/auto_learning.log | grep -oP '\d+(?= 个学习机会)')
    echo "💡 发现 $OPPORTUNITIES 个优化机会"
fi

# 检查测试结果
if grep -q "通过" $LOG_DIR/auto_test.log; then
    echo "✅ 测试验证通过"
fi

echo ""
echo "下次运行：60 分钟后"
echo "========================================"
