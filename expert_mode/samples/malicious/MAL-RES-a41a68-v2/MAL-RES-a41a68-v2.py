# 死循环计算
while True:
    x = 2 ** 1000
    y = x % 17
    print(f"Computing... {y}")
