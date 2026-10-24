import urllib.request, re

url = 'https://www.usinainfo.com.br/conversores-e-adaptadores/conversor-de-nivel-logico-33v-5v-bidirecional-cnl35-2678.html'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req) as resp:
    html = resp.read().decode('utf-8', errors='ignore')
    price = re.search(r'itemprop="price" content="([^"]+)"', html)
    name = re.search(r'<h1[^>]*>([^<]+)</h1>', html)
    code = re.search(r'itemprop="sku">([^<]+)<', html) or re.search(r'data-id-product="([^"]+)"', html)
    print('Name:', name.group(1).strip() if name else 'N/A')
    print('Price:', price.group(1) if price else 'N/A')
    print('Code:', code.groups() if code else 'N/A')
