        return result
    
    # --------------------------------------------------------------------------
    # 规则 7: 进程行为检测
    # --------------------------------------------------------------------------
    def check_process_behavior(self) -> Dict:
        """检测可疑进程行为"""
        result = {
            "rule_id": "EXFIL-007",
            "rule_name": "进程行为检测",
            "risk_level": "MEDIUM",
            "findings": [],
        }
        
        suspicious_processes = [
            "nc", "netcat", "ncat",
            "nc.traditional", "nc.openbsd",
            "curl", "wget",
            "dns2tcp", "dnscat", "iodine",
            "ngrok", "frpc", "frps",
            "stunnel", "socat",
        ]
        
        try:
            import subprocess
            proc = subprocess.run(
                ["ps", "aux"],
                capture_output=True, text=True, timeout=5
            )
            
            for line in proc.stdout.split("\n"):
                for proc_name in suspicious_processes:
                    if proc_name in line.lower():
                        # 过滤掉正常系统进程
                        if "grep" in line:
                            continue
                        
                        result["findings"].append({
                            "type": "可疑进程",
                            "detail": line.strip()[:200],
                            "process": proc_name,
                            "recommendation": "检查进程用途和父进程",
                        })
        except Exception as e:
            result["findings"].append({
                "type": "进程检查失败",
                "detail": str(e),
            })
                
        return result
    
    # --------------------------------------------------------------------------
    # 规则 8: 文件时间线分析
    # --------------------------------------------------------------------------
    def check_file_timeline(self, target_path: str) -> Dict:
        """分析文件时间线异常"""
        result = {
            "rule_id": "EXFIL-008",
            "rule_name": "文件时间线异常检测",
            "risk_level": "LOW",
            "findings": [],
        }
        
        target = Path(target_path)
        
        # 检查最近修改的可疑文件
        suspicious_exts = [".py", ".sh", ".pth", ".so", ".dll", ".exe"]
        now = datetime.now().timestamp()
        one_day_ago = now - 86400  # 24 小时前
        
        for ext in suspicious_exts:
            for file in target.rglob(ext):
                try:
                    mtime = file.stat().st_mtime
                    if mtime > one_day_ago:
                        # 24 小时内修改的文件
                        content = file.read_text(encoding="utf-8", errors="ignore")
                        
                        # 检查是否包含外传特征
                        has_c2 = any(d in content for d in KNOWN_C2_DOMAINS)
                        has_exfil = any(re.search(p, content) for p, _ in EXFILTRATION_COMMANDS)
                        
                        if has_c2 or has_exfil:
                            result["findings"].append({
                                "file": str(file),
                                "modified": datetime.fromtimestamp(mtime).isoformat(),
                                "has_c2_domain": has_c2,
                                "has_exfil_command": has_exfil,
                                "recommendation": "重点审查最近修改的文件",
                            })
                except:
                    pass
                
        return result
    
    # --------------------------------------------------------------------------
    # 主检测入口
    # --------------------------------------------------------------------------
    def scan(self, target_path: str) -> Dict:
        """执行完整扫描"""
        print(f"🔍 开始异常外发数据检测...")
        print(f"   目标：{target_path}")
        print()
        
        all_results = []
        total_risk = 0
        
        # 执行所有检测
        detectors = [
            ("C2 域名检测", lambda: self.check_c2_domains(target_path)),
            ("敏感数据检测", lambda: self.check_sensitive_data(target_path)),
            ("外传命令检测", lambda: self.check_exfil_commands(target_path)),
            ("加密隧道检测", lambda: self.check_encrypted_tunnel(target_path)),
            ("DNS 隧道检测", lambda: self.check_dns_tunnel(target_path)),
            ("网络行为检测", self.check_network_behavior),
            ("进程行为检测", self.check_process_behavior),
            ("文件时间线检测", lambda: self.check_file_timeline(target_path)),
        ]
        
        for name, detector in detectors:
            try:
                result = detector()
                all_results.append(result)
                
                # 计算风险评分
                finding_count = len(result.get("findings", []))
                if finding_count > 0:
                    risk_map = {
                        "CRITICAL": 40,
                        "HIGH": 25,
                        "MEDIUM": 10,
                        "LOW": 5,
                    }
                    total_risk += risk_map.get(result["risk_level"], 0) * finding_count
                    
                # 打印简要结果
                status = "⚠️ 发现风险" if finding_count > 0 else "✅ 未检出"
                print(f"   [{status}] {name}: {finding_count} 个发现")
                
            except Exception as e:
                print(f"   [❌ 错误] {name}: {str(e)}")
        
        print()
        
        # 总体评估
        if total_risk >= 80:
            verdict = "🔴 CRITICAL - 立即处置!"
        elif total_risk >= 40:
            verdict = "🟠 HIGH - 尽快处置"
        elif total_risk >= 20:
            verdict = "🟡 MEDIUM - 建议处置"
        else:
            verdict = "🟢 SAFE - 未发现风险"
        
        return {
            "scan_target": target_path,
            "scan_time": datetime.now().isoformat(),
            "detector": "Data-Exfiltration-Detector",
            "version": "1.0.0",
            "total_risk_score": min(total_risk, 100),
            "verdict": verdict,
            "results": all_results,
        }


# ============================================================================
# CLI 入口
# ============================================================================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("用法：python exfil_detector.py <目标路径>")
        print("示例：python exfil_detector.py /path/to/project")
        print("      python exfil_detector.py ~/.openclaw/workspace/")
        sys.exit(1)
    
    target = sys.argv[1]
    detector = ExfiltrationDetector()
    result = detector.scan(target)
    
    # 输出详细报告
    print("=" * 70)
    print("异常外发数据检测报告")
    print("=" * 70)
    print(f"扫描目标：{result['scan_target']}")
    print(f"扫描时间：{result['scan_time']}")
    print(f"风险评分：{result['total_risk_score']}/100")
    print(f"总体判定：{result['verdict']}")
    print()
    
    # 输出详细发现
    for res in result["results"]:
        findings = res.get("findings", [])
        if findings:
            print(f"\n{res['rule_id']}: {res['rule_name']}")
            print(f"风险等级：{res['risk_level']}")
            print(f"发现数量：{len(findings)}")
            for f in findings[:5]:  # 只显示前 5 个
                print(f"  - 文件：{f.get('file', 'N/A')}")
                print(f"    详情：{f.get('context', f.get('command', f.get('detail', 'N/A')))}")
                print(f"    建议：{f.get('recommendation', 'N/A')}")
            if len(findings) > 5:
                print(f"  ... 还有 {len(findings) - 5} 个发现")
    
    # 保存报告
    report_file = f"exfil_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, "w") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"\n📄 完整报告已保存：{report_file}")
