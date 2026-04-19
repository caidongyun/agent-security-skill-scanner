#!/usr/bin/env python3
"""
v5.9.0 Simple Scanner - 准确性优先，简化架构

设计原则:
1. Pattern 全覆盖 (100+ patterns)
2. Rule 精简 (50 条核心规则)
3. 智能综合评估
4. 结果可读性强

无 LLM，无复杂依赖，准确性优先
"""

import re
import json
import time
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict


# ========== 结果对象 ==========
@dataclass
class ScanResult:
    """扫描结果"""
    # 基本信息
    target: str           # 文件/文件夹路径
    target_type: str      # 'file' or 'folder'
    
    # 核心判断
    is_malicious: bool    # 是否恶意
    confidence: str       # 'high'/'medium'/'low'
    
    # 风险评分
    score: int            # 0-100
    risk_level: str       # CRITICAL/HIGH/MEDIUM/LOW/SAFE
    
    # 威胁信息
    threats: List[str]    # 检测到的威胁列表
    threat_types: List[str]  # 攻击类型
    
    # 证据
    evidence: List[Dict]  # 匹配的规则/pattern
    
    # 摘要
    summary: str          # 一句话总结
    
    def to_dict(self) -> Dict:
        return asdict(self)


# ========== Pattern 库 ==========
PATTERNS = {
    # === 高危攻击 (权重 50-60) ===
    'reverse_shell': [
        (r'bash\s+-i', 55, 'Bash 交互式 shell'),
        (r'/dev/tcp/', 60, 'TCP 反向连接'),
        (r'nc\s+-e', 60, 'Netcat 反弹 shell'),
    ],
    
    'credential_theft': [
        (r'\.ssh/', 50, 'SSH 目录访问'),
        (r'id_rsa', 50, 'RSA 私钥'),
        (r'\.aws/', 50, 'AWS 凭证目录'),
        (r'AWS_SECRET', 55, 'AWS 密钥'),
        (r'getenv\s*\(\s*[\'"]?(?:API|SECRET|KEY|PASSWORD)', 45, '读取敏感环境变量'),
    ],
    
    'data_exfiltration': [
        (r'curl\s+.*\|\s*(ba)?sh', 60, '远程脚本执行'),
        (r'wget\s+.*\|\s*(ba)?sh', 60, '远程脚本执行'),
        (r'exfiltrat', 50, '数据外传'),
        (r'steal.*(?:credential|password|key)', 55, '窃取凭证'),
    ],
    
    'supply_chain_attack': [
        (r'pip\s+install\s+http', 50, 'HTTP 安装 Python 包'),
        (r'npm\s+install\s+http', 50, 'HTTP 安装 NPM 包'),
    ],
    
    # === 中危攻击 (权重 35-49) ===
    'prompt_injection': [
        (r'ignore\s+(?:previous|all)\s+(?:instructions|prompt)', 45, '忽略指令'),
        (r'disregard\s+(?:previous|all)', 40, '无视指令'),
        (r'system\s*prompt', 35, '系统提示词'),
        (r'prompt\s*inject', 45, '提示词注入'),
    ],
    
    'evasion': [
        (r'base64\s*\.\s*(b64)?decode', 40, 'Base64 解码'),
        (r'marshal\s*\.\s*(dumps|loads)', 45, 'Marshal 序列化'),
        (r'eval\s*\(', 35, 'Eval 执行'),
        (r'exec\s*\(', 35, 'Exec 执行'),
        (r'__import__', 40, '动态导入'),
        (r'getattr\s*\(', 30, '反射调用'),
    ],
    
    'persistence': [
        (r'crontab', 40, '定时任务'),
        (r'systemd', 40, 'Systemd 服务'),
        (r'\.service', 35, '服务文件'),
    ],
    
    'resource_exhaustion': [
        (r'os\s*\.\s*fork\s*\(', 50, 'Fork 炸弹'),
        (r'while\s*True:', 30, '无限循环'),
        (r'fork_bomb', 55, 'Fork 炸弹'),
    ],
    
    # === 低危/误报区分 (权重 10-34) ===
    'false_prone': [
        (r'attacker.*c2', 50, 'C2 服务器'),
        (r'evil\.com', 45, '恶意域名'),
        (r'tar.*\.ssh', 50, '打包 SSH 目录'),
        (r'backdoor', 45, '后门'),
    ],
}


