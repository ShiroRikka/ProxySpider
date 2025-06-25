import requests
from get_url_time import get_url_time
import database_control as dc

header={
    "accept":"*/*",
    "accept-encoding":"gzip, deflate, br, zstd",
    "accept-language":"zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "connection":"keep-alive",
    "host":"api.checkerproxy.net",
    "referer":"https://checkerproxy.net/",
    "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 Edg/137.0.0.0"
}



url = "https://api.checkerproxy.net/v1/landing/archive/%s"%get_url_time()
print(url)

response = requests.get(url=url,headers=header)
print(response.status_code)

ip_json_data = response.json()
print(ip_json_data['data']['proxyList'])











