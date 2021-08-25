from proxies import proxy_list
import random
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium import common, webdriver


used_proxies = []

def draw_proxy(proxy_list: list) -> str:
    """
    Function draws single proxy from delivered proxy list if proxy isn't
    currently used by other worker
    :param proxy_list: List containing proxy server IP's
    :return: Single string containing one proxy IP
    """
    proxy = proxy_list[random.randint(0, len(proxy_list) - 1)]
    if proxy not in used_proxies:
        used_proxies.append(proxy)
    else:
        while proxy in used_proxies:
            if len(used_proxies) == len(proxy_list):
                logging.critical("All proxied are used right now")
                break
            proxy = proxy_list[random.randint(0, len(proxy_list) - 1)]
    return proxy

firefox_options = webdriver.FirefoxOptions
proxy = dict(draw_proxy(proxy_list))
print('whats goin on')
prox = Proxy()
prox.proxy_type = ProxyType.MANUAL
print(proxy['proxy']['http'][34:-5])
print(proxy['proxy']['http'][-4:])
