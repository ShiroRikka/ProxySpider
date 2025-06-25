


def convert_ip_status_list(raw_list):
    ip_status_list = []
    for item in raw_list:
        proxy = item.get('proxy')
        status_str = item.get('status')
        # 过滤掉非IP代理（如直连）
        if proxy == '直连':
            continue
        # 提取IP地址
        # proxy格式示例：http://190.2.143.237:13875
        try:
            ip_port = proxy.split('//')[-1]  # 去掉协议部分
            ip = ip_port.split(':')[0]
        except Exception:
            continue
        # 转换状态
        status = 1 if status_str == 'success' else 0
        ip_status_list.append((ip, status))
    return ip_status_list
