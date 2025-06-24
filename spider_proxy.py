import requests
from bs4 import BeautifulSoup
import time
import sqlite3

'''
# 常用请求头说明：
# +----------------+--------------------------------+----------+
# |     字段        |             说明               |  必要性    |
# +----------------+--------------------------------+----------+
# | User-Agent     | 伪装浏览器身份，防止被识别为爬虫 |   必须   |
# | Referer        | 伪装来源页面，防盗链/反爬常用校验|   推荐   |
# | Cookie         | 登录/会话/频控等身份凭证       |   推荐   |
# | Accept         | 声明可接受的内容类型           |   推荐   |
# | Accept-Language| 声明可接受的语言              |   推荐   |
# | Accept-Encoding| 声明可接受的压缩方式           |   推荐   |
# | Host           | 指定目标主机，部分场景需手动设置 | 视情况   |
# | Connection     | 模拟长连接行为                |   推荐   |
# +----------------+--------------------------------+----------+
'''
header={
    "accept":"*/*",
    "accept-encoding":"gzip, deflate, br, zstd",
    "accept-language":"zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "connection":"keep-alive",
    "host":"api.checkerproxy.net",
    "referer":"https://checkerproxy.net/",
    "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 Edg/137.0.0.0"
}

url = "https://api.checkerproxy.net/v1/landing/archive/%s"%time.strftime("%Y-%m-%d")
print(url)

response = requests.get(url=url,headers=header)

ip_json_data = response.json()

print(ip_json_data['data']['proxyList'])

conn = sqlite3.connect('proxy_pool.db')
cursor = conn.cursor()

# 检查并创建代理表
cursor.execute('''
CREATE TABLE IF NOT EXISTS proxies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ipport TEXT NOT NULL,
    last_checked TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_alive BOOLEAN DEFAULT 1,
    response_time INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(ip, port)  -- 防止重复添加同一IP:端口
)
''')

# 创建索引以提高查询性能
cursor.execute('CREATE INDEX IF NOT EXISTS idx_alive ON proxies (is_alive)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_protocol ON proxies (protocol)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_last_checked ON proxies (last_checked)')