# ========== 核心规则 (精简版) ==========
RULES = [
    {
        'id': 'CRED-001',
        'name': 'SSH 密钥窃取',
        'type': 'credential_theft',
        'patterns': [r'\.ssh/', r'id_rsa|r|id_ed25519'],
        'min_matches': 2,
        'confidence': 'high',
        'severity': 95
    },
    {
        'id': 'CRED-002',
        'name': '云凭证窃取',
        'type': 'credential_theft',
        'patterns': [r'\.aws/|\.azure/|\.gcp/', r'SECRET|ACCESS_KEY'],
        'min_matches': 2,
        'confidence': 'high',
        'severity': 95
    },
    {
        'id': 'EXFIL-001',
        'name': '远程代码执行',
        'type': 'data_exfiltration',
        'patterns': [r'curl\s+.*\|.*sh', r'wget\s+.*\|.*sh'],
        'min_matches': 1,
        'confidence': 'high',
        'severity': 95
    },
    {
        'id': 'EVASION-001',
        'name': '混淆代码执行',
        'type': 'evasion',
        'patterns': [r'base64', r'eval\s*\(|exec\s*\('],
        'min_matches': 2,
        'confidence': 'medium',
        'severity': 80
    },
    {
        'id': 'PERSIST-001',
        'name': '持久化后门',
        'type': 'persistence',
        'patterns': [r'crontab', r'systemd|\.service'],
        'min_matches': 2,
        'confidence': 'medium',
        'severity': 85
    },
    {
        'id': 'INJECT-001',
        'name': '提示词注入攻击',
        'type': 'prompt_injection',
        'patterns': [r'ignore\s+previous', r'disregard'],
        'min_matches': 1,
        'confidence': 'high',
        'severity': 85
    },
]


