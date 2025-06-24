import sqlite3
import time
import random
import pyperclip
from datetime import datetime, timedelta

# 创建并连接数据库
def create_database():
    conn = sqlite3.connect('proxy_pool.db')
    cursor = conn.cursor()
    
    # 创建代理表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS proxies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ip TEXT NOT NULL,
        port INTEGER NOT NULL,
        protocol TEXT CHECK(protocol IN ('http', 'https', 'socks4', 'socks5')),
        country TEXT,
        anonymity TEXT CHECK(anonymity IN ('transparent', 'anonymous', 'elite')),
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
    
    conn.commit()
    print("数据库和表已成功创建")
    return conn

# 插入单个代理
def insert_proxy(conn, proxy):
    """插入单个代理到数据库"""
    cursor = conn.cursor()
    try:
        cursor.execute('''
        INSERT INTO proxies (ip, port, protocol, country, anonymity, response_time)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', proxy)
        conn.commit()
        print(f"代理已添加: {proxy[0]}:{proxy[1]}")
        return True
    except sqlite3.IntegrityError:
        print(f"代理已存在: {proxy[0]}:{proxy[1]} - 跳过")
        return False

# 批量插入代理
def batch_insert_proxies(conn, proxies):
    """批量插入代理列表"""
    cursor = conn.cursor()
    new_count = 0
    
    for proxy in proxies:
        try:
            cursor.execute('''
            INSERT INTO proxies (ip, port, protocol, country, anonymity, response_time)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', proxy)
            new_count += 1
        except sqlite3.IntegrityError:
            # 代理已存在，跳过
            continue
    
    conn.commit()
    print(f"批量添加完成: 共添加 {new_count} 个新代理, {len(proxies) - new_count} 个已存在")
    return new_count

# 测试代理可用性（模拟）
def test_proxy(proxy):
    """模拟测试代理可用性"""
    # 在实际应用中，这里会发送测试请求
    # 模拟80%的成功率
    is_alive = random.random() > 0.2
    response_time = random.randint(50, 500) if is_alive else None
    return is_alive, response_time

# 更新代理状态
def update_proxy_status(conn):
    """更新代理状态（模拟定时任务）"""
    cursor = conn.cursor()
    
    # 获取所有需要检查的代理（最近5分钟未检查的）
    five_min_ago = datetime.now() - timedelta(minutes=5)
    cursor.execute('''
    SELECT id, ip, port, protocol 
    FROM proxies 
    WHERE last_checked < ? 
    ORDER BY last_checked ASC
    ''', (five_min_ago,))
    
    proxies_to_check = cursor.fetchall()
    print(f"需要检查 {len(proxies_to_check)} 个代理")
    
    updated_count = 0
    for proxy in proxies_to_check:
        proxy_id, ip, port, protocol = proxy
        is_alive, response_time = test_proxy((ip, port, protocol))
        
        cursor.execute('''
        UPDATE proxies 
        SET last_checked = CURRENT_TIMESTAMP, 
            is_alive = ?, 
            response_time = ?
        WHERE id = ?
        ''', (is_alive, response_time, proxy_id))
        
        updated_count += 1
    
    conn.commit()
    print(f"代理状态更新完成: 已更新 {updated_count} 个代理")
    return updated_count

# 删除无效代理
def remove_dead_proxies(conn):
    """删除标记为无效的代理"""
    cursor = conn.cursor()
    
    # 先获取要删除的代理数量用于报告
    cursor.execute('SELECT COUNT(*) FROM proxies WHERE is_alive = 0')
    dead_count = cursor.fetchone()[0]
    
    # 执行删除操作
    cursor.execute('DELETE FROM proxies WHERE is_alive = 0')
    conn.commit()
    
    print(f"已删除 {dead_count} 个无效代理")
    return dead_count

# 获取可用代理列表
def get_available_proxies(conn, protocol=None, limit=10):
    """获取可用代理列表，支持协议筛选和数量限制"""
    cursor = conn.cursor()
    query = '''
    SELECT ip, port, protocol, response_time, last_checked 
    FROM proxies 
    WHERE is_alive = 1 
    '''
    params = []
    
    if protocol:
        query += ' AND protocol = ?'
        params.append(protocol)
    
    query += ' ORDER BY response_time ASC, last_checked DESC'
    
    if limit:
        query += ' LIMIT ?'
        params.append(limit)
    
    cursor.execute(query, params)
    return cursor.fetchall()

# 导出代理到剪贴板
def export_proxies_to_clipboard(conn, protocol=None, limit=None):
    """导出代理到剪贴板"""
    proxies = get_available_proxies(conn, protocol, limit)
    
    if not proxies:
        print("没有可用的代理可导出")
        return False
    
    # 格式化代理为 ip:port 每行一个
    proxy_list = [f"{proxy[0]}:{proxy[1]}" for proxy in proxies]
    proxy_text = "\n".join(proxy_list)
    
    # 复制到剪贴板
    pyperclip.copy(proxy_text)
    
    print(f"已将 {len(proxy_list)} 个代理复制到剪贴板")
    print(f"示例: {proxy_list[0]} 等...")
    return True

# 显示数据库统计信息
def show_database_stats(conn):
    """显示数据库统计信息"""
    cursor = conn.cursor()
    
    # 总数统计
    cursor.execute('SELECT COUNT(*) FROM proxies')
    total = cursor.fetchone()[0]
    
    # 可用代理统计
    cursor.execute('SELECT COUNT(*) FROM proxies WHERE is_alive = 1')
    alive = cursor.fetchone()[0]
    
    # 按协议统计
    cursor.execute('''
    SELECT protocol, COUNT(*) 
    FROM proxies 
    WHERE is_alive = 1 
    GROUP BY protocol
    ''')
    protocol_stats = cursor.fetchall()
    
    # 响应时间统计
    cursor.execute('''
    SELECT AVG(response_time), MIN(response_time), MAX(response_time)
    FROM proxies 
    WHERE is_alive = 1 AND response_time IS NOT NULL
    ''')
    time_stats = cursor.fetchone()
    
    print("\n===== 代理池统计 =====")
    print(f"总代理数: {total}")
    print(f"可用代理: {alive} ({alive/total*100:.1f}%)")
    print("按协议分布:")
    for protocol, count in protocol_stats:
        print(f"  {protocol.upper()}: {count} ({count/alive*100:.1f}%)")
    
    if time_stats and time_stats[0]:
        avg, min_time, max_time = time_stats
        print(f"响应时间: 平均 {avg:.1f}ms, 最小 {min_time}ms, 最大 {max_time}ms")
    print("======================")

# 主程序
def main():
    # 创建数据库连接
    conn = create_database()
    
    # 添加一些示例代理
    sample_proxies = [
        ('192.168.1.101', 8080, 'http', 'US', 'anonymous', 120),
        ('192.168.1.102', 3128, 'https', 'UK', 'elite', 80),
        ('192.168.1.103', 8888, 'socks5', 'DE', 'anonymous', 200),
        ('192.168.1.104', 1080, 'socks4', 'FR', 'transparent', 150),
        ('192.168.1.105', 8080, 'http', 'CA', 'anonymous', 90),
        ('192.168.1.106', 3128, 'https', 'US', 'elite', 110),
        ('192.168.1.107', 8888, 'socks5', 'JP', 'anonymous', 180),
        ('192.168.1.108', 1080, 'socks4', 'RU', 'transparent', 220),
    ]
    
    # 批量插入代理
    batch_insert_proxies(conn, sample_proxies)
    
    # 模拟定时任务：更新代理状态
    print("\n模拟代理状态检查...")
    update_proxy_status(conn)
    
    # 显示数据库统计
    show_database_stats(conn)
    
    # 导出HTTP代理到剪贴板
    print("\n导出HTTP代理到剪贴板:")
    export_proxies_to_clipboard(conn, protocol='http')
    
    # 模拟添加更多代理
    print("\n模拟添加新代理...")
    new_proxies = [
        ('192.168.1.109', 8080, 'http', 'CN', 'anonymous', 100),
        ('192.168.1.110', 3128, 'https', 'IN', 'elite', 85),
        ('192.168.1.101', 8080, 'http', 'US', 'anonymous', 120),  # 重复代理
    ]
    batch_insert_proxies(conn, new_proxies)
    
    # 再次更新状态
    print("\n第二次代理状态检查...")
    update_proxy_status(conn)
    
    # 删除无效代理
    print("\n清理无效代理...")
    remove_dead_proxies(conn)
    
    # 最终统计
    show_database_stats(conn)
    
    # 导出所有可用代理
    print("\n导出所有可用代理到剪贴板:")
    export_proxies_to_clipboard(conn)
    
    # 关闭连接
    conn.close()
    print("\n数据库操作完成")

if __name__ == "__main__":
    main()