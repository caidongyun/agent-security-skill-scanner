# Sample Generator v2.0 - Makefile
# 集成质量门禁的编排工具

.PHONY: all generate check-gate scan rules report clean help

# ==================== 配置 ====================
SAMPLES_DIR := output/samples
RULES_DIR := output/rules
REPORTS_DIR := reports
QUALITY_DIR := quality_gate
THRESHOLD := 70

# ==================== 质量门禁 ====================

# 样本质量检查
check-gate-sample:
	@echo ""
	@echo "🔍 质量门禁：样本检查..."
	python3 -m quality_gate.gatekeeper --mode batch --input $(SAMPLES_DIR)/python/ --output $(REPORTS_DIR)/quality_sample --threshold $(THRESHOLD)
	@echo ""

# 规则质量检查
check-gate-rule:
	@echo ""
	@echo "🔍 质量门禁：规则检查..."
	python3 -m quality_gate.gatekeeper --mode rule --input $(RULES_DIR)/python_all.yar --output $(REPORTS_DIR)/quality_rule --threshold $(THRESHOLD)
	@echo ""

# 完整质量门禁
check-gate: check-gate-sample check-gate-rule
	@echo ""
	@echo "✅ 质量门禁完成"
	@echo ""

# ==================== 样本生成 ====================

# 生成 Python 样本 (50 个)
generate-python:
	@echo "🔨 生成 Python 样本..."
	python3 -m generators.cli --language python --count 50 --output $(SAMPLES_DIR)/python/
	@echo "✅ Python 样本完成"

# 生成 PowerShell 样本 (50 个)
generate-powershell:
	@echo "🔨 生成 PowerShell 样本..."
	python3 -m generators.cli --language powershell --count 50 --output $(SAMPLES_DIR)/powershell/
	@echo "✅ PowerShell 样本完成"

# 生成 JavaScript 样本 (50 个)
generate-javascript:
	@echo "🔨 生成 JavaScript 样本..."
	python3 -m generators.cli --language javascript --count 50 --output $(SAMPLES_DIR)/javascript/
	@echo "✅ JavaScript 样本完成"

# 生成 Bash 样本 (30 个)
generate-bash:
	@echo "🔨 生成 Bash 样本..."
	python3 -m generators.cli --language bash --count 30 --output $(SAMPLES_DIR)/bash/
	@echo "✅ Bash 样本完成"

# 生成所有样本
generate: generate-python
	@echo ""
	@echo "🎉 所有样本生成完成！"
	@echo "📂 位置：$(SAMPLES_DIR)/"
	@find $(SAMPLES_DIR) -name "*.py" -o -name "*.ps1" -o -name "*.js" -o -name "*.sh" | wc -l | xargs -I {} echo "📊 总计：{} 个文件"

# ==================== 扫描 ====================

scan: generate check-gate-sample
	@echo ""
	@echo "🔍 扫描样本..."
	python3 scanner/integration_scanner.py --rules $(RULES_DIR) --samples $(SAMPLES_DIR)/python --output $(REPORTS_DIR)/scan_results
	@echo "✅ 扫描完成"
	@echo "📂 报告位置：$(REPORTS_DIR)/"

# ==================== 规则生成 ====================

rules: generate check-gate-sample
	@echo ""
	@echo "📝 生成检测规则..."
	python3 rules/generator.py --samples $(SAMPLES_DIR)/python --output $(RULES_DIR)/
	@echo "✅ 规则生成完成"
	@echo "📂 规则位置：$(RULES_DIR)/"
	@$(MAKE) check-gate-rule

# ==================== 报告生成 ====================

report: scan
	@echo ""
	@echo "📊 生成综合报告..."
	python3 -m reports.generator --input $(REPORTS_DIR)/scan_results.json --output $(REPORTS_DIR)/final_report.md
	@echo "✅ 报告完成"
	@echo "📂 报告位置：$(REPORTS_DIR)/final_report.md"

# ==================== 完整流程 ====================

all: generate check-gate-sample rules check-gate-rule scan report
	@echo ""
	@echo "🎉🎉🎉 全部完成！"
	@echo ""
	@echo "📊 结果汇总:"
	@echo "   样本：$(SAMPLES_DIR)/"
	@echo "   规则：$(RULES_DIR)/"
	@echo "   报告：$(REPORTS_DIR)/"
	@echo "   质量报告：$(REPORTS_DIR)/quality_*.md"
	@echo ""

# ==================== 清理 ====================

clean:
	@echo "🧹 清理输出目录..."
	rm -rf $(SAMPLES_DIR)/* $(RULES_DIR)/* $(REPORTS_DIR)/*
	@echo "✅ 清理完成"

clean-all: clean
	@echo "🧹 清理 Python 缓存..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	@echo "✅ 完全清理完成"

# ==================== 帮助 ====================

help:
	@echo ""
	@echo "📚 Sample Generator v2.0 - 可用命令"
	@echo ""
	@echo "生成样本:"
	@echo "  make generate         生成所有样本 (默认 Python)"
	@echo "  make generate-python  仅生成 Python 样本"
	@echo "  make generate-powershell  仅生成 PowerShell 样本"
	@echo "  make generate-javascript  仅生成 JavaScript 样本"
	@echo "  make generate-bash    仅生成 Bash 样本"
	@echo ""
	@echo "扫描与规则:"
	@echo "  make scan             扫描样本并生成报告"
	@echo "  make rules            生成检测规则"
	@echo "  make report           生成综合报告"
	@echo ""
	@echo "完整流程:"
	@echo "  make all              完整流程：生成→扫描→规则→报告"
	@echo ""
	@echo "清理:"
	@echo "  make clean            清理输出目录"
	@echo "  make clean-all        清理所有 (包括缓存)"
	@echo ""
	@echo "帮助:"
	@echo "  make help             显示此帮助信息"
	@echo ""
	@echo "📖 文档:"
	@echo "  - PRIORITY_PLAN_2026.md  实施计划"
	@echo "  - SAMPLE_GENERATOR_V2_DESIGN.md  设计文档"
	@echo ""
