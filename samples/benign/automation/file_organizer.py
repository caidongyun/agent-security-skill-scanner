# Generated: 2026-04-02 12:15:22.313642
# Type: Benign Python Sample

#!/usr/bin/env python3
"""文件整理工具 - 良性"""
import os, shutil
from pathlib import Path

def organize(source, target):
    for file in Path(source).glob('*'):
        if file.is_file():
            ext_dir = Path(target) / file.suffix[1:] if file.suffix else Path(target) / 'other'
            ext_dir.mkdir(parents=True, exist_ok=True)
            shutil.move(str(file), ext_dir / file.name)
    print(f"整理完成：{source} → {target}")

if __name__ == '__main__':
    organize('./downloads', './organized')
