# Generated: 2026-04-02 11:55:15.209512
# Type: Benign Python Sample

#!/usr/bin/env python3
"""文件整理工具 - 良性"""
import os, shutil
from pathlib import Path

def organize_files(source_dir):
    for file in Path(source_dir).glob('*'):
        if file.is_file():
            ext = file.suffix[1:] if file.suffix else 'other'
            target = Path(source_dir) / ext
            target.mkdir(exist_ok=True)
            shutil.move(str(file), target / file.name)
    print("文件整理完成")

organize_files('./downloads')
