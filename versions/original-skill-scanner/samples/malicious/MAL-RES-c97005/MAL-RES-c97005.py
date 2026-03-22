# 分配大量内存
data = []
for i in range(10000000):
    data.append("X" * 1000)  # 每个元素 1KB
print("Memory exhausted")
