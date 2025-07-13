import proxy as gp
from ProxyTester import ProxyTester
import time
import convert
from database_control import ProxyDB
from loguru import logger

dc = ProxyDB()
dc.create()
dc.delete_old_ip()
dc.multiple_insert(gp.get_proxy())
time.sleep(2)
dc.delete_duplicate_ips()
time.sleep(2)
dc.create_index()
tester = ProxyTester()

while True:
    if dc.ip_count() > 0:
        ip_list = []
        for ip in dc.get_new_ips_from_db(500):
            ip = f"http://{ip}"
            ip_list.append(ip)
        ip_for_test = ",".join(ip_list)
        logger.info("当前测试的是低分代理")
    else:
        ip_list = []
        for ip in dc.get_best_ips_from_db(500):
            ip = f"http://{ip}"
            ip_list.append(ip)
        ip_for_test = ",".join(ip_list)
        logger.info("当前测试的是高分代理")
        ip_info = convert.convert_ip_info(tester.test_proxy_list(ip_for_test, 500))
        dc.update_ips_status(ip_info)
        time.sleep(2)
        dc.output_proxies_to_txt()
        time.sleep(300)
        continue

    ip_info = convert.convert_ip_info(tester.test_proxy_list(ip_for_test, 500))
    dc.update_ips_status(ip_info)
    time.sleep(2)
