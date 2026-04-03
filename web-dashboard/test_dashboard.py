#!/usr/bin/env python3
"""
Web Dashboard 自动化测试套件
测试 Web 服务的功能、性能和稳定性
"""

import requests
import time
import json
from pathlib import Path
from datetime import datetime

BASE_URL = "http://localhost:8080"
REPORT_DIR = Path(__file__).parent / "test_reports"
REPORT_DIR.mkdir(exist_ok=True)

class DashboardTester:
    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url
        self.results = []
    
    def test_status(self):
        """测试 1: 服务状态"""
        try:
            r = requests.get(self.base_url, timeout=5)
            status = "✅ PASS" if r.status_code == 200 else f"❌ FAIL (HTTP {r.status_code})"
            self.results.append(("服务状态", status, f"HTTP {r.status_code}"))
            return r.status_code == 200
        except Exception as e:
            self.results.append(("服务状态", "❌ FAIL", str(e)))
            return False
    
    def test_html_content(self):
        """测试 2: HTML 内容"""
        try:
            r = requests.get(self.base_url, timeout=5)
            html = r.text
            
            checks = [
                ("Scanner V3", "Scanner V3" in html),
                ("Round 15", "Round 15" in html),
                ("Round 16", "Round 16" in html),
                ("Round 17", "Round 17" in html),
                ("Round 18", "Round 18" in html),
                ("353 样本", "353" in html),
                ("100%", "100%" in html),
            ]
            
            for name, passed in checks:
                status = "✅ PASS" if passed else "❌ FAIL"
                self.results.append((f"HTML 内容 - {name}", status, ""))
            
            return all(passed for _, passed in checks)
        except Exception as e:
            self.results.append(("HTML 内容", "❌ FAIL", str(e)))
            return False
    
    def test_response_time(self):
        """测试 3: 响应时间"""
        try:
            times = []
            for _ in range(5):
                start = time.time()
                requests.get(self.base_url, timeout=5)
                times.append(time.time() - start)
            
            avg_time = sum(times) / len(times) * 1000
            p95_time = sorted(times)[int(len(times) * 0.95)] * 1000
            
            status = "✅ PASS" if avg_time < 100 else "⚠️ SLOW"
            self.results.append(("响应时间", status, f"平均 {avg_time:.2f}ms, P95 {p95_time:.2f}ms"))
            return avg_time < 100
        except Exception as e:
            self.results.append(("响应时间", "❌ FAIL", str(e)))
            return False
    
    def test_concurrent(self):
        """测试 4: 并发请求"""
        try:
            import concurrent.futures
            
            def fetch(i):
                r = requests.get(self.base_url, timeout=5)
                return r.status_code
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                results = list(executor.map(fetch, range(10)))
            
            success = all(code == 200 for code in results)
            status = "✅ PASS" if success else "❌ FAIL"
            self.results.append(("并发请求 (10)", status, f"成功 {sum(1 for c in results if c==200)}/10"))
            return success
        except Exception as e:
            self.results.append(("并发请求", "❌ FAIL", str(e)))
            return False
    
    def test_stability(self):
        """测试 5: 稳定性 (10 次连续请求)"""
        try:
            success = 0
            for i in range(10):
                r = requests.get(self.base_url, timeout=5)
                if r.status_code == 200:
                    success += 1
                time.sleep(0.1)
            
            status = "✅ PASS" if success == 10 else f"⚠️ {success}/10"
            self.results.append(("稳定性 (10 次)", status, f"成功 {success}/10"))
            return success == 10
        except Exception as e:
            self.results.append(("稳定性", "❌ FAIL", str(e)))
            return False
    
    def run_all(self):
        """运行所有测试"""
        print("=" * 60)
        print("🧪 Scanner V3 Web Dashboard - 自动化测试")
        print("=" * 60)
        print()
        
        self.test_status()
        self.test_html_content()
        self.test_response_time()
        self.test_concurrent()
        self.test_stability()
        
        # 打印结果
        print(f"{'测试项':<30} {'状态':<15} {'详情'}")
        print("-" * 60)
        for name, status, detail in self.results:
            print(f"{name:<30} {status:<15} {detail}")
        
        # 汇总
        total = len(self.results)
        passed = sum(1 for _, s, _ in self.results if "✅" in s)
        print("-" * 60)
        print(f"总计：{passed}/{total} 通过 ({passed/total*100:.1f}%)")
        print("=" * 60)
        
        # 保存报告
        report = {
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "total": total,
            "passed": passed,
            "rate": f"{passed/total*100:.1f}%",
            "results": [(n, s, d) for n, s, d in self.results]
        }
        
        report_file = REPORT_DIR / f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 报告已保存：{report_file}")
        return passed == total

if __name__ == '__main__':
    tester = DashboardTester()
    success = tester.run_all()
    exit(0 if success else 1)
