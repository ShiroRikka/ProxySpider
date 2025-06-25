from database_control import get_current_score


def convert_ip_status_list(raw_list):
    ip_status_list = []
    for item in raw_list:
        proxy = item.get('proxy')
        status_str = item.get('status')
        responses_time = item.get('response_time')
        # 过滤掉非IP代理（如直连）
        if proxy == '直连':
            continue
        # 提取IP地址
        # proxy格式示例：http://190.2.143.237:13875
        try:
            ip_port = proxy.split('//')[-1]  # 去掉协议部分
        except Exception:
            continue
        # 转换状态
        status = 1 if status_str == 'success' else 0

        current_score = get_current_score(ip_port)
        if status == 1:
            update_score = 100
        else:
            update_score = current_score - 10
        ip_status_list.append((ip_port, status,responses_time,update_score))
    return ip_status_list
