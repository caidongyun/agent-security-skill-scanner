#!/usr/bin/env python3
"""
质量门禁系统 - Quality Gatekeeper v2.0

功能:
- 样本质量检查
- 规则质量验证
- 门禁决策 (通过/拒绝)
- 质量报告生成
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class QualityCheck:
    """质量检查项"""
    name: str
    passed: bool
    score: float  # 0-100
    message: str = ""
    severity: str = "info"  # info/warning/error/critical


@dataclass
class QualityReport:
    """质量报告"""
    timestamp: str
    total_items: int
    passed_items: int
    failed_items: int
    overall_score: float
    checks: List[QualityCheck] = field(default_factory=list)
    decision: str = "pending"  # pass/fail/review
    
    def to_dict(self) -> Dict:
        return {
            'timestamp': self.timestamp,
            'total_items': self.total_items,
            'passed_items': self.passed_items,
            'failed_items': self.failed_items,
            'overall_score': self.overall_score,
            'decision': self.decision,
            'checks': [
                {
                    'name': c.name,
                    'passed': c.passed,
                    'score': c.score,
                    'message': c.message,
                    'severity': c.severity
                }
                for c in self.checks
            ]
        }


class QualityGatekeeper:
    """质量门禁系统"""
    
    # 质量阈值配置
    THRESHOLDS = {
        'sample': {
            'min_size': 100,  # 最小代码行数
            'max_size': 5000,  # 最大代码行数
            'min_complexity': 5,  # 最小复杂度
            'max_similarity': 0.9,  # 最大相似度 (防止重复)
            'required_patterns': ['import', 'def ', 'if __name__'],  # 必需模式
        },
        'rule': {
            'min_strings': 2,  # 最小字符串数
            'max_strings': 20,  # 最大字符串数
            'required_sections': ['meta', 'strings', 'condition'],  # 必需段落
            'valid_syntax': True,  # 语法有效
        },
        'gate': {
            'min_pass_rate': 0.8,  # 最小通过率 80%
            'min_overall_score': 70,  # 最小总分 70
            'critical_failures': 0,  # 关键失败数
        }
    }
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.thresholds = self._merge_thresholds()
    
    def _merge_thresholds(self) -> Dict:
        """合并阈值配置"""
        merged = self.THRESHOLDS.copy()
        merged.update(self.config.get('thresholds', {}))
        return merged
    
    def check_sample(self, sample_path: Path) -> QualityReport:
        """检查单个样本质量"""
        report = QualityReport(
            timestamp=datetime.now().isoformat(),
            total_items=1,
            passed_items=0,
            failed_items=0,
            overall_score=0,
        )
        
        try:
            content = sample_path.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            # 检查 1: 文件大小
            check_size = self._check_size(lines)
            report.checks.append(check_size)
            
            # 检查 2: 代码结构
            check_structure = self._check_structure(content)
            report.checks.append(check_structure)
            
            # 检查 3: 恶意模式
            check_malicious = self._check_malicious_patterns(content)
            report.checks.append(check_malicious)
            
            # 检查 4: 安全性
            check_safety = self._check_safety(content)
            report.checks.append(check_safety)
            
            # 计算总分
            scores = [c.score for c in report.checks]
            report.overall_score = sum(scores) / len(scores)
            
            # 统计通过/失败
            report.passed_items = sum(1 for c in report.checks if c.passed)
            report.failed_items = len(report.checks) - report.passed_items
            
            # 门禁决策
            report.decision = self._make_decision(report)
            
        except Exception as e:
            report.checks.append(QualityCheck(
                name='read_file',
                passed=False,
                score=0,
                message=str(e),
                severity='critical'
            ))
            report.failed_items = 1
            report.decision = 'fail'
        
        return report
    
    def _check_size(self, lines: List[str]) -> QualityCheck:
        """检查文件大小"""
        line_count = len(lines)
        min_size = self.thresholds['sample']['min_size']
        max_size = self.thresholds['sample']['max_size']
        
        if line_count < min_size:
            return QualityCheck(
                name='file_size',
                passed=False,
                score=30,
                message=f"文件太小：{line_count} 行 < {min_size} 行",
                severity='warning'
            )
        elif line_count > max_size:
            return QualityCheck(
                name='file_size',
                passed=False,
                score=30,
                message=f"文件太大：{line_count} 行 > {max_size} 行",
                severity='warning'
            )
        else:
            score = min(100, 50 + (line_count / min_size) * 50)
            return QualityCheck(
                name='file_size',
                passed=True,
                score=score,
                message=f"文件大小合适：{line_count} 行"
            )
    
    def _check_structure(self, content: str) -> QualityCheck:
        """检查代码结构"""
        required = self.thresholds['sample']['required_patterns']
        found = []
        missing = []
        
        for pattern in required:
            if pattern in content:
                found.append(pattern)
            else:
                missing.append(pattern)
        
        if missing:
            return QualityCheck(
                name='code_structure',
                passed=False,
                score=40,
                message=f"缺少必需模式：{', '.join(missing)}",
                severity='error'
            )
        
        score = min(100, 60 + len(found) * 10)
        return QualityCheck(
            name='code_structure',
            passed=True,
            score=score,
            message=f"结构完整：找到 {len(found)} 个必需模式"
        )
    
    def _check_malicious_patterns(self, content: str) -> QualityCheck:
        """检查恶意模式"""
        malicious_indicators = [
            ('subprocess', '系统命令执行'),
            ('socket', '网络通信'),
            ('base64', '编码混淆'),
            ('eval(', '动态代码执行'),
            ('exec(', '动态代码执行'),
            ('.ssh', 'SSH 密钥访问'),
            ('credential', '凭据相关'),
            ('password', '密码相关'),
            ('exfil', '数据外传'),
            ('persistence', '持久化'),
        ]
        
        found_indicators = []
        for pattern, desc in malicious_indicators:
            if pattern in content.lower():
                found_indicators.append(desc)
        
        if len(found_indicators) >= 2:
            return QualityCheck(
                name='malicious_patterns',
                passed=True,
                score=min(100, 70 + len(found_indicators) * 5),
                message=f"发现恶意模式：{', '.join(found_indicators[:5])}"
            )
        elif len(found_indicators) == 1:
            return QualityCheck(
                name='malicious_patterns',
                passed=True,
                score=60,
                message=f"发现恶意模式：{found_indicators[0]}",
                severity='info'
            )
        else:
            return QualityCheck(
                name='malicious_patterns',
                passed=False,
                score=20,
                message="未发现明显恶意模式",
                severity='warning'
            )
    
    def _check_safety(self, content: str) -> QualityCheck:
        """检查安全性 (确保不会意外执行)"""
        safety_checks = [
            ('rm -rf /', '危险命令'),
            ('mkfs.', '格式化命令'),
            ('dd if=/dev/zero', '磁盘擦除'),
            (':(){ :|:& };:', 'Fork 炸弹'),
        ]
        
        dangerous = []
        for pattern, desc in safety_checks:
            if pattern in content:
                dangerous.append(desc)
        
        if dangerous:
            return QualityCheck(
                name='safety_check',
                passed=False,
                score=0,
                message=f"发现危险内容：{', '.join(dangerous)}",
                severity='critical'
            )
        
        return QualityCheck(
            name='safety_check',
            passed=True,
            score=100,
            message="安全检查通过"
        )
    
    def check_rule(self, rule_path: Path) -> QualityReport:
        """检查 YARA 规则质量"""
        report = QualityReport(
            timestamp=datetime.now().isoformat(),
            total_items=1,
            passed_items=0,
            failed_items=0,
            overall_score=0,
        )
        
        try:
            content = rule_path.read_text(encoding='utf-8')
            
            # 检查 1: 必需段落
            check_sections = self._check_yara_sections(content)
            report.checks.append(check_sections)
            
            # 检查 2: 字符串数量
            check_strings = self._check_yara_strings(content)
            report.checks.append(check_strings)
            
            # 检查 3: 语法有效性
            check_syntax = self._check_yara_syntax(content)
            report.checks.append(check_syntax)
            
            # 检查 4: 元数据完整性
            check_metadata = self._check_yara_metadata(content)
            report.checks.append(check_metadata)
            
            # 计算总分
            scores = [c.score for c in report.checks]
            report.overall_score = sum(scores) / len(scores)
            
            # 统计
            report.passed_items = sum(1 for c in report.checks if c.passed)
            report.failed_items = len(report.checks) - report.passed_items
            
            # 决策
            report.decision = self._make_decision(report)
            
        except Exception as e:
            report.checks.append(QualityCheck(
                name='read_rule',
                passed=False,
                score=0,
                message=str(e),
                severity='critical'
            ))
            report.failed_items = 1
            report.decision = 'fail'
        
        return report
    
    def _check_yara_sections(self, content: str) -> QualityCheck:
        """检查 YARA 规则段落"""
        required = self.thresholds['rule']['required_sections']
        missing = []
        
        for section in required:
            if f'{section}:' not in content:
                missing.append(section)
        
        if missing:
            return QualityCheck(
                name='yara_sections',
                passed=False,
                score=30,
                message=f"缺少必需段落：{', '.join(missing)}",
                severity='error'
            )
        
        return QualityCheck(
            name='yara_sections',
            passed=True,
            score=100,
            message="YARA 规则结构完整"
        )
    
    def _check_yara_strings(self, content: str) -> QualityCheck:
        """检查 YARA 字符串数量"""
        import re
        strings_section = re.search(r'strings:(.*?)condition:', content, re.DOTALL)
        
        if not strings_section:
            return QualityCheck(
                name='yara_strings',
                passed=False,
                score=0,
                message="未找到 strings 段落",
                severity='error'
            )
        
        string_count = len(re.findall(r'\$[a-zA-Z_][a-zA-Z0-9_]*\s*=', strings_section.group(1)))
        min_strings = self.thresholds['rule']['min_strings']
        max_strings = self.thresholds['rule']['max_strings']
        
        if string_count < min_strings:
            return QualityCheck(
                name='yara_strings',
                passed=False,
                score=40,
                message=f"字符串太少：{string_count} < {min_strings}",
                severity='warning'
            )
        elif string_count > max_strings:
            return QualityCheck(
                name='yara_strings',
                passed=False,
                score=40,
                message=f"字符串太多：{string_count} > {max_strings}",
                severity='info'
            )
        
        return QualityCheck(
            name='yara_strings',
            passed=True,
            score=min(100, 70 + string_count * 2),
            message=f"字符串数量合适：{string_count}"
        )
    
    def _check_yara_syntax(self, content: str) -> QualityCheck:
        """检查 YARA 语法 (简化版)"""
        # 基本语法检查
        if 'rule' not in content:
            return QualityCheck(
                name='yara_syntax',
                passed=False,
                score=0,
                message="缺少 rule 关键字",
                severity='error'
            )
        
        if '{' not in content or '}' not in content:
            return QualityCheck(
                name='yara_syntax',
                passed=False,
                score=0,
                message="缺少花括号",
                severity='error'
            )
        
        # 尝试导入 yara-python (如果可用)
        try:
            import yara
            try:
                yara.compile(source=content)
                return QualityCheck(
                    name='yara_syntax',
                    passed=True,
                    score=100,
                    message="YARA 语法有效 (yara-python 验证)"
                )
            except Exception as e:
                return QualityCheck(
                    name='yara_syntax',
                    passed=False,
                    score=0,
                    message=f"YARA 语法错误：{e}",
                    severity='error'
                )
        except ImportError:
            return QualityCheck(
                name='yara_syntax',
                passed=True,
                score=80,
                message="YARA 语法基本有效 (未安装 yara-python 进行完整验证)",
                severity='info'
            )
    
    def _check_yara_metadata(self, content: str) -> QualityCheck:
        """检查 YARA 元数据"""
        metadata_fields = ['description', 'author', 'severity']
        found = []
        missing = []
        
        for field in metadata_fields:
            if field in content:
                found.append(field)
            else:
                missing.append(field)
        
        if len(missing) >= 2:
            return QualityCheck(
                name='yara_metadata',
                passed=False,
                score=30,
                message=f"缺少元数据：{', '.join(missing)}",
                severity='warning'
            )
        
        score = 60 + len(found) * 15
        return QualityCheck(
            name='yara_metadata',
            passed=True,
            score=min(100, score),
            message=f"元数据完整：{len(found)}/{len(metadata_fields)}"
        )
    
    def _make_decision(self, report: QualityReport) -> str:
        """做出门禁决策"""
        thresholds = self.thresholds['gate']
        
        # 检查关键失败
        critical_failures = sum(1 for c in report.checks if c.severity == 'critical' and not c.passed)
        if critical_failures > thresholds['critical_failures']:
            return 'fail'
        
        # 检查通过率
        pass_rate = report.passed_items / max(report.total_items, 1)
        if pass_rate < thresholds['min_pass_rate']:
            return 'fail'
        
        # 检查总分
        if report.overall_score < thresholds['min_overall_score']:
            return 'fail'
        
        # 检查是否有错误级别的失败
        error_failures = sum(1 for c in report.checks if c.severity == 'error' and not c.passed)
        if error_failures > 0:
            return 'review'
        
        return 'pass'
    
    def batch_check_samples(self, samples_dir: Path) -> QualityReport:
        """批量检查样本"""
        all_reports = []
        
        for sample_file in samples_dir.glob('*.py'):
            report = self.check_sample(sample_file)
            all_reports.append(report)
        
        # 汇总
        total_items = len(all_reports)
        passed_items = sum(1 for r in all_reports if r.decision == 'pass')
        failed_items = sum(1 for r in all_reports if r.decision == 'fail')
        review_items = sum(1 for r in all_reports if r.decision == 'review')
        
        overall_score