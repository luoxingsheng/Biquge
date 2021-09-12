import requests


# 调用API获取新的代理
def get_proxy():
    headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",}
    proxy_url = 'http://http1.9vps.com/getip.asp?username=17857096920&pwd=43cd62bcbdea222f5ed240b767709e4e&geshi=1&fenge=5&fengefu=%2C&getnum=1'
    response=requests.get(proxy_url, headers=headers)
    response.encoding = "utf-8"
    result = response.text
    proxy_host = result.strip()
    proxy = {

        'http://': proxy_host,
        'https://': proxy_host,
    }
    return proxy

