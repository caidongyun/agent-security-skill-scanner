import re
from collections import Counter

def analyze_log(log_file):
    ip_pattern = r'\d+\.\d+\.\d+\.\d+'
    ips = []
    
    with open(log_file) as f:
        for line in f:
            match = re.search(ip_pattern, line)
            if match:
                ips.append(match.group())
    
    return Counter(ips).most_common(10)

if __name__ == "__main__":
    top_ips = analyze_log("access.log")
    print(top_ips)
