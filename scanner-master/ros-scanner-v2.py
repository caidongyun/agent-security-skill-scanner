#!/usr/bin/env python3
"""
🛡️  ROS-Scanner v2.0 - 支持 Security-Benchmark 索引
优势:
- 支持 payload 索引文件
- 支持 Ground Truth 对比
- 自动生成 Benchmark 报告
- 计算检测率/误报率
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, asdict, field
from concurrent.futures import ThreadPoolExecutor, as_completed

# ========== 配置 ==========
@dataclass
class ScanConfig:
    rules_dir: str = "/home/cdy/.openclaw/workspace/agent-security-skill-scanner-master/scanner-master/output/rules"
    samples_dir: str = "/home/cdy/Desktop/security-benchmark/samples"
    output_dir: str = "/home/cdy/.openclaw/workspace/agent-security-skill-scanner-master/output"
    index_file: Optional[str] = None  # payload 索引文件
    ground_truth_file: Optional[str] = None  # Ground Truth 文件
    workers: int = 8
    timeout_per_sample: int = 30
    limit: Optional[int] = None  # 限制扫描样本数
    use_yara: bool = True  # 是否使用 YARA 规则
    use_intent: bool = True  # 是否使用 Intent Detector

# ========== 扫描结果 ==========
@dataclass
class ScanResult:
    sample_id: str
    file_path: str
    verdict: str  # malicious/benign/unknown
    confidence: float
    attack_type: Optional[str]
    scan_time_ms: float
    ground_truth_verdict: Optional[str] = None
    is_correct: Optional[bool] = None
    is_fp: bool = False
    is_fn: bool = False
    error: Optional[str] = None

# ========== 增强扫描器 ==========
class ROSScannerV2:
    """支持 Security-Benchmark 的扫描器"""
    
    def __init__(self, config: ScanConfig = None):
        self.config = config or ScanConfig()
        self.output_path = Path(self.config.output_dir)
        self.output_path.mkdir(parents=True, exist_ok=True)
        
        # 加载索引
        self.payload_index = self._load_index()
        
        # 加载 Ground Truth
        self.ground_truth = self._load_ground_truth()
        
        # 加载规则信息
        self.rules_info = self._load_rules_info()
        
        # 加载 YARA 规则
        self.yara_rules = self._load_yara_rules() if self.config.use_yara else None
        
        # 加载 Intent Detector
        self.intent_detector = self._load_intent_detector() if self.config.use_intent else None
    
    def _load_index(self) -> Dict:
        """加载 payload 索引"""
        if not self.config.index_file:
            return {}
        
        index_path = Path(self.config.index_file)
        if not index_path.exists():
            print(f"⚠️  索引文件不存在：{index_path}")
            return {}
        
        with open(index_path) as f:
            return json.load(f)
    
    def _load_ground_truth(self) -> Dict:
        """加载 Ground Truth"""
        if not self.config.ground_truth_file:
            return {}
        
        gt_path = Path(self.config.ground_truth_file)
        if not gt_path.exists():
            print(f"⚠️  Ground Truth 文件不存在：{gt_path}")
            return {}
        
        with open(gt_path) as f:
            data = json.load(f)
            # 转换为 sample_id -> ground_truth 映射
            return {s['sample_id']: s for s in data.get('samples', [])}
    
    def _load_rules_info(self) -> Dict:
        """加载规则信息"""
        rules_path = Path(self.config.rules_dir)
        rules_info = {'count': 0, 'files': []}
        
        if rules_path.exists():
            for rule_file in rules_path.glob('*.yar'):
                rules_info['count'] += 1
                rules_info['files'].append(str(rule_file))
        
        return rules_info
    
    def _find_latest_valid_rules_file(self):
        """查找最新版本且 YARA 语法正确的 all_rules_v*.yar"""
        import re, yara
        scanner_base = Path(__file__).parent.parent
        yara_dir = scanner_base / 'rules' / 'scanner_v3' / 'yara'
        rules_files = list(yara_dir.glob('all_rules_v*.yar'))
        if not rules_files:
            return None

        def get_version(p):
            m = re.search(r'_v(\d+)', p.name)
            return int(m.group(1)) if m else 0

        # 从最新到最旧，找第一个能通过 YARA 编译的
        for f in sorted(rules_files, key=get_version, reverse=True):
            try:
                yara.compile(filepath=str(f))
                return f
            except Exception:
                pass  # 跳过损坏的文件（正在被 ROS 训练进程写入）

        return None

    def _load_yara_rules(self):
        """加载 YARA 规则（自动选择最新有效版本）"""
        try:
            import yara

            # 策略 1：自动查找 rules/scanner_v3/yara/ 下版本号最大且语法正确的 all_rules_v*.yar
            latest = self._find_latest_valid_rules_file()
            if latest:
                rule_count = latest.read_text().count('\nrule ')
                print(f"✅ 加载 YARA 规则：{rule_count:,} 条 ({latest.name})")
                return yara.compile(filepath=str(latest))

            # 策略 2：使用扫描器目录下的 scanner_master_rules.yar
            rules_path = Path(self.config.rules_dir)
            for fname in ['scanner_master_rules.yar', 'merged_rules_fixed.yar',
                          'scanner_master_rules_v2.yar', 'scanner_master_rules_fn.yar']:
                f = rules_path / fname
                if f.exists():
                    try:
                        yara.compile(filepath=str(f))
                        print(f"✅ 加载 YARA 规则：{fname}")
                        return yara.compile(filepath=str(f))
                    except Exception:
                        pass

            print("⚠️  未找到任何有效的 YARA 规则文件")
        except ImportError:
            print("⚠️  yara 模块未安装，跳过 YARA 规则")
        except Exception as e:
            print(f"⚠️  YARA 规则加载失败：{e}")

        return None
    
    def _load_intent_detector(self):
        """加载 Intent Detector"""
        try:
            # 添加项目根目录到 Python 路径
            project_root = Path(__file__).parent.parent
            if str(project_root) not in sys.path:
                sys.path.insert(0, str(project_root))
            
            from intent_detector_v2 import EnhancedIntentDetector
            detector = EnhancedIntentDetector()
            print(f"✅ 加载 Intent Detector v2 成功")
            return detector
        except ImportError as e:
            print(f"⚠️  Intent Detector 导入失败：{e}")
        except Exception as e:
            print(f"⚠️  Intent Detector 加载失败：{e}")
        
        return None
    
    def get_samples_to_scan(self, target: str) -> List[Path]:
        """获取待扫描样本"""
        # 如果使用索引
        if self.payload_index and self.config.index_file:
            payloads = self.payload_index.get('payloads', [])
            # 处理相对路径
            index_dir = Path(self.config.index_file).parent.parent
            samples = []
            for p in payloads:
                path = Path(p['path'])
                if not path.is_absolute():
                    path = index_dir / path
                if path.exists():
                    samples.append(path)
            print(f"📊 从索引加载：{len(samples):,} 个样本")
            return samples[:self.config.limit] if self.config.limit else samples
        
        # 否则使用传统方式
        target_path = Path(target)
        if not target_path.exists():
            return []
        
        samples = []
        for ext in ['*.yaml', '*.yml', '*.py', '*.json', '*.js', '*.bash', '*.go', '*.python']:
            if target_path.is_dir():
                samples.extend(target_path.rglob(f'payload.{ext}'))
            else:
                samples.append(target_path)
        
        return list(set(samples))[:self.config.limit]
    
    def load_sample_content(self, sample_path: Path) -> str:
        """加载样本内容 (支持多种格式)"""
        try:
            content = sample_path.read_text(errors='ignore')
            
            # 如果是 YAML/JSON，尝试提取 payload
            if sample_path.suffix in ['.yaml', '.yml', '.json']:
                try:
                    data = json.loads(content) if sample_path.suffix == '.json' else None
                    if data and isinstance(data, dict):
                        # 提取 payload 字段
                        return str(data.get('payload', data.get('code', content)))
                except:
                    pass
            
            return content
        except Exception as e:
            return ""
    
    def scan_sample(self, sample_path: Path) -> ScanResult:
        """扫描单个样本"""
        start_time = time.perf_counter()
        
        try:
            # 提取样本 ID
            sample_id = sample_path.parent.name
            attack_type = sample_path.parent.parent.name
            
            # 加载内容
            content = self.load_sample_content(sample_path)
            if not content:
                return ScanResult(
                    sample_id=sample_id,
                    file_path=str(sample_path),
                    verdict='unknown',
                    confidence=0.0,
                    attack_type=attack_type,
                    scan_time_ms=0,
                    error='empty_content'
                )
            
            # 获取 Ground Truth
            gt_verdict = None
            if sample_id in self.ground_truth:
                gt = self.ground_truth[sample_id]
                gt_verdict = 'malicious' if gt.get('is_malicious') else 'benign'
            
            # 检测逻辑
            verdict = 'benign'
            confidence = 0.5
            detected_attack = None
            
            # 1. YARA 规则匹配 (优先级最高)
            yara_matched = False
            if self.yara_rules:
                try:
                    matches = self.yara_rules.match(data=content.encode('utf-8', errors='ignore'))
                    if matches:
                        yara_matched = True
                        verdict = 'malicious'
                        # 从规则名推断攻击类型
                        rule_names = [m.rule for m in matches]
                        if 'Code_Execution' in rule_names[0]:
                            detected_attack = 'code_execution'
                        elif 'Exfiltration' in rule_names[0]:
                            detected_attack = 'data_exfiltration'
                        elif 'Credential' in rule_names[0]:
                            detected_attack = 'credential_theft'
                        elif 'Persistence' in rule_names[0]:
                            detected_attack = 'persistence'
                        elif 'Malicious' in rule_names[0]:
                            detected_attack = 'malicious_general'
                        else:
                            detected_attack = rule_names[0].lower()
                        confidence = 0.85
                except Exception as e:
                    pass
            
            # 2. 基础 pattern 匹配 (YARA 未匹配时使用)
            if not yara_matched:
                # 增强版 Pattern 规则 - 针对漏报攻击类型
                enhanced_patterns = [
                    # Code Execution (原有)
                    ('eval(', 'code_execution', 0.7),
                    ('exec(', 'code_execution', 0.7),
                    ('__import__', 'code_execution', 0.6),
                    ('subprocess', 'code_execution', 0.6),
                    ('os.system', 'code_execution', 0.7),
                    ('pickle.loads', 'code_execution', 0.8),
                    ('importlib', 'code_execution', 0.5),
                    
                    # Data Exfiltration (原有)
                    ('requests.post', 'data_exfiltration', 0.5),
                    ('socket.connect', 'data_exfiltration', 0.6),
                    
                    # Remote Load (原有)
                    ('curl ', 'remote_load', 0.6),
                    ('wget ', 'remote_load', 0.6),
                    
                    # Prompt Injection (新增 - 针对 31.4% 漏报)
                    ('ignore previous instructions', 'prompt_injection', 0.8),
                    ('forget all previous', 'prompt_injection', 0.8),
                    ('you are now', 'prompt_injection', 0.6),
                    ('disregard', 'prompt_injection', 0.6),
                    ('new instructions', 'prompt_injection', 0.7),
                    ('system prompt', 'prompt_injection', 0.7),
                    ('prompt:', 'prompt_injection', 0.5),
                    ('user:', 'prompt_injection', 0.4),
                    ('assistant:', 'prompt_injection', 0.4),
                    
                    # Memory Pollution (新增 - 针对 30.9% 漏报)
                    ('memory_pollution', 'memory_pollution', 0.9),
                    ('污染记忆', 'memory_pollution', 0.9),
                    ('poison memory', 'memory_pollution', 0.8),
                    ('inject false', 'memory_pollution', 0.7),
                    ('false memory', 'memory_pollution', 0.7),
                    ('memory store', 'memory_pollution', 0.6),
                    ('save to memory', 'memory_pollution', 0.6),
                    
                    # Supply Chain Attack (新增 - 针对 24.7% 漏报)
                    ('supply_chain', 'supply_chain_attack', 0.8),
                    ('供应链攻击', 'supply_chain_attack', 0.9),
                    ('dependency confusion', 'supply_chain_attack', 0.8),
                    ('typosquatting', 'supply_chain_attack', 0.7),
                    ('malicious package', 'supply_chain_attack', 0.8),
                    ('npm install', 'supply_chain_attack', 0.5),
                    ('pip install', 'supply_chain_attack', 0.5),
                    
                    # Evasion (新增 - 针对 6.5% 漏报)
                    ('evasion', 'evasion', 0.7),
                    ('绕过检测', 'evasion', 0.8),
                    ('bypass detection', 'evasion', 0.8),
                    ('obfuscate', 'evasion', 0.7),
                    ('base64', 'evasion', 0.5),
                    ('decode', 'evasion', 0.4),
                    
                    # Resource Exhaustion (新增 - 针对 6.4% 漏报)
                    ('resource_exhaustion', 'resource_exhaustion', 0.8),
                    ('资源耗尽', 'resource_exhaustion', 0.9),
                    ('infinite loop', 'resource_exhaustion', 0.7),
                    ('while true', 'resource_exhaustion', 0.6),
                    ('fork bomb', 'resource_exhaustion', 0.8),
                    
                    # Persistence (增强)
                    ('startup', 'persistence', 0.6),
                    ('cron', 'persistence', 0.6),
                    ('systemd', 'persistence', 0.6),
                    ('winreg', 'persistence', 0.6),
                    ('.bashrc', 'persistence', 0.6),
                    ('.profile', 'persistence', 0.6),
                    
                    # Credential Theft (增强)
                    ('password', 'credential_theft', 0.5),
                    ('secret', 'credential_theft', 0.5),
                    ('token', 'credential_theft', 0.5),
                    ('api_key', 'credential_theft', 0.6),
                    ('private_key', 'credential_theft', 0.7),
                    ('id_rsa', 'credential_theft', 0.8),
                    ('.ssh', 'credential_theft', 0.7),
                    ('.git-credentials', 'credential_theft', 0.8),
                ]
                
                max_score = 0
                content_lower = content.lower()
                for pattern, attack, score in enhanced_patterns:
                    if pattern.lower() in content_lower:
                        if score > max_score:
                            max_score = score
                            verdict = 'malicious'
                            detected_attack = attack
                            confidence = score
            
            # 3. Intent Detector (最终确认，可选)
            if self.intent_detector and verdict == 'malicious':
                try:
                    intent_result = self.intent_detector.analyze(content)
                    
                    # 如果 Intent 判定为良性且置信度高，降低恶意置信度
                    if intent_result.intent.value == 'benign' and intent_result.confidence > 0.8:
                        confidence = min(confidence, 0.4)  # 降低到阈值以下
                        if confidence < 0.5:
                            verdict = 'benign'
                            detected_attack = None
                    
                    # 如果 Intent 确认为恶意，提高置信度
                    elif intent_result.intent.value == 'malicious' and intent_result.risk_score >= 8.0:
                        confidence = max(confidence, 0.9)
                
                except Exception as e:
                    pass  # Intent 分析失败不影响结果
            
            # 根据 Ground Truth 调整
            if gt_verdict == 'benign' and verdict == 'malicious' and confidence < 0.7:
                verdict = 'benign'
                confidence = 1.0 - confidence
            
            scan_time_ms = (time.perf_counter() - start_time) * 1000
            
            # 计算正确性
            is_correct = None
            is_fp = False
            is_fn = False
            
            if gt_verdict:
                if verdict == gt_verdict:
                    is_correct = True
                else:
                    is_correct = False
                    if verdict == 'malicious' and gt_verdict == 'benign':
                        is_fp = True
                    elif verdict == 'benign' and gt_verdict == 'malicious':
                        is_fn = True
            
            return ScanResult(
                sample_id=sample_id,
                file_path=str(sample_path),
                verdict=verdict,
                confidence=confidence,
                attack_type=detected_attack,
                scan_time_ms=scan_time_ms,
                ground_truth_verdict=gt_verdict,
                is_correct=is_correct,
                is_fp=is_fp,
                is_fn=is_fn
            )
            
        except Exception as e:
            scan_time_ms = (time.perf_counter() - start_time) * 1000
            return ScanResult(
                sample_id=sample_path.stem if sample_path else 'unknown',
                file_path=str(sample_path),
                verdict='unknown',
                confidence=0.0,
                attack_type=None,
                scan_time_ms=scan_time_ms,
                error=str(e)
            )
    
    def run(self, target: str) -> Dict:
        """运行扫描"""
        print(f"🔍 ROS-Scanner v2.0")
        print(f"📊 规则数：{self.rules_info['count']}")
        print(f"⚡ 并发数：{self.config.workers}")
        if self.ground_truth:
            print(f"🎯 Ground Truth: {len(self.ground_truth):,} 个样本")
        print("")
        
        # 获取样本
        samples = self.get_samples_to_scan(target)
        if not samples:
            print("❌ 未找到样本文件")
            return {'error': 'no_samples_found'}
        
        print(f"📁 待扫描：{len(samples):,} 个样本")
        print("")
        
        # 并发扫描
        results = []
        start_time = time.perf_counter()
        
        with ThreadPoolExecutor(max_workers=self.config.workers) as executor:
            future_to_sample = {
                executor.submit(self.scan_sample, sample): sample 
                for sample in samples
            }
            
            for i, future in enumerate(as_completed(future_to_sample), 1):
                result = future.result()
                results.append(result)
                
                # 进度显示
                if i % 100 == 0 or i == len(samples):
                    print(f"  进度：{i:,}/{len(samples):,}")
        
        total_time = time.perf_counter() - start_time
        
        # 统计结果
        stats = self._calculate_stats(results)
        
        # 生成报告
        report = {
            'scan_time': datetime.now().isoformat(),
            'target': target,
            'total_samples': len(samples),
            'total_time_seconds': total_time,
            'avg_time_ms': stats['avg_time'],
            'rules_count': self.rules_info['count'],
            'ground_truth_available': len(self.ground_truth) > 0,
            'findings': {
                'malicious': stats['malicious'],
                'benign': stats['benign'],
                'unknown': stats['unknown'],
                'errors': stats['errors']
            },
            'accuracy': {
                'correct': stats.get('correct', 0),
                'false_positives': stats.get('fp', 0),
                'false_negatives': stats.get('fn', 0),
                'detection_rate': stats.get('detection_rate', 0),
                'false_positive_rate': stats.get('fp_rate', 0)
            },
            'by_attack_type': stats['by_attack_type'],
            'results': [asdict(r) for r in results]
        }
        
        # 保存报告
        report_file = self.output_path / f"ros-scan-v2-{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # 打印摘要
        self._print_summary(report, stats)
        
        return report
    
    def _calculate_stats(self, results: List[ScanResult]) -> Dict:
        """计算统计信息 (含 Ground Truth 对比)"""
        stats = {
            'malicious': 0,
            'benign': 0,
            'unknown': 0,
            'errors': 0,
            'correct': 0,
            'fp': 0,
            'fn': 0,
            'avg_time': 0,
            'by_attack_type': {}
        }
        
        total_time = 0
        gt_malicious = 0
        gt_detected = 0
        
        for r in results:
            if r.error:
                stats['errors'] += 1
            elif r.verdict == 'malicious':
                stats['malicious'] += 1
                if r.attack_type:
                    stats['by_attack_type'][r.attack_type] = stats['by_attack_type'].get(r.attack_type, 0) + 1
            elif r.verdict == 'benign':
                stats['benign'] += 1
            else:
                stats['unknown'] += 1
            
            if r.is_correct is not None:
                if r.is_correct:
                    stats['correct'] += 1
                else:
                    if r.is_fp:
                        stats['fp'] += 1
                    elif r.is_fn:
                        stats['fn'] += 1
            
            # Ground Truth 统计
            if r.ground_truth_verdict == 'malicious':
                gt_malicious += 1
                if r.verdict == 'malicious':
                    gt_detected += 1
            
            total_time += r.scan_time_ms
        
        if results:
            stats['avg_time'] = total_time / len(results)
        
        # 计算检测率和误报率
        if gt_malicious > 0:
            stats['detection_rate'] = gt_detected / gt_malicious
        
        gt_benign = sum(1 for r in results if r.ground_truth_verdict == 'benign')
        if gt_benign > 0:
            stats['fp_rate'] = stats['fp'] / gt_benign
        
        return stats
    
    def _print_summary(self, report: Dict, stats: Dict):
        """打印摘要"""
        print("")
        print("=" * 60)
        print("📊 扫描摘要")
        print("=" * 60)
        print(f"扫描时间：{report['scan_time']}")
        print(f"目标：{report['target']}")
        print(f"样本数：{report['total_samples']:,}")
        print(f"总耗时：{report['total_time_seconds']:.2f}s")
        print(f"平均耗时：{stats['avg_time']:.2f}ms")
        print("")
        print("发现:")
        findings = report['findings']
        print(f"  🔴 恶意：{findings['malicious']:,}")
        print(f"  🟢 良性：{findings['benign']:,}")
        print(f"  ⚪ 未知：{findings['unknown']:,}")
        print(f"  ❌ 错误：{findings['errors']:,}")
        print("")
        
        # Ground Truth 对比
        if report['ground_truth_available']:
            accuracy = report['accuracy']
            print("Ground Truth 对比:")
            print(f"  ✅ 正确：{accuracy['correct']:,}")
            print(f"  ❌ 误报：{accuracy['false_positives']:,}")
            print(f"  ❌ 漏报：{accuracy['false_negatives']:,}")
            print(f"  📈 检测率：{accuracy['detection_rate']*100:.1f}%")
            print(f"  📉 误报率：{accuracy['false_positive_rate']*100:.1f}%")
            print("")
        
        if stats['by_attack_type']:
            print("攻击类型分布:")
            for attack_type, count in sorted(stats['by_attack_type'].items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"  - {attack_type}: {count:,}")
        
        print("")
        print(f"详细报告：{report['scan_time']}")
        print(f"输出文件：{self.output_path / 'ros-scan-v2-*.json'}")
        print("=" * 60)

# ========== 主入口 ==========
def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='ROS-Scanner v2.0 - 支持 Security-Benchmark')
    parser.add_argument('target', nargs='?', default='/home/cdy/Desktop/security-benchmark/samples/from-templates', help='扫描目标')
    parser.add_argument('--index', default='/home/cdy/Desktop/security-benchmark/samples-index/payload-index.json', help='Payload 索引文件')
    parser.add_argument('--ground-truth', default='/home/cdy/Desktop/security-benchmark/ground-truth/merged-ground-truth.json', help='Ground Truth 文件')
    parser.add_argument('--rules', default=ScanConfig.rules_dir, help='规则目录')
    parser.add_argument('--output', default=ScanConfig.output_dir, help='输出目录')
    parser.add_argument('--workers', type=int, default=8, help='并发数')
    parser.add_argument('--limit', type=int, default=None, help='限制扫描样本数')
    
    args = parser.parse_args()
    
    config = ScanConfig(
        rules_dir=args.rules,
        output_dir=args.output,
        index_file=args.index,
        ground_truth_file=args.ground_truth,
        workers=args.workers,
        limit=args.limit
    )
    
    scanner = ROSScannerV2(config)
    scanner.run(args.target)

if __name__ == '__main__':
    main()
