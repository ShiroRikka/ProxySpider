import database_control
import proxy as gp
from ProxyTester import *
import convert

dc = database_control

dc.create()
dc.delete_old_ip()
dc.multiple_insert(gp.get_proxy())

dc.create_index()

while True:
    tester = ProxyTester()
    ip_list = tester.test_proxy_list(dc.get_ips_to_test(16),16)
    ip = convert.convert_ip_status_list(ip_list)


    print(ip)


    dc.update_ips_status(ip)
