import requests
from bs4 import BeautifulSoup
import time
import sqlite3
from datetime import datetime, timedelta

header={
    "accept":"*/*",
    "accept-encoding":"gzip, deflate, br, zstd",
    "accept-language":"zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "connection":"keep-alive",
    "host":"api.checkerproxy.net",
    "referer":"https://checkerproxy.net/",
    "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 Edg/137.0.0.0"
}

current_time = datetime.now()
noon_time = current_time.replace(hour=12, minute=0, second=0, microsecond=0)

if current_time > noon_time:
    # 如果当前时间超过12点，使用当前日期
    date_str = current_time.strftime("%Y-%m-%d")
else:
    # 如果当前时间未超过12点，使用前一天日期
    yesterday = current_time - timedelta(days=1)
    date_str = yesterday.strftime("%Y-%m-%d")


url = "https://api.checkerproxy.net/v1/landing/archive/%s"%date_str

response = requests.get(url=url,headers=header)

ip_json_data = response.json()

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
def insert_proxy(conn, proxy_list):
    """批量插入代理到数据库"""
    cursor = conn.cursor()
    success_count = 0
    skip_count = 0
    
    for proxy in proxy_list:
        try:
            # 初始化代理状态
            current_time = datetime.now()
            proxy_data = (proxy, current_time, 0, None)  # ip, last_checked, is_alive, response_time
            
            cursor.execute('''
            INSERT INTO proxies (ip, last_checked, is_alive, response_time)
            VALUES (?, ?, ?, ?)
            ''', proxy_data)
            
            success_count += 1
            print(f"代理已添加: {proxy}")
            
        except sqlite3.IntegrityError:
            skip_count += 1
            print(f"代理已存在: {proxy} - 跳过")
            continue
    
    conn.commit()
    print(f"\n批量导入完成 - 成功: {success_count}, 跳过: {skip_count}")
    return success_count

# 从json数据中获取代理列表并插入数据库
proxy_list = ip_json_data['data']['proxyList']
insert_proxy(conn, proxy_list)


def check_proxy_status(conn, proxy_ip):
    """检查代理状态并更新数据库"""
    cursor = conn.cursor()
    
    # 初始化结果字典
    result = {
        "proxy": proxy_ip,
        "status": "failed",
        "response_time": None,
        "error": None
    }
    
    try:
        session = requests.Session()
        session.trust_env = False
        
        # 配置代理
        proxies = {
            "http": f"http://{proxy_ip}",
            "https": f"http://{proxy_ip}"
        }
        
        # 测试连通性和响应时间
        start_time = time.time()
        response = session.get(
            "https://api.bilibili.com/x/web-interface/nav",
            proxies=proxies,  # 添加代理配置
            timeout=10,
            headers={
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0",
            }
        )
        end_time = time.time()
        response_time = round((end_time - start_time) * 1000, 2)  # 转换为毫秒
        
        if response.status_code == 200:
            result["status"] = "success"
            result["response_time"] = response_time
            # 更新数据库中代理状态为有效
            cursor.execute(
                'UPDATE proxies SET is_alive = 1, response_time = ?, last_checked = CURRENT_TIMESTAMP WHERE ip = ?',
                (response_time, proxy_ip)
            )
            print(f"代理 {proxy_ip} 状态检查成功，响应时间: {response_time} 毫秒")
        else:
            result["error"] = f"B站连接失败: HTTP {response.status_code}"
            # 更新数据库中代理状态为无效
            cursor.execute(
                'UPDATE proxies SET is_alive = 0, response_time = NULL, last_checked = CURRENT_TIMESTAMP WHERE ip = ?',
                (proxy_ip,)
            )
            print(f"代理 {proxy_ip} 状态检查失败: HTTP {response.status_code}")
            
    except requests.exceptions.Timeout:
        result["error"] = "连接超时"
        cursor.execute(
            'UPDATE proxies SET is_alive = 0, response_time = NULL, last_checked = CURRENT_TIMESTAMP WHERE ip = ?',
            (proxy_ip,)
        )
        print(f"代理 {proxy_ip} 状态检查失败: 连接超时")
        
    except requests.exceptions.ProxyError:
        result["error"] = "代理服务器错误"
        cursor.execute(
            'UPDATE proxies SET is_alive = 0, response_time = NULL, last_checked = CURRENT_TIMESTAMP WHERE ip = ?',
            (proxy_ip,)
        )
        print(f"代理 {proxy_ip} 状态检查失败: 代理服务器错误")
        
    except Exception as e:
        result["error"] = f"未知错误: {str(e)}"
        cursor.execute(
            'UPDATE proxies SET is_alive = 0, response_time = NULL, last_checked = CURRENT_TIMESTAMP WHERE ip = ?',
            (proxy_ip,)
        )
        print(f"代理 {proxy_ip} 状态检查失败: {str(e)}")
    
    conn.commit()
    return result

# 获取所有代理并测试
cursor = conn.cursor()
cursor.execute('SELECT ip FROM proxies')
proxies = cursor.fetchall()

for proxy in proxies:
    proxy_ip = proxy[0]
    result = check_proxy_status(conn, proxy_ip)
    print(f"测试结果: {result}")

# 关闭数据库连接
conn.close()

