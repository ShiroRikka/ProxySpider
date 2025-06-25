import requests
import sqlite3
from get_url_time import get_url_time

header={
    "accept":"*/*",
    "accept-encoding":"gzip, deflate, br, zstd",
    "accept-language":"zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "connection":"keep-alive",
    "host":"api.checkerproxy.net",
    "referer":"https://checkerproxy.net/",
    "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 Edg/137.0.0.0"
}



url = "https://api.checkerproxy.net/v1/landing/archive/%s"%get_url_time()
print(url)

response = requests.get(url=url,headers=header)
print(response.status_code)

ip_json_data = response.json()
print(ip_json_data['data']['proxyList'])


conn = sqlite3.connect('proxy_pool.db')
cursor = conn.cursor()

# 检查并创建代理表
cursor.execute('''
CREATE TABLE IF NOT EXISTS proxies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ip TEXT NOT NULL,
    last_checked TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_alive BOOLEAN DEFAULT 0,
    response_time INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(ip)  -- 防止重复添加同一IP:端口
)
''')

# 创建索引以提高查询性能
cursor.execute('CREATE INDEX IF NOT EXISTS idx_alive ON proxies (is_alive)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_last_checked ON proxies (last_checked)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_response_time ON proxies (response_time)')


conn.commit()

print("数据库和表已成功创建")

cursor.execute('INSERT INTO proxies ip VALIES ?', ip_json_data['data']['proxyList'])













