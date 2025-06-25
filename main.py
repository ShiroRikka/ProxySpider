import database_control
import proxy as gp
import ProxyTester
from ProxyTester import *
import convert

dc = database_control.DatabaseControl()

dc.create()

dc.multiple_insert(gp.get_proxy())

dc.create_index()
#
# test_proxy_connectivity(dc.get_ips_to_test())
while(True):
    tester = ProxyTester(timeout=10)
    ip_list = tester.test_proxy_list(dc.get_ips_to_test())
    ip = convert.convert_ip_status_list(ip_list)


    print(ip)


    dc.update_ips_status(ip)
