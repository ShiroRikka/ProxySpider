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


# 获取所有代理并测试
# 这一段代码将移动到 schedule_proxy_check 函数中
# cursor = conn.cursor()
# cursor.execute('SELECT ip, port FROM proxies')
# proxies = cursor.fetchall()

# for proxy in proxies:
#     proxy_ip_port = f"{proxy[0]}:{proxy[1]}"
#     result = check_proxy_status(conn, proxy_ip_port)
#     print(f"测试结果: {result}")

def schedule_proxy_check(conn, interval_seconds=3600):
    """
    定时检查代理可用性并更新数据库。
    :param conn: SQLite数据库连接对象
    :param interval_seconds: 检查间隔时间（秒），默认为1小时
    """
    cursor = conn.cursor()
    while True:
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始定时代理检查...")
        cursor.execute('SELECT ip, port FROM proxies')
        proxies_to_check = cursor.fetchall()

        for proxy in proxies_to_check:
            proxy_ip_port = f"{proxy[0]}:{proxy[1]}"
            check_proxy_status(conn, proxy_ip_port)
        
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 代理检查完成，等待 {interval_seconds} 秒进行下一次检查...")
        time.sleep(interval_seconds)

def delete_inactive_proxies(conn, inactive_threshold_hours=24):
    """
    从数据库中删除长时间不活跃的代理。
    :param conn: SQLite数据库连接对象
    :param inactive_threshold_hours: 代理被视为不活跃的时间阈值（小时），默认为24小时
    """
    cursor = conn.cursor()
    # 计算不活跃时间戳
    threshold_time = datetime.now() - timedelta(hours=inactive_threshold_hours)
    
    cursor.execute('''
    DELETE FROM proxies
    WHERE is_alive = 0 AND last_check_time < ?
    ''', (threshold_time.strftime('%Y-%m-%d %H:%M:%S'),))
    
    deleted_count = cursor.rowcount
    conn.commit()
    print(f"已从数据库中删除 {deleted_count} 个不活跃代理。")
    return deleted_count

def get_available_proxies(conn, protocol=None, country=None, anonymity=None, min_response_time=None, max_response_time=None, limit=None):
    """
    根据条件从数据库中获取可用的代理。
    :param conn: SQLite数据库连接对象
    :param protocol: 协议类型 (e.g., 'HTTP', 'HTTPS')
    :param country: 国家
    :param anonymity: 匿名度 (e.g., 'elite', 'anonymous', 'transparent')
    :param min_response_time: 最小响应时间（毫秒）
    :param max_response_time: 最大响应时间（毫秒）
    :param limit: 返回代理的最大数量
    :return: 符合条件的代理列表 (ip:port)
    """
    cursor = conn.cursor()
    query = "SELECT ip, port FROM proxies WHERE is_alive = 1"
    params = []

    if protocol:
        query += " AND protocol = ?"
        params.append(protocol)
    if country:
        query += " AND country = ?"
        params.append(country)
    if anonymity:
        query += " AND anonymity = ?"
        params.append(anonymity)
    if min_response_time is not None:
        query += " AND response_time >= ?"
        params.append(min_response_time)
    if max_response_time is not None:
        query += " AND response_time <= ?"
        params.append(max_response_time)
    
    query += " ORDER BY response_time ASC" # 优先返回响应时间更短的代理

    if limit:
        query += " LIMIT ?"
        params.append(limit)

    cursor.execute(query, tuple(params))
    proxies = cursor.fetchall()
    return [f"{ip}:{port}" for ip, port in proxies]

def export_proxies_to_clipboard(conn, alive_only=True):
    """
    将当前数据库中所有或符合特定条件的可用代理以 ip:port 的格式复制到用户的剪贴板。
    :param conn: SQLite数据库连接对象
    :param alive_only: 是否只导出活跃代理，默认为True
    """
    try:
        import pyperclip
    except ImportError:
        print("pyperclip 库未安装。请运行 'pip install pyperclip' 进行安装。")
        return

    cursor = conn.cursor()
    if alive_only:
        cursor.execute('SELECT ip, port FROM proxies WHERE is_alive = 1')
    else:
        cursor.execute('SELECT ip, port FROM proxies')
    
    proxies = cursor.fetchall()
    proxy_list_str = "\n".join([f"{ip}:{port}" for ip, port in proxies])

    if proxy_list_str:
        pyperclip.copy(proxy_list_str)
        print(f"已将 {len(proxies)} 个代理复制到剪贴板。")
    else:
        print("没有找到符合条件的代理可供导出。")

