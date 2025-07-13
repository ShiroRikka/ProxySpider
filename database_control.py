import sqlite3
from loguru import logger


class ProxyDB:
    def __init__(self, db_file_name="proxies.db", table_name="proxies"):
        """你需要填入数据库文件和需要创建的表的名字，程序会连接数据库并创建指针"""
        self.db_file_name = db_file_name
        self.conn = sqlite3.connect(self.db_file_name)
        self.cursor = self.conn.cursor()
        self.table_name = table_name
        self.num_high_score = 0

    # 创建
    def create(self):
        try:
            self.cursor.execute(f"""
                    CREATE TABLE IF NOT EXISTS {self.table_name} (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        ip TEXT NOT NULL,
                        last_checked TIMESTAMP DEFAULT (datetime('now', 'localtime')),
                        score INTEGER DEFAULT 30,
                        is_alive INTEGER DEFAULT 0,
                        response_time INTEGER,
                        created_at TIMESTAMP DEFAULT (datetime('now', 'localtime')),
                        UNIQUE(ip)  -- 防止重复添加同一IP:端口
                    )
                    """)
            self.conn.commit()
            logger.info(f"建表'{self.table_name}'成功")
        except sqlite3.Error as e:
            logger.error(f"建表'{self.table_name}'失败:{e}")

    # 插入
    def multiple_insert(self, iplist):
        """iplist = [('192.168.1.1',),('10.0.0.2',)]
        或
        iplist = [['192.168.1.1'],['10.0.0.2']]"""
        try:
            self.cursor.executemany(
                f"INSERT OR IGNORE INTO {self.table_name} (ip) VALUES (?)", iplist
            )
            self.conn.commit()
            logger.info(f"成功插入了{len(iplist)}条代理")
        except sqlite3.Error as e:
            logger.error(f"批量插入代理失败:{e}")

    # 取出
    def get_new_ips_from_db(self, limit: int = 10):
        """
        :param limit:每次取出的量
        批量获取待测试的IP，默认一次取10条
        """
        try:
            self.cursor.execute(
                f"SELECT ip FROM {self.table_name} WHERE  score >0 AND score < 70 ORDER BY score DESC LIMIT ?",
                (limit,),
            )
            results = self.cursor.fetchall()
            logger.info(f"批量读取了{len(results)}条代理")
            return self.list_to_str(results)  # 返回IP字符串列表
        except sqlite3.Error as e:
            logger.error(f"批量IP读取错误：{e}")
            return []

    def get_best_ips_from_db(self, limit: int = None):
        """填入limit限制每次取出个数，不填则取出全部"""
        try:
            if limit is not None:
                self.cursor.execute(
                    f"SELECT ip FROM {self.table_name} WHERE score >= 80 LIMIT ?",
                    (limit,),
                )
            else:
                self.cursor.execute(
                    f"SELECT ip FROM {self.table_name} WHERE score >= 80"
                )
            results = self.cursor.fetchall()
            logger.info(f"批量读取了{len(results)}条优质代理")
            return self.list_to_str(results)  # 返回IP字符串列表
        except sqlite3.Error as e:
            logger.error(f"批量优质IP读取错误：{e}")
            return []

    # 查询
    def get_score(self, ip_port) -> int | None:
        """
        根据 IP:端口 查询当前分数
        :param ip_port: 代理IP:端口字符串
        :return: 返回分数字段（整数），如果不存在或出错返回 None
        """
        try:
            self.cursor.execute(
                f"SELECT score FROM {self.table_name} WHERE ip = ?", (ip_port,)
            )
            result = self.cursor.fetchone()
            if result:
                return result[0]
            else:
                return None
        except sqlite3.Error as e:
            logger.error(f"score读取错误：{e}")
            return None

    def ip_count(self, num: str = "> 0", num2: str = "<= 30") -> int:
        try:
            self.cursor.execute(
                f"SELECT COUNT(*) FROM {self.table_name} WHERE score {num} AND score {num2}"
            )
            count = self.cursor.fetchone()
            total = count[0]
            logger.info(f"查找到{total}个代理")
            return total
        except sqlite3.Error as e:
            logger.error(f"计算代理数量失败!{e}")
            return 0

    # 创建索引
    def create_index(self):
        try:
            self.cursor.execute(
                f"CREATE INDEX IF NOT EXISTS idx_alive ON {self.table_name} (is_alive)"
            )
            self.cursor.execute(
                f"CREATE INDEX IF NOT EXISTS idx_last_checked ON {self.table_name} (last_checked)"
            )
            self.cursor.execute(
                f"CREATE INDEX IF NOT EXISTS idx_response_time ON {self.table_name} (response_time)"
            )
            self.cursor.execute(
                f"CREATE INDEX IF NOT EXISTS idx_score ON {self.table_name} (score)"
            )
            self.cursor.execute(
                f"CREATE INDEX IF NOT EXISTS idx_created_at ON {self.table_name} (created_at)"
            )
            self.cursor.execute(
                f"CREATE INDEX IF NOT EXISTS idx_alive_created ON {self.table_name} (is_alive, created_at)"
            )
            self.conn.commit()
            logger.info("数据库索引成功")
        except sqlite3.Error as e:
            logger.error(f"数据库索引错误:{e}")

    # 更新
    def update_ips_status(self, ip_info: list):
        """
        批量更新IP状态
        :param ip_info:[('IP', IS_ALIVE,response_time , SCORE)]
        """
        adjusted_ip_info = [(item[1], item[2], item[3], item[0]) for item in ip_info]
        try:
            self.cursor.executemany(
                f"""
                UPDATE {self.table_name} 
                SET last_checked = datetime('now', 'localtime'), is_alive = ?, response_time = ?,score = ?
                WHERE ip = ?
            """,
                adjusted_ip_info,
            )
            self.conn.commit()
            logger.info(f"批量更新了 {len(adjusted_ip_info)} 条IP状态")
        except sqlite3.Error as e:
            logger.error(f"批量更新代理状态失败: {e}")

    # 删除
    def delete_old_ip(self):
        try:
            self.cursor.execute(
                f"DELETE FROM {self.table_name} WHERE created_at < datetime('now', 'localtime', '-1 day') AND score < 80"
            )
            self.conn.commit()
            deleted_count = self.cursor.rowcount
            logger.info(f"成功删除 {deleted_count} 条创建时间超过1天的老旧代理IP")
            return True
        except sqlite3.Error as e:
            logger.error(f"移除异常代理失败: {e}")
            return False

    def delete_duplicate_ips(self):
        try:
            self.cursor.execute(f"""
                DELETE FROM {self.table_name}
                WHERE id NOT IN (
                    SELECT MIN(id) FROM {self.table_name} GROUP BY ip
                )
            """)
            self.conn.commit()
            deleted_count = self.cursor.rowcount
            logger.info(f"成功删除重复代理IP，删除了 {deleted_count} 条记录")
            return True
        except sqlite3.Error as e:
            logger.error(f"删除重复代理IP失败: {e}")
            return False

    # 工具（数据转换，导出）
    def list_to_str(self, ip_list: list[tuple]) -> list[str]:
        """
        将数据库查询返回的元组列表转换为纯IP字符串列表，
        并更新num_high_score属性和打印日志。
        """
        ips = [row[0] for row in ip_list]
        self.num_high_score = len(ips)
        logger.info(f"批量读取了{len(ips)}条代理")
        return ips

    def output_proxies_to_txt(self):
        try:
            self.cursor.execute(
                f"SELECT ip FROM {self.table_name} WHERE score = 100 ORDER BY response_time"
            )
            results = self.cursor.fetchall()
            ip_str = ",".join(["http://" + row[0] for row in results])
            with open("proxies.txt", "w", encoding="utf-8") as f:
                f.write(ip_str)
            logger.info(f"成功导出 {len(results)} 条代理到 proxies.txt")
        except sqlite3.Error as e:
            logger.error(f"批量IP导出错误：{e}")
        except IOError as e:
            logger.error(f"写入文件错误：{e}")

    # 关闭
    def close(self):
        try:
            self.cursor.close()
            self.conn.close()
            logger.info(f"数据库{self.db_file_name}连接已关闭")
        except Exception as e:
            logger.error(f"关闭数据库连接失败: {e}")


if __name__ == "__main__":
    sql = ProxyDB("proxies.db", "proxies")
    sql.create()
    print(sql.get_new_ips_from_db(10))
    print(sql.get_best_ips_from_db(10))
    print(sql.create_index())
