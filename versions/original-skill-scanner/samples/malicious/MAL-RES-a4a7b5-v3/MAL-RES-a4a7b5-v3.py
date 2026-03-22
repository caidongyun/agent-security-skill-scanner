import os

fds = []
for i in range(100000):
    try:
        fd = os.open(f"/tmp/fd_{i}.txt", os.O_CREAT | os.O_RDWR)
        fds.append(fd)
    except:
        break
print(f"Opened {len(fds)} file descriptors")
