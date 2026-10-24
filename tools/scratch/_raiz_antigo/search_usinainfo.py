import urllib.request, re

url = "https://www.usinainfo.com.br/busca?s=conversor+de+nivel+logico"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req) as resp:
        content = resp.read().decode('utf-8', errors='ignore')
        products = re.findall(r'<a\s+class="[^"]*product-name[^"]*"\s+href="([^"]+)"\s+title="([^"]+)"', content)
        if not products:
            products = re.findall(r'href="(https://www.usinainfo.com.br/[^"]+)"[^>]*>([^<]*conversor[^<]*)</a>', content, re.I)
        print("Found:", products[:5])
except Exception as e:
    print("Error:", e)
