from database_control import ProxyDB
"""
批量更新IP状态
ip_status_list 格式示例:
[
    {
        'proxy': 'http://152.42.170.187:9090',
        'status': 'success',
        'response_time': 4744.03,
        'error': None,
        'ip_info': None
    },
    ...
]
"""

def convert_ip_info(raw_list:list[dict])->list[tuple]:
    """
    返回的格式：[('152.42.170.187:9090', 1, 4744.03, 100)]
    返回的格式：[('IP', IS_ALIVE,response_time , SCORE)]
    """
    ip_info = []
    proxy_db = ProxyDB()
    for item in raw_list:
        proxy = item.get('proxy')
        status_str = item.get('status')
        response_time = item.get('response_time',0)
        try:
            ip_port = proxy.split('//')[-1]  # 去掉协议部分
        except (AttributeError, IndexError):
            continue
        # 转换状态
        status = 1 if status_str == 'success' else 0
        current_score = proxy_db.get_score(ip_port)
        if status == 1:
            update_score = 100
        else:
            update_score = (current_score if current_score is not None else 0) - 10
        ip_info.append((ip_port, status,response_time,update_score))
    return ip_info

if __name__ == "__main__":
    test=[
        {
            'proxy': 'http://152.42.170.187:9090',
            'status': 'success',
            'response_time': 4744.03,
            'error': None,
            'ip_info': None
        },
    ]
    print(convert_ip_info(test))