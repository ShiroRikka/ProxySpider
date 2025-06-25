import requests
from get_url_time import get_url_time

def get_proxy(url_time):
    header={
        "accept":"*/*",
        "accept-encoding":"gzip, deflate, br, zstd",
        "accept-language":"zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "connection":"keep-alive",
        "host":"api.checkerproxy.net",
        "referer":"https://checkerproxy.net/",
        "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 Edg/137.0.0.0"
    }

    url = "https://api.checkerproxy.net/v1/landing/archive/%s"%url_time
    print(url)

    response = requests.get(url=url,headers=header)
    print(f"获取代理成功：{response.status_code}")

    ip_json_data = response.json()

    tuple_list = [(ip,) for ip in ip_json_data['data']['proxyList']]

    return tuple_list



