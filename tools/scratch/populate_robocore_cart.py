import os
import sys
import time
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

ITEMS_TO_ADD = [
    {
        "id_name": "servos",
        "name": "Micro Servo 9g SG90",
        "url": "https://www.robocore.net/atuador/micro-servo-9g-sg90-towerpro",
        "quantity": 2,
        "role": "Mecânica Pan & Tilt (Movimentação horizontal e vertical da câmera)"
    },
    {
        "id_name": "pan_tilt",
        "name": "Suporte Pan/Tilt para Câmera Raspberry Pi",
        "url": "https://www.robocore.net/item-mecanico/suporte-pan-tilt-para-camera-raspberry-pi",
        "quantity": 1,
        "role": "Suporte articulado 2 eixos para os servos SG90"
    },
    {
        "id_name": "motors",
        "name": "Micro Motor com Caixa de Redução 6V 100RPM – Low Power",
        "url": "https://www.robocore.net/motor-caixas-de-reducao/micro-motor-com-caixa-de-reducao-6v-100rpm",
        "quantity": 4,
        "role": "4 Micromotores de tração com redução de metal e eixo D 3mm"
    },
    {
        "id_name": "wheels",
        "name": "StickyMAX - Roda S20 Macia - 22mm",
        "url": "https://www.robocore.net/roda/roda-stickymax-s20-22mm",
        "quantity": 4,
        "role": "4 Rodas de silicone/borracha de alta aderência com cubo de 3mm"
    },
    {
        "id_name": "motor_brackets",
        "name": "Suporte para Micro Motores (par branco)",
        "url": "https://www.robocore.net/item-mecanico/suporte-para-micro-motores",
        "quantity": 2, # 2 pares = 4 suportes
        "role": "2 Pares de suportes de fixação em L para os 4 micromotores"
    },
    {
        "id_name": "driver",
        "name": "Módulo Driver Ponte H - L298N",
        "url": "https://www.robocore.net/driver-motor/driver-motor-ponte-h-l298n",
        "quantity": 1,
        "role": "Driver Ponte H para controle de sentido e velocidade (PWM) dos 4 motores"
    },
    {
        "id_name": "step_down",
        "name": "Conversor DC/DC Step Down Mini 560 5V",
        "url": "https://www.robocore.net/regulador-de-tensao/conversor-dc-dc-step-down-mini-560-5v",
        "quantity": 1,
        "role": "Regulador Step-Down para alimentar ESP32 e Servos com 5.0V estáveis (até 5A)"
    },
    {
        "id_name": "battery",
        "name": "Pack de Bateria Li-Ion 7,4V 2500mAh com BMS",
        "url": "https://www.robocore.net/baterias-fontes/pack-bateria-li-ion-7_4v-2500mah-com-bms",
        "quantity": 1,
        "role": "Bateria 2S 18650 Li-Ion com circuito BMS de proteção integrado"
    },
    {
        "id_name": "jst_cable",
        "name": "Cabo JST-RCY 2 pinos fêmea",
        "url": "https://www.robocore.net/cabo/cabo-jst-rcy-2-pinos-femea",
        "quantity": 1,
        "role": "Rabicho conector fêmea para ligação da bateria à chave e regulador"
    },
    {
        "id_name": "buzzer",
        "name": "Módulo Buzzer 5V Passivo",
        "url": "https://www.robocore.net/atuador/modulo-buzzer-5v-passivo",
        "quantity": 1,
        "role": "Módulo buzzer sonoro para bips e alertas via PWM"
    },
    {
        "id_name": "leds",
        "name": "Módulo WS2812 LED RGB Endereçável – 8 LEDs",
        "url": "https://www.robocore.net/led/modulo-ws2812-led-enderecavel-8-leds",
        "quantity": 1,
        "role": "Barra de 8 LEDs RGB endereçáveis usando 1 único GPIO"
    },
    {
        "id_name": "switch",
        "name": "Chave Gangorra KCD1-101 2T",
        "url": "https://www.robocore.net/botao-chave/chave-gangorra-kcd1-101-2t",
        "quantity": 1,
        "role": "Chave geral Liga/Desliga para o robô"
    },
    {
        "id_name": "jumpers_ff",
        "name": "Jumpers Fêmea-Fêmea x40 Unidades",
        "url": "https://www.robocore.net/cabo/jumpers-femea-femea-x40-unidades",
        "quantity": 1,
        "role": "Fios de conexão para ESP32 e módulos"
    },
    {
        "id_name": "jumpers_mm",
        "name": "Jumpers Macho-Macho x40 Cabos",
        "url": "https://www.robocore.net/cabo/jumpers-macho-macho-x40-cabos",
        "quantity": 1,
        "role": "Fios de conexão adicionais para protoboard/bornes"
    }
]

