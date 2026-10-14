import os
import sys
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

profile_dir = os.path.expanduser('~/.robocore_chrome_profile')

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        user_data_dir=profile_dir,
        channel='chrome',
        headless=True
    )
    page = context.pages[0] if context.pages else context.new_page()
    page.goto('https://www.robocore.net/carrinho', timeout=30000)
    page.wait_for_timeout(2000)
    
    # Extract each item row
    rows = page.locator('table tr, .cart-item, div[class*="item"]').all()
    print("=== DADOS DETALHADOS DO CARRINHO ===")
    
    # We can also parse the table directly
    tr_elements = page.locator('tr').all()
    for tr in tr_elements:
        txt = tr.inner_text().strip()
        if 'R$' in txt:
            lines = [l.strip() for l in txt.split('\n') if l.strip()]
            print("ROW:", " | ".join(lines))
            
    # Also extract totals
    for selector in ['.subtotal', '.total', '.carrinho-totais', 'div:has-text("Total no PIX")']:
        try:
            el = page.locator(selector).first
            if el.is_visible():
                print(f"{selector}: {el.inner_text().strip()}")
        except Exception:
            pass
            
    # Get all text with R$ in the whole page
    all_lines = page.locator('body').inner_text().split('\n')
    for l in all_lines:
        if any(w in l.lower() for w in ['subtotal', 'total no pix', 'total', 'em 3x']):
            print("TOTAL LINE:", l.strip())
            
    context.close()
