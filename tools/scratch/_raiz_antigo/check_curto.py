import urllib.request, re

url = 'https://curtocircuito.com.br/modulo-decodificador-dac-3w-max98357.html'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
        price = re.search(r'data-price-amount="([^"]+)"', html) or re.search(r'"price":\s*"([^"]+)"', html)
        stock = 'Em estoque' if 'in-stock' in html or 'Disponível' in html else 'Indisponível'
        print('Price:', price.group(1) if price else 'N/A')
        print('Stock:', stock)
except Exception as e:
    print('Err:', e)