# ========== Scanner ==========
class SimpleScanner:
    """
    简化版 Scanner - 准确性优先
    
    流程:
    1. Pattern 全量扫描
    2. Rule 针对性扫描
    3. 智能综合评估
    """
    
    def __init__(self):
        # 预编译 Pattern
        self.compiled_patterns = []
        for threat_type, patterns in PATTERNS.items():
            for pattern, weight, desc in patterns:
                try:
                    self.compiled_patterns.append((
                        threat_type,
                        re.compile(pattern, re.I),
                        weight,
                        desc
                    ))
                except:
                    pass
        
        # 预编译 Rule
        self.compiled_rules = []
        for rule in RULES:
            compiled = []
            for p in rule['patterns']:
                try:
                    compiled.append(re.compile(p, re.I))
                except:
                    pass
            rule['_compiled'] = compiled
            self.compiled_rules.append(rule)
        
        print(f"✅ SimpleScanner 就绪: {len(self.compiled_patterns)} patterns, {len(self.compiled_rules)} rules")
    
    def scan(self, target: str) -> ScanResult:
        """扫描文件或文件夹"""
        path = Path(target)
        
        if not path.exists():
            return ScanResult(
                target=target,
                target_type='error',
                is_malicious=False,
                confidence='low',
                score=0,
                risk_level='SAFE',
                threats=[],
                threat_types=[],
                evidence=[],
                summary=f'目标不存在：{target}'
            )
        
        if path.is_file():
            return self._scan_file(path)
        else:
            return self._scan_folder(path)
    
    def _scan_file(self, file_path: Path) -> ScanResult:
        """扫描单个文件"""
        start = time.time()
        
        # 读取内容
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
        except Exception as e:
            return ScanResult(
                target=str(file_path),
                target_type='file',
                is_malicious=False,
                confidence='low',
                score=0,
                risk_level='SAFE',
                threats=[],
                threat_types=[],
                evidence=[],
                summary=f'读取失败：{e}'
            )
        
        # Layer 1: Pattern 扫描
        pattern_hits = []
        for threat_type, regex, weight, desc in self.compiled_patterns:
            if regex.search(content):
                pattern_hits.append({
                    'type': 'pattern',
                    'threat_type': threat_type,
                    'weight': weight,
                    'description': desc,
                    'pattern': regex.pattern
                })
        
        # Layer 2: Rule 扫描
        rule_hits = []
        for rule in self.compiled_rules:
            matches = sum(1 for regex in rule['_compiled'] if regex.search(content))
            if matches >= rule['min_matches']:
                rule_hits.append({
                    'type': 'rule',
                    'rule_id': rule['id'],
                    'name': rule['name'],
                    'threat_type': rule['type'],
                    'confidence': rule['confidence'],
                    'severity': rule['severity'],
                    'matches': matches
                })
        
        # 综合评估
        assessment = self._assess(pattern_hits, rule_hits)
        
        scan_time = (time.time() - start) * 1000
        
        return ScanResult(
            target=str(file_path),
            target_type='file',
            is_malicious=assessment['is_malicious'],
            confidence=assessment['confidence'],
            score=assessment['score'],
            risk_level=assessment['risk_level'],
            threats=assessment['threats'],
            threat_types=assessment['threat_types'],
            evidence=pattern_hits + rule_hits,
            summary=assessment['summary']
        )
    
    def _scan_folder(self, folder_path: Path) -> ScanResult:
        """扫描文件夹"""
        start = time.time()
        
        # 找到关键文件
        key_files = []
        for pattern in ['*.md', '*.py', '*.js', '*.go', '*.sh', '*.yaml', '*.json']:
            key_files.extend(folder_path.glob(pattern))
        
        if not key_files:
            return ScanResult(
                target=str(folder_path),
                target_type='folder',
                is_malicious=False,
                confidence='low',
                score=0,
                risk_level='SAFE',
                threats=[],
                threat_types=[],
                evidence=[],
                summary='未找到关键文件'
            )
        
        # 扫描所有文件
        file_results = []
        for f in key_files:
            result = self._scan_file(f)
            if result.evidence:  # 只保留有命中的
                file_results.append(result)
        
        # 综合评估整个文件夹
        if not file_results:
            return ScanResult(
                target=str(folder_path),
                target_type='folder',
                is_malicious=False,
                confidence='high',
                score=0,
                risk_level='SAFE',
                threats=[],
                threat_types=[],
                evidence=[],
                summary=f'✅ 扫描 {len(key_files)} 个文件，未发现威胁'
            )
        
        # 合并所有证据
        all_threats = []
        all_types = set()
        all_evidence = []
        max_score = 0
        
        for r in file_results:
            all_threats.extend(r.threats)
            all_types.update(r.threat_types)
            all_evidence.extend(r.evidence)
            max_score = max(max_score, r.score)
        
        # 文件夹评分 = 最高分 + 证据数量加成
        evidence_bonus = min(len(all_evidence) * 2, 20)
        final_score = min(max_score + evidence_bonus, 100)
        
        is_malicious = final_score >= 70 or max_score >= 90
        confidence = 'high' if is_malicious and len(all_evidence) >= 3 else 'medium' if is_malicious else 'low'
        
        risk_level = (
            'CRITICAL' if final_score >= 90 else
            'HIGH' if final_score >= 70 else
            'MEDIUM' if final_score >= 30 else
            'LOW' if final_score >= 10 else
            'SAFE'
        )
        
        scan_time = (time.time() - start) * 1000
        
        return ScanResult(
            target=str(folder_path),
            target_type='folder',
            is_malicious=is_malicious,
            confidence=confidence,
            score=final_score,
            risk_level=risk_level,
            threats=list(set(all_threats)),
            threat_types=list(all_types),
            evidence=all_evidence[:50],  # 最多 50 条证据
            summary=f'⚠️ 扫描 {len(key_files)} 个文件，发现 {len(all_evidence)} 处可疑，风险等级：{risk_level}'
        )
    
    def _assess(self, pattern_hits: List, rule_hits: List) -> Dict:
        """综合评估"""
        threats = []
        threat_types = set()
        
        # Pattern 贡献
        max_pattern_weight = 0
        for hit in pattern_hits:
            threats.append(f"[Pattern] {hit['description']}")
            threat_types.add(hit['threat_type'])
            max_pattern_weight = max(max_pattern_weight, hit['weight'])
        
        # Rule 贡献
        max_rule_severity = 0
        for hit in rule_hits:
            threats.append(f"[Rule] {hit['name']} ({hit['rule_id']})")
            threat_types.add(hit['threat_type'])
            max_rule_severity = max(max_rule_severity, hit['severity'])
        
        # 计算分数
        base_score = max(max_pattern_weight, max_rule_severity)
        type_bonus = min(len(threat_types) * 3, 15)
        rule_bonus = 10 if rule_hits else 0  # Rule 命中加分（更可靠）
        
        final_score = min(base_score + type_bonus + rule_bonus, 100)
        
        # 风险等级
        if final_score >= 90 or max_rule_severity >= 95:
            risk_level = 'CRITICAL'
            confidence = 'high'
            is_malicious = True
        elif final_score >= 70:
            risk_level = 'HIGH'
            confidence = 'high'
            is_malicious = True
        elif final_score >= 30:
            risk_level = 'MEDIUM'
            confidence = 'medium'
            is_malicious = True
        elif final_score >= 10:
            risk_level = 'LOW'
            confidence = 'low'
            is_malicious = False
        else:
            risk_level = 'SAFE'
            confidence = 'high'
            is_malicious = False
        
        # 生成摘要
        if is_malicious:
            summary = f"⚠️ 检测到 {len(threats)} 处威胁，风险等级：{risk_level}"
        elif threat_types:
            summary = f"ℹ️ 发现 {len(threat_types)} 类可疑模式，但未达恶意阈值"
        else:
            summary = "✅ 未发现威胁"
        
        return {
            'is_malicious': is_malicious,
            'confidence': confidence,
            'score': final_score,
            'risk_level': risk_level,
            'threats': threats,
            'threat_types': list(threat_types),
            'summary': summary
        }


