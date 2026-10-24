import urllib.request, re

url = 'https://www.usinainfo.com.br/conversores-de-sinal/conversor-de-nivel-logico-33-5v-bidirecional-cnl35-3741.html'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req) as resp:
    html = resp.read().decode('utf-8', errors='ignore')
    name = re.search(r'<h1[^>]*>([^<]+)</h1>', html)
    price = re.search(r'itemprop="price" content="([^"]+)"', html)
    code = re.search(r'Código:\s*<span>([^<]+)</span>', html) or re.search(r'data-id-product="([^"]+)"', html)
    stock = 'indisponivel' if 'indisponivel' in html.lower() else 'em estoque'
    print('Name:', name.group(1).strip() if name else 'N/A')
    print('Price:', price.group(1) if price else 'N/A')
    print('Code:', code.group(1).strip() if code else 'N/A')
    print('Stock:', stock)
