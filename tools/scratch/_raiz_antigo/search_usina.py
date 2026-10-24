import urllib.request, re

url = 'https://www.usinainfo.com.br/index.php?controller=search&s=conversor+nivel+logico'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req) as resp:
    html = resp.read().decode('utf-8', errors='ignore')
    links = re.findall(r'href="(https://www.usinainfo.com.br/[^"]+)" title="([^"]+)"', html)
    for l, t in set(links):
        if 'conversor' in l.lower() or 'logico' in l.lower():
            print(t, '->', l)
