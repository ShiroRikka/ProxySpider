import database_control as dc
import proxy as gp
from ProxyTester import *
import convert

dc.create()
dc.delete_old_ip()
dc.multiple_insert(gp.get_proxy())

dc.create_index()
tester = ProxyTester()

while True:
    dc.delete_duplicate_ips()
    if dc.count_low_score_proxies() > 0 :
        ip_list = tester.test_proxy_list(dc.get_ips_to_test(16), 16)
        print(f"当前测试的是低分代理")
    else:
        ip_list = tester.test_proxy_list(dc.get_best_ips_to_test(16), 16)
        print(f"当前测试的是高分代理")


    ip = convert.convert_ip_status_list(ip_list)

    dc.update_ips_status(ip)
    time.sleep(2)
