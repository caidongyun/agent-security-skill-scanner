 < timedelta(hours=CONFIG["cache_ttl_hours"]):
                return cache_data["items"]
        except:
            pass
        
        return None
    
    def save_cache(self, source_id: str, items: List[dict]):
        """保存缓存"""
        cache_file = self.cache_dir / f"{source_id}.json"
        cache_data = {
            "cached_at": datetime.now().isoformat(),
            "items": items,
        }
        cache_file.write_text(json.dumps(cache_data, indent=2, ensure_ascii=False))
    
    def aggregate_ioc(self, all_items: List[dict]):
        """聚合 IoC 指标"""
        domains = set()
        urls = set()
        ips = set()
        
        for item in all_items:
            ioc = item.get("ioc", {})
            domains.update(ioc.get("domains", []))
            urls.update(ioc.get("urls", []))
            ips.update(ioc.get("ips", []))
            
            # 从文本中提取 IoC
            text = item.get("summary", "") + " " + item.get("description", "")
            extracted = self.extract_ioc_from_text(text)
            domains.update(extracted.get("domains", []))
            urls.update(extracted.get("urls", []))
            ips.update(extracted.get("ips", []))
        
        # 添加到情报库
        self.intel["ioc"]["domains"] = sorted(list(domains))
        self.intel["ioc"]["urls"] = sorted(list(urls))
        self.intel["ioc"]["ips"] = sorted(list(ips))
    
    def fetch_all(self) -> Dict:
        """采集所有情报源"""
        print("=" * 70)
        print("供应链威胁情报采集")
        print("=" * 70)
        print(f"开始时间：{datetime.now().isoformat()}")
        print(f"情报源数量：{len([s for s in INTEL_SOURCES if s.get('enabled', True)])}")
        print()
        
        all_items = []
        
        for source in INTEL_SOURCES:
            print(f"[{source['id']}] {source['name']}")
            
            # 检查缓存
            cached = self.check_cache(source["id"])
            if cached:
                print(f"  ✅ 使用缓存 ({len(cached)} 条)")
                all_items.extend(cached)
                continue
            
            # 采集新数据
            items = self.fetch_source(source)
            if items:
                print(f"  ✅ 采集成功 ({len(items)} 条)")
                all_items.extend(items)
                
                # 保存缓存
                self.save_cache(source["id"], items)
            else:
                print(f"  ❌ 采集失败或无数据")
            
            # 礼貌延迟
            time.sleep(1)
        
        print()
        print("聚合 IoC 指标...")
        self.aggregate_ioc(all_items)
        
        # 更新元数据
        self.intel["metadata"]["sources"] = [s["id"] for s in INTEL_SOURCES if s.get("enabled", True)]
        self.intel["metadata"]["total_items"] = len(all_items)
        self.intel["advisories"] = all_items
        
        # 保存情报文件
        self.save_intel()
        
        print()
        print("=" * 70)
        print(f"采集完成")
        print(f"  情报源：{len(self.intel['metadata']['sources'])}")
        print(f"  告警数：{len(self.intel['advisories'])}")
        print(f"  域名 IoC: {len(self.intel['ioc']['domains'])}")
        print(f"  URL IoC: {len(self.intel['ioc']['urls'])}")
        print(f"  IP IoC: {len(self.intel['ioc']['ips'])}")
        print(f"输出文件：{self.output_dir / 'threat_intel.json'}")
        print("=" * 70)
        
        return self.intel
    
    def save_intel(self):
        """保存情报文件"""
        # 完整情报
        intel_file = self.output_dir / "threat_intel.json"
        intel_file.write_text(json.dumps(self.intel, indent=2, ensure_ascii=False))
        
        # IoC 简化版 (用于快速加载)
        ioc_file = self.output_dir / "ioc.json"
        ioc_data = {
            "generated_at": self.intel["metadata"]["generated_at"],
            "domains": self.intel["ioc"]["domains"],
            "urls": self.intel["ioc"]["urls"],
            "ips": self.intel["ioc"]["ips"],
            "malicious_packages": self.intel["ioc"]["malicious_packages"],
        }
        ioc_file.write_text(json.dumps(ioc_data, indent=2, ensure_ascii=False))
        
        # YAML 格式 (用于 Scanner 集成)
        yaml_file = self.output_dir / "ioc.yaml"
        try:
            import yaml
            yaml_file.write_text(yaml.dump(ioc_data, allow_unicode=True, default_flow_style=False))
        except ImportError:
            print("  ⚠️  PyYAML 未安装，跳过 YAML 输出")
        
        # 生成 README
        readme_file = self.output_dir / "README.md"
        readme_content = f"""# 供应链威胁情报库

> 自动生成 - 最后更新：{self.intel['metadata']['generated_at']}

## 统计

| 指标 | 数量 |
|------|------|
| 情报源 | {len(self.intel['metadata']['sources'])} |
| 告警数 | {len(self.intel['advisories'])} |
| 域名 IoC | {len(self.intel['ioc']['domains'])} |
| URL IoC | {len(self.intel['ioc']['urls'])} |
| IP IoC | {len(self.intel['ioc']['ips'])} |

## 文件说明

- `threat_intel.json` - 完整情报 (告警 + IoC + 攻击模式)
- `ioc.json` - 简化 IoC (快速加载)
- `ioc.yaml` - YAML 格式 (Scanner 集成)

## 情报源

{chr(10).join('- ' + s['name'] for s in INTEL_SOURCES if s.get('enabled', True))}

## 更新频率

每 6 小时自动更新

## 使用方法

```bash
# 手动更新
python3 intel_fetcher.py

# 查看 IoC
cat ioc.json | jq '.domains'

# Scanner 集成
python3 cli.py scan --intel intel/ <target>
```
"""
        readme_file.write_text(readme_content)


# ============================================================================
# CLI 入口
# ============================================================================

if __name__ == "__main__":
    import sys
    
    fetcher = ThreatIntelligenceFetcher()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("用法：python3 intel_fetcher.py [options]")
        print()
        print("选项:")
        print("  --help      显示帮助")
        print("  --force     强制刷新 (忽略缓存)")
        print("  --source    指定情报源 (如：pypi-security)")
        print()
        print("示例:")
        print("  python3 intel_fetcher.py")
        print("  python3 intel_fetcher.py --force")
        print("  python3 intel_fetcher.py --source pypi-security")
        sys.exit(0)
    
    # 强制刷新
    if len(sys.argv) > 1 and sys.argv[1] == "--force":
        print("强制刷新模式 - 忽略缓存")
        # 清空缓存
        for cache_file in fetcher.cache_dir.glob("*.json"):
            cache_file.unlink()
    
    fetcher.fetch_all()
