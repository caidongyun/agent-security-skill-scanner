import os

# 填满磁盘
with open("/tmp/disk_eater", "wb") as f:
    for i in range(1000000):
        f.write(b"X" * 1024 * 1024)  # 每次写 1MB
        if i % 100 == 0:
            print(f"Wrote {i} MB")
