import database_control as dc
import proxy as gp
from ProxyTester import *
import convert

dc.create()
dc.delete_old_ip()
dc.multiple_insert(gp.get_proxy())
dc.delete_duplicate_ips()

dc.create_index()
tester = ProxyTester()

while True:

    if dc.count_low_score_proxies() > 0 :
        ip_list = tester.test_proxy_list(dc.get_ips_to_test(16), 16)
    else:
        ip_list = tester.test_proxy_list(dc.get_best_ips_to_test(16), 16)


    ip = convert.convert_ip_status_list(ip_list)

    dc.update_ips_status(ip)
    time.sleep(2)