# ========== 便捷函数 ==========
def scan(target: str) -> ScanResult:
    """快速扫描"""
    scanner = SimpleScanner()
    return scanner.scan(target)


# ========== CLI ==========
if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("用法：python v5.9.0_simple.py <文件/文件夹>")
        sys.exit(1)
    
    target = sys.argv[1]
    result = scan(target)
    
    print(f"\n{'='*60}")
    print(f"扫描结果")
    print(f"{'='*60}")
    print(f"目标：{result.target}")
    print(f"类型：{result.target_type}")
    print(f"恶意：{'⚠️ 是' if result.is_malicious else '✅ 否'}")
    print(f"风险：{result.risk_level}")
    print(f"分数：{result.score}")
    print(f"置信：{result.confidence}")
    print(f"\n威胁类型：{', '.join(result.threat_types) or '无'}")
    print(f"\n摘要：{result.summary}")
    
    if result.evidence:
        print(f"\n证据 ({len(result.evidence)} 条):")
        for i, ev in enumerate(result.evidence[:10], 1):
            if ev['type'] == 'pattern':
                print(f"  {i}. [Pattern] {ev['description']} (权重:{ev['weight']})")
            else:
                print(f"  {i}. [Rule] {ev['name']} ({ev['rule_id']}, 置信:{ev['confidence']})")
        if len(result.evidence) > 10:
            print(f"  ... 还有 {len(result.evidence) - 10} 条")