def build_cart(profile_dir):
    print("=" * 60)
    print("🤖 INICIANDO MONTAGEM DO CARRINHO NA ROBOCORE VIA PYTHON")
    print(f"Diretório de perfil Chrome: {profile_dir}")
    print("=" * 60)
    
    with sync_playwright() as p:
        # Launch persistent context so session and cart cookies are saved
        context = p.chromium.launch_persistent_context(
            user_data_dir=profile_dir,
            channel='chrome',
            headless=True,
            args=['--start-maximized']
        )
        page = context.pages[0] if context.pages else context.new_page()
        
        # 1. First visit cart to see current state
        print("\n[1/3] Acessando carrinho inicial...")
        page.goto('https://www.robocore.net/carrinho', timeout=30000)
        page.wait_for_timeout(2000)
        
        # Check if cart already has items and empty if necessary or leave it
        # Let's see if there are delete buttons
        del_btns = page.locator('a[href*="carrinho/remover"], a[href*="remover"], .btn-remover, button:has-text("Remover")').all()
        if del_btns:
            print(f"Limpando {len(del_btns)} itens existentes do carrinho de testes...")
            for b in del_btns:
                try:
                    b.click()
                    page.wait_for_timeout(1000)
                except Exception:
                    pass
            page.goto('https://www.robocore.net/carrinho', timeout=30000)
            page.wait_for_timeout(1500)
            
        # 2. Add each item
        print("\n[2/3] Adicionando itens ao carrinho...")
        added_summary = []
        for i, item in enumerate(ITEMS_TO_ADD, 1):
            print(f"  ({i}/{len(ITEMS_TO_ADD)}) Adicionando: {item['name']} (Qtd: {item['quantity']})...")
            try:
                page.goto(item['url'], timeout=30000)
                page.wait_for_timeout(1500)
                
                # Check for quantity input
                qty_input = page.locator('input[name="quantidade"]')
                if qty_input.is_visible():
                    qty_input.fill(str(item['quantity']))
                
                # Click comprar button
                comprar_btn = page.locator('form[action="/carrinho"] button[type="submit"], button:has-text("COMPRAR"), input[value="COMPRAR"]')
                if comprar_btn.is_visible():
                    comprar_btn.first.click()
                    page.wait_for_timeout(2500)
                    print(f"      ✅ Sucesso! URL atual: {page.url}")
                    added_summary.append({**item, "status": "OK"})
                else:
                    print(f"      ❌ Botão comprar não encontrado para {item['name']}")
                    added_summary.append({**item, "status": "ERRO: Botão não encontrado"})
            except Exception as e:
                print(f"      ❌ Erro ao adicionar {item['name']}: {e}")
                added_summary.append({**item, "status": f"ERRO: {e}"})
                
        # 3. Final Cart Inspection
        print("\n[3/3] Inspecionando carrinho final...")
        page.goto('https://www.robocore.net/carrinho', timeout=30000)
        page.wait_for_timeout(3000)
        
        screenshot_path = "C:/Users/caihe/.gemini/antigravity-ide/brain/ca950029-71e7-4b50-aee1-a3b78060ade8/carrinho_robocore.png"
        page.screenshot(path=screenshot_path, full_page=True)
        print(f"📸 Screenshot do carrinho salva em: {screenshot_path}")
        
        # Extract cart items from DOM
        text = page.locator('body').inner_text()
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        
        cart_info = []
        for l in lines:
            if any(k in l.lower() for k in ['subtotal', 'total no pix', 'total']):
                cart_info.append(l)
                
        print("\n" + "=" * 60)
        print("RESUMO DO CARRINHO ROBOCORE:")
        for ci in cart_info:
            print("  ", ci)
        print("=" * 60)
        
        context.close()
        return added_summary

if __name__ == '__main__':
    profile_dir = os.path.expanduser('~/.robocore_chrome_profile')
    build_cart(profile_dir)
