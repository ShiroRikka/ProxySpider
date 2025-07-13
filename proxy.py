import requests

from cal_time import today, yesterday


def get_proxy():
    header = {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "connection": "keep-alive",
        "host": "api.checkerproxy.net",
        "referer": "https://checkerproxy.net/",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 Edg/137.0.0.0",
    }

    url = "https://api.checkerproxy.net/v1/landing/archive/%s" % today()
    print(url)

    response = requests.get(url=url, headers=header)

    ip_json_data = response.json()

    if response.status_code != 200:
        print("今日的代理列表还未更新，将使用昨天的代理列表！")
        url2 = "https://api.checkerproxy.net/v1/landing/archive/%s" % yesterday()
        response = requests.get(url=url2, headers=header)
        ip_json_data = response.json()

        tuple_list = [(ip,) for ip in ip_json_data["data"]["proxyList"]]
        return tuple_list
    else:
        tuple_list = [(ip,) for ip in ip_json_data["data"]["proxyList"]]
        return tuple_list
