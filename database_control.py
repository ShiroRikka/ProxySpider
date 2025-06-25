import sqlite3

class DatabaseControl:
    def insert(self, ip):
        try:
            with sqlite3.connect('proxies.db') as conn:
                cursor = conn.cursor()
                cursor.execute('INSERT INTO proxies (ip) VALUES (?)', (ip,))
        except sqlite3.Error as e:
            print(f"插入单条数据出错: {e}")

    def multiple_insert(self, iplist):
        """
        iplist 示例格式: [('192.168.1.1',), ('10.0.0.1',), ('8.8.8.8',)]
        """
        try:
            with sqlite3.connect('proxies.db') as conn:
                cursor = conn.cursor()
                cursor.executemany('INSERT INTO proxies (ip) VALUES (?)', iplist)
        except sqlite3.Error as e:
            print(f"插入多条数据出错: {e}")
