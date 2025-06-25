import sqlite3


def insert(ip):
    try:
        with sqlite3.connect('proxies.db') as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO proxies (ip) VALUES (?)', (ip,))
        print(f"插入单条数据成功")
    except sqlite3.Error as e:
        print(f"插入单条数据出错:{e}")


def create():
    try:
        with sqlite3.connect('proxies.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS proxies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ip TEXT NOT NULL,
                last_checked TIMESTAMP DEFAULT (datetime('now', 'localtime')),
                score INTEGER DEFAULT 30,
                is_alive BOOLEAN DEFAULT 0,
                response_time INTEGER,
                created_at TIMESTAMP DEFAULT (datetime('now', 'localtime')),
                UNIQUE(ip)  -- 防止重复添加同一IP:端口
            )
            ''')
        print(f"数据库创建成功")
    except sqlite3.Error as e:
        print(f"数据库创建错误: {e}")


def multiple_insert(iplist):
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


def create_index():
    try:
        with sqlite3.connect('proxies.db') as conn:
            cursor = conn.cursor()
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_alive ON proxies (is_alive)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_last_checked ON proxies (last_checked)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_response_time ON proxies (response_time)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_score ON proxies (score)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_created_at ON proxies (created_at)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_alive_created ON proxies (is_alive, created_at)')
        print(f"数据库索引成功")
    except sqlite3.Error as e:
        print(f"数据库索引错误:{e}")
#
#
# def get_ip_to_test():
#     try:
#         with sqlite3.connect('proxies.db') as conn:
#             cursor = conn.cursor()
#             cursor.execute("SELECT ip FROM proxies WHERE is_alive = 0 ORDER BY created_at LIMIT 1")
#             result = cursor.fetchone()[0]
#             return 'http://' + result # 返回 (id, ip) 或 None
#     except sqlite3.Error as e:
#         print(f"ip读取错误：{e}")
#

def get_ips_to_test(limit: int =10):
    """
    批量获取待测试的IP，默认一次取10条
    返回格式：[ip1, ip2, ...]
    """
    try:
        with sqlite3.connect('proxies.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT ip FROM proxies WHERE  score >0 AND score < 80 ORDER BY score DESC LIMIT ?", (limit,))
            results = cursor.fetchall()
            results = ','.join(['http://' + row[0] for row in results])
            return results  # 返回IP字符串列表
    except sqlite3.Error as e:
        print(f"批量IP读取错误：{e}")
        return []


def get_best_ips_to_test():
    try:
        with sqlite3.connect('proxies.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT ip FROM proxies WHERE score > 80")
            results = cursor.fetchall()
            results = ','.join(['http://' + row[0] for row in results])
            return results  # 返回IP字符串列表
    except sqlite3.Error as e:
        print(f"批量IP读取错误：{e}")
        return []

def count_best_score_proxies():
    try:
        with sqlite3.connect('proxies.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM proxies WHERE score > 80")
            result = cursor.fetchone()
            return result[0] if result else 0
    except sqlite3.Error as e:
        print(f"查询高分代理数量出错: {e}")
        return 0

def update_ip_status(ip, status):
    try:
        with sqlite3.connect('proxies.db') as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE proxies 
                SET last_checked = datetime('now', 'localtime'), is_alive = ?
                WHERE ip = ?
            """, (status, ip))
    except sqlite3.Error as e:
        print(f"更新代理状态失败{e}")


def update_ips_status(ip_status_list):
    """
    批量更新IP状态
    ip_status_list 格式示例: [('192.168.1.1', 1), ('10.0.0.1', 0), ...]
    """
    try:
        with sqlite3.connect('proxies.db') as conn:
            cursor = conn.cursor()
            data = [(status, response_time,score, ip) for ip, status, response_time ,score in ip_status_list]
            cursor.executemany("""
                UPDATE proxies 
                SET last_checked = datetime('now', 'localtime'), is_alive = ?, response_time = ?,score = ?
                WHERE ip = ?
            """, data)

        print(f"批量更新了 {len(ip_status_list)} 条IP状态")
    except sqlite3.Error as e:
        print(f"批量更新代理状态失败: {e}")


def delete_worse_ip():
    try:
        with sqlite3.connect('proxies.db') as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM proxies WHERE score <= 0")
            conn.commit()
            deleted_count = cursor.rowcount
            print(f"成功删除 {deleted_count} 条评分<=0的代理IP")
            return True
    except sqlite3.Error as e:
        print(f"移除异常代理失败: {e}")
        return False

def delete_old_ip():
    try:
        with sqlite3.connect('proxies.db') as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM proxies WHERE created_at < datetime('now', 'localtime', '-1 day') AND score < 80" )
            conn.commit()
            deleted_count = cursor.rowcount
            print(f"成功删除 {deleted_count} 条创建时间超过1天的老旧代理IP")
            return True
    except sqlite3.Error as e:
        print(f"移除异常代理失败: {e}")
        return False

def get_current_score(ip_port):
    try:
        with sqlite3.connect('proxies.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT score FROM proxies WHERE ip = ?",(ip_port,))
            result = cursor.fetchone()
            if result:
                return result[0]
            else:
                return None
    except sqlite3.Error as e:
        print(f"score读取错误：{e}")
        return None

def count_low_score_proxies():
    try:
        with sqlite3.connect('proxies.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM proxies WHERE score > 10 AND score < 80")
            result = cursor.fetchone()
            return result[0]
    except sqlite3.Error as e:
        print(f"查询低分代理数量出错: {e}")
        return 0

def delete_duplicate_ips():
    try:
        with sqlite3.connect('proxies.db') as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM proxies
                WHERE id NOT IN (
                    SELECT MIN(id) FROM proxies GROUP BY ip
                )
            """)
            conn.commit()
            print(f"成功删除重复代理IP，删除了 {cursor.rowcount} 条记录")
            return True
    except sqlite3.Error as e:
        print(f"删除重复代理IP失败: {e}")
        return False
