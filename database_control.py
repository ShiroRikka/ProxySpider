import sqlite3
from datetime import datetime

class DatabaseControl:


    def create(self):
        try:
            with sqlite3.connect('proxies.db') as conn:
                cursor = conn.cursor()
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
            print(f"数据库创建成功")
        except sqlite3.Error as e:
            print(f"数据库创建错误: {e}")

    def insert(self, ip):
        try:
            with sqlite3.connect('proxies.db') as conn:
                cursor = conn.cursor()
                cursor.execute('INSERT INTO proxies (ip) VALUES (?)', (ip,))
            print(f"插入单条数据成功")
        except sqlite3.Error as e:
            print(f"插入单条数据出错:{e}")

    def multiple_insert(self, iplist):
        """
        iplist 示例格式: [('192.168.1.1',), ('10.0.0.1',), ('8.8.8.8',)]
        """
        try:
            with sqlite3.connect('proxies.db') as conn:
                cursor = conn.cursor()
                cursor.executemany('INSERT OR IGNORE INTO proxies (ip) VALUES (?)', iplist)
            print(f"插入多条数据成功")
        except sqlite3.Error as e:
            print(f"插入多条数据出错:{e}")

    def create_index(self):
        try:
            with sqlite3.connect('proxies.db') as conn:
                cursor = conn.cursor()
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_alive ON proxies (is_alive)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_last_checked ON proxies (last_checked)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_response_time ON proxies (response_time)')
            print(f"数据库索引成功")
        except sqlite3.Error as e:
            print(f"数据库索引错误:{e}")

    def get_ip_to_test(self):
        try:
            with sqlite3.connect('proxies.db') as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT ip FROM proxies WHERE is_alive = 0 ORDER BY created_at LIMIT 1")
                result = cursor.fetchone()[0]
                return 'http://' + result # 返回 (id, ip) 或 None
        except sqlite3.Error as e:
            print(f"ip读取错误：{e}")


    def get_ips_to_test(self, limit=10):
        """
        批量获取待测试的IP，默认一次取10条
        返回格式：[ip1, ip2, ...]
        """
        try:
            with sqlite3.connect('proxies.db') as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT ip FROM proxies WHERE is_alive = 0 ORDER BY created_at LIMIT ?", (limit,))
                results = cursor.fetchall()
                results = ','.join(['http://' + row[0] for row in results])
                return results  # 返回IP字符串列表
        except sqlite3.Error as e:
            print(f"批量IP读取错误：{e}")
            return []

    def update_ip_status(self, ip, status):
        try:
            with sqlite3.connect('proxies.db') as conn:
                cursor = conn.cursor()
                now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                cursor.execute("""
                    UPDATE proxies 
                    SET last_checked = ?, is_alive = ?
                    WHERE ip = ?
                """, (now, status, ip))
        except sqlite3.Error as e:
            print(f"更新代理状态失败")

    def update_ips_status(self, ip_status_list):
        """
        批量更新IP状态
        ip_status_list 格式示例: [('192.168.1.1', 1), ('10.0.0.1', 0), ...]
        """
        try:
            with sqlite3.connect('proxies.db') as conn:
                cursor = conn.cursor()
                now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                data = [(now, status, ip) for ip, status in ip_status_list]
                cursor.executemany("""
                    UPDATE proxies 
                    SET last_checked = ?, is_alive = ?
                    WHERE ip = ?
                """, data)

            print(f"批量更新了 {len(ip_status_list)} 条IP状态")
        except sqlite3.Error as e:
            print(f"批量更新代理状态失败: {e}")
