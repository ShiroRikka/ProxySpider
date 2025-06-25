import sqlite3

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
        except sqlite3.Error as e:
            print(f"数据库创建错误: {e}")

    def insert(self, ip):
        try:
            with sqlite3.connect('proxies.db') as conn:
                cursor = conn.cursor()
                cursor.execute('INSERT INTO proxies (ip) VALUES (?)', (ip,))
        except sqlite3.Error as e:
            print(f"插入单条数据出错:{e}")

    def multiple_insert(self, iplist):
        """
        iplist 示例格式: [('192.168.1.1',), ('10.0.0.1',), ('8.8.8.8',)]
        """
        try:
            with sqlite3.connect('proxies.db') as conn:
                cursor = conn.cursor()
                cursor.executemany('INSERT INTO proxies (ip) VALUES (?)', iplist)
        except sqlite3.Error as e:
            print(f"插入多条数据出错:{e}")

    def create_index(self):
        try:
            with sqlite3.connect('proxies.db') as conn:
                cursor = conn.cursor()
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_alive ON proxies (is_alive)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_last_checked ON proxies (last_checked)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_response_time ON proxies (response_time)')
        except sqlite3.Error as e:
            print(f"数据库索引错误:{e}")