def generate_proxy_report(conn):
    """
    生成并打印代理池的详细统计报告。
    :param conn: SQLite数据库连接对象
    """
    cursor = conn.cursor()

    print("\n--- 代理池统计报告 ---")

    # 总代理数量
    cursor.execute('SELECT COUNT(*) FROM proxies')
    total_proxies = cursor.fetchone()[0]
    print(f"总代理数量: {total_proxies}")

    # 活跃代理数量
    cursor.execute('SELECT COUNT(*) FROM proxies WHERE is_alive = 1')
    alive_proxies = cursor.fetchone()[0]
    print(f"活跃代理数量: {alive_proxies}")

    # 按协议分类
    cursor.execute('SELECT protocol, COUNT(*) FROM proxies GROUP BY protocol')
    protocol_counts = cursor.fetchall()
    print("\n按协议分类:")
    for protocol, count in protocol_counts:
        print(f"  {protocol}: {count}")

    # 按国家分类
    cursor.execute('SELECT country, COUNT(*) FROM proxies GROUP BY country')
    country_counts = cursor.fetchall()
    print("\n按国家分类:")
    for country, count in country_counts:
        print(f"  {country}: {count}")

    # 按匿名度分类
    cursor.execute('SELECT anonymity, COUNT(*) FROM proxies GROUP BY anonymity')
    anonymity_counts = cursor.fetchall()
    print("\n按匿名度分类:")
    for anonymity, count in anonymity_counts:
        print(f"  {anonymity}: {count}")

    # 平均响应时间
    cursor.execute('SELECT AVG(response_time) FROM proxies WHERE is_alive = 1 AND response_time IS NOT NULL')
    avg_response_time = cursor.fetchone()[0]
    if avg_response_time is not None:
        print(f"\n活跃代理平均响应时间: {avg_response_time:.2f} 毫秒")
    else:
        print("\n暂无活跃代理的平均响应时间数据。")
    
    print("--- 报告结束 ---")

# 主程序逻辑
if __name__ == "__main__":
    # 初始化数据库连接
    conn = sqlite3.connect('proxy_pool.db')
    cursor = conn.cursor()

    # 检查并创建代理表 (这部分代码已经存在于文件顶部，这里只是为了确保在 __main__ 中也可用)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS proxies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ip TEXT NOT NULL,
        port INTEGER NOT NULL,
        protocol TEXT,
        country TEXT,
        anonymity TEXT,
        last_check_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        response_time INTEGER,
        is_alive BOOLEAN DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(ip, port)
    )
    ''')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_is_alive ON proxies (is_alive)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_last_check_time ON proxies (last_check_time)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_response_time ON proxies (response_time)')
    conn.commit()
    print("数据库和表已成功创建/检查。")

    # 示例：获取并插入新代理
    # 这部分代码可以根据实际需求调整，例如每天只运行一次
    current_time = datetime.now()
    noon_time = current_time.replace(hour=12, minute=0, second=0, microsecond=0)

    if current_time > noon_time:
        date_str = current_time.strftime("%Y-%m-%d")
    else:
        yesterday = current_time - timedelta(days=1)
        date_str = yesterday.strftime("%Y-%m-%d")

    url = "https://api.checkerproxy.net/v1/landing/archive/%s"%date_str
    try:
        response = requests.get(url=url,headers=header, timeout=10)
        ip_json_data = response.json()
        processed_proxy_list = []
        for proxy_str in ip_json_data['data']['proxyList']:
            try:
                ip, port_str = proxy_str.split(':')
                port = int(port_str)
                processed_proxy_list.append({
                    'ip': ip,
                    'port': port,
                    'protocol': 'HTTP',
                    'country': 'UNKNOWN',
                    'anonymity': 'UNKNOWN'
                })
            except ValueError:
                print(f"无法解析代理字符串: {proxy_str}")
                continue
        insert_proxy(conn, processed_proxy_list)
    except requests.exceptions.RequestException as e:
        print(f"获取最新代理失败: {e}")

    # 运行定时检查（在一个单独的线程中运行，或者在主循环中调用）
    # 为了简单起见，这里直接调用一次，实际应用中可能需要多线程或异步
    # schedule_proxy_check(conn, interval_seconds=3600) # 如果要启用定时检查，请取消注释

    # 示例：删除不活跃代理
    delete_inactive_proxies(conn, inactive_threshold_hours=48) # 删除超过48小时不活跃的代理

    # 示例：获取可用代理
    print("\n--- 获取可用代理示例 ---")
    http_proxies = get_available_proxies(conn, protocol='HTTP', limit=5)
    print(f"前5个HTTP活跃代理: {http_proxies}")

    country_proxies = get_available_proxies(conn, country='US', anonymity='elite')
    print(f"美国精英匿名代理: {country_proxies}")

    # 示例：导出代理到剪贴板
    export_proxies_to_clipboard(conn, alive_only=True)

    # 示例：生成代理报告
    generate_proxy_report(conn)

    # 关闭数据库连接
    conn.close()

