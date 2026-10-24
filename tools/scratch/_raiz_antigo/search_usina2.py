import urllib.request, re

url = 'https://www.usinainfo.com.br/busca?s=conversor'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
        matches = re.findall(r'<a[^>]+class="[^"]*product-title[^"]*"[^>]*href="([^"]+)"[^>]*>([^<]+)</a>', html)
        if not matches:
            matches = re.findall(r'<a[^>]+href="(https://www.usinainfo.com.br/[^"]+)"[^>]*>([^<]+)</a>', html)
        for m in matches[:10]:
            print(m)
except Exception as e:
    print('Error:', e)
