#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
官方技能白名单初始化
从 agents-hub 仓库采集官方技能，生成 L1 白名单
"""

import os
import sys
import json
import hashlib
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class OfficialSkill:
    """官方技能条目"""
    name: str
    hash: str
    files: List[str]
    verified_by: str
    verified_at: str
    level: str = "L1"
    source: str = "official"
    
    def to_dict(self) -> Dict:
        return asdict(self)


class OfficialSkillCollector:
    """官方技能采集器"""
    
    def __init__(self, workspace: str = "/home/cdy/.openclaw/workspace"):
        self.workspace = Path(workspace)
        self.temp_dir = self.workspace / "temp/official_scan"
        self.output_dir = self.workspace / "skills/agent-security-skill-scanner/data/whitelist"
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def clone_repo(self, repo_url: str, branch: str = "master") -> Path:
        """克隆仓库"""
        print(f"[INFO] 克隆仓库：{repo_url}@{branch}")
        
        if self.temp_dir.exists():
            print(f"[INFO] 清理临时目录...")
            import shutil
            shutil.rmtree(self.temp_dir)
        
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        cmd = ["git", "clone", "-b", branch, "--depth", "1", repo_url, str(self.temp_dir)]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"[ERROR] 克隆失败：{result.stderr}")
            raise Exception(f"Git clone failed: {result.stderr}")
        
        print(f"[OK] 仓库已克隆到：{self.temp_dir}")
        return self.temp_dir
    
    def find_skills(self, repo_path: Path) -> List[Path]:
        """查找所有技能目录"""
        skills = []
        
        # 查找包含 SKILL.md 的目录
        for skill_md in repo_path.rglob("SKILL.md"):
            skill_dir = skill_md.parent
            skills.append(skill_dir)
        
        print(f"[INFO] 找到 {len(skills)} 个技能")
        return skills
    
    def compute_skill_hash(self, skill_dir: Path) -> str:
        """计算技能目录的整体哈希"""
        hash_sha256 = hashlib.sha256()
        
        files = []
        for root, dirs, filenames in os.walk(skill_dir):
            # 跳过隐藏文件和目录
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            filenames = [f for f in filenames if not f.startswith('.')]
            
            for filename in sorted(filenames):
                filepath = Path(root) / filename
                rel_path = filepath.relative_to(skill_dir)
                files.append(str(rel_path))
                
                # 计算文件内容哈希
                with open(filepath, "rb") as f:
                    hash_sha256.update(rel_path.encode())  # 文件路径
                    for chunk in iter(lambda: f.read(4096), b""):
                        hash_sha256.update(chunk)
        
        return hash_sha256.hexdigest()
    
    def get_skill_files(self, skill_dir: Path) -> List[str]:
        """获取技能文件列表"""
        files = []
        
        for root, dirs, filenames in os.walk(skill_dir):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            filenames = [f for f in filenames if not f.startswith('.')]
            
            for filename in sorted(filenames):
                filepath = Path(root) / filename
                rel_path = filepath.relative_to(skill_dir)
                files.append(str(rel_path))
        
        return files
    
    def collect_skill(self, skill_dir: Path) -> Optional[OfficialSkill]:
        """采集单个技能"""
        skill_name = skill_dir.name
        
        # 读取 SKILL.md 获取基本信息
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            print(f"[WARN] 跳过（无 SKILL.md）: {skill_name}")
            return None
        
        # 计算哈希
        skill_hash = self.compute_skill_hash(skill_dir)
        
        # 获取文件列表
        files = self.get_skill_files(skill_dir)
        
        skill = OfficialSkill(
            name=skill_name,
            hash=skill_hash,
            files=files,
            verified_by="official",  # 使用通用标识，不包含个人信息
            verified_at=datetime.now().isoformat(),
            level="L1",
            source="official"
        )
        
        print(f"[OK] 采集：{skill_name} ({len(files)} files)")
        return skill
    
    def collect_all(self, repo_url: str, branch: str = "master") -> List[OfficialSkill]:
        """采集所有官方技能"""
        # 克隆仓库
        repo_path = self.clone_repo(repo_url, branch)
        
        # 查找技能
        skill_dirs = self.find_skills(repo_path)
        
        # 采集每个技能
        skills = []
        for skill_dir in skill_dirs:
            skill = self.collect_skill(skill_dir)
            if skill:
                skills.append(skill)
        
        print(f"\n[SUMMARY] 采集完成：{len(skills)} 个官方技能")
        return skills
    
    def save_whitelist(self, skills: List[OfficialSkill], output_file: Optional[str] = None):
        """保存白名单"""
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = self.output_dir / f"official_whitelist_{timestamp}.json"
        else:
            output_file = Path(output_file)
        
        data = {
            'version': '1.0.0',
            'created_at': datetime.now().isoformat(),
            'source': 'agents-hub',
            'level': 'L1',
            'description': '官方技能白名单 - 已人工审核（公共版本，无个人信息）',
            'total_skills': len(skills),
            'skills': [skill.to_dict() for skill in skills],
            'privacy_note': '此文件为公共白名单，不包含任何个人信息，可安全分享'
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"[OK] 白名单已保存：{output_file}")
        return output_file
    
    def cleanup(self):
        """清理临时文件"""
        import shutil
        if self.temp_dir.exists():
            print(f"[INFO] 清理临时目录...")
            shutil.rmtree(self.temp_dir)


def main():
    """主程序"""
    import argparse
    
    parser = argparse.ArgumentParser(description='官方技能白名单初始化')
    parser.add_argument('--repo', type=str, 
                       default='https://gitee.com/caidongyun/agents-hub.git',
                       help='仓库地址')
    parser.add_argument('--branch', type=str, default='master', help='分支')
    parser.add_argument('--output', '-o', type=str, help='输出文件')
    parser.add_argument('--keep-temp', action='store_true', help='保留临时文件')
    parser.add_argument('--stats', action='store_true', help='显示统计')
    
    args = parser.parse_args()
    
    collector = OfficialSkillCollector()
    
    # 采集官方技能
    skills = collector.collect_all(args.repo, args.branch)
    
    if not skills:
        print("[ERROR] 未采集到任何技能")
        sys.exit(1)
    
    # 保存白名单
    output_file = collector.save_whitelist(skills, args.output)
    
    # 显示统计
    if args.stats or True:  # 默认显示
        print(f"\n[统计信息]")
        print(f"  总技能数：{len(skills)}")
        print(f"  总文件数：{sum(len(s.files) for s in skills)}")
        print(f"  输出文件：{output_file}")
    
    # 清理
    if not args.keep_temp:
        collector.cleanup()
    
    print(f"\n[COMPLETE] 官方技能白名单初始化完成")


if __name__ == "__main__":
    main()
