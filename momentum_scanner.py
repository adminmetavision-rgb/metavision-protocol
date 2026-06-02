#!/usr/bin/env python3
import os, time, requests, threading
from dotenv import load_dotenv
from web3 import Web3
from datetime import datetime

load_dotenv()

MIN_CHANGE_1H  = 8.0
MIN_LIQUIDITY  = 10000
MIN_VOLUME_1H  = 500
MAX_CHANGE_1H  = 200.0
TAKE_PROFIT    = 0.30
STOP_LOSS      = 0.15
BUY_AMOUNT_ETH = 0.003

WETH    = "0x4200000000000000000000000000000000000006"
UNI_V2  = "0x4752ba5DBc23f44D87826276BF6Fd6b1C372aD24"
AERO    = "0xcF77a3Ba9A5CA399B7c97c74d54e5b1Beb874E43"
AERO_FACTORY = "0x420DD381b31aEf6683db6B902084cB0FFECe40Da"

w3  = Web3(Web3.HTTPProvider("https://base-mainnet.g.alchemy.com/v2/RRKWldOIff76bFqkISPGU"))
pk  = os.getenv("PRIVATE_KEY")
acc = Web3.to_checksum_address(os.getenv("WALLET_ADDRESS"))

TG_TOKEN   = "8721989598:AAHvaiUOjyCRKlgkCpGR7_jejiYlACOnt8Q"
TG_CHANNEL = "-1003586688256"

UNI_ABI = [
    {"constant":True,"inputs":[{"name":"amountIn","type":"uint256"},{"name":"path","type":"address[]"}],"name":"getAmountsOut","outputs":[{"name":"amounts","type":"uint256[]"}],"type":"function"},
    {"inputs":[{"name":"amountOutMin","type":"uint256"},{"name":"path","type":"address[]"},{"name":"to","type":"address"},{"name":"deadline","type":"uint256"}],"name":"swapExactETHForTokens","outputs":[{"name":"amounts","type":"uint256[]"}],"stateMutability":"payable","type":"function"},
    {"inputs":[{"name":"amountIn","type":"uint256"},{"name":"amountOutMin","type":"uint256"},{"name":"path","type":"address[]"},{"name":"to","type":"address"},{"name":"deadline","type":"uint256"}],"name":"swapExactTokensForETHSupportingFeeOnTransferTokens","outputs":[],"type":"function"},
]
AERO_ABI = [
    {"inputs":[{"name":"amountIn","type":"uint256"},{"components":[{"name":"from","type":"address"},{"name":"to","type":"address"},{"name":"stable","type":"bool"},{"name":"factory","type":"address"}],"name":"routes","type":"tuple[]"}],"name":"getAmountsOut","outputs":[{"name":"amounts","type":"uint256[]"}],"stateMutability":"view","type":"function"},
    {"inputs":[{"name":"amountOutMin","type":"uint256"},{"components":[{"name":"from","type":"address"},{"name":"to","type":"address"},{"name":"stable","type":"bool"},{"name":"factory","type":"address"}],"name":"routes","type":"tuple[]"},{"name":"to","type":"address"},{"name":"deadline","type":"uint256"}],"name":"swapExactETHForTokens","outputs":[{"name":"amounts","type":"uint256[]"}],"stateMutability":"payable","type":"function"},
    {"inputs":[{"name":"amountIn","type":"uint256"},{"name":"amountOutMin","type":"uint256"},{"components":[{"name":"from","type":"address"},{"name":"to","type":"address"},{"name":"stable","type":"bool"},{"name":"factory","type":"address"}],"name":"routes","type":"tuple[]"},{"name":"to","type":"address"},{"name":"deadline","type":"uint256"}],"name":"swapExactTokensForETHSupportingFeeOnTransferTokens","outputs":[],"type":"function"},
]
ERC20_ABI = [
    {"constant":True,"inputs":[{"name":"_owner","type":"address"}],"name":"balanceOf","outputs":[{"name":"balance","type":"uint256"}],"type":"function"},
    {"constant":False,"inputs":[{"name":"_spender","type":"address"},{"name":"_value","type":"uint256"}],"name":"approve","outputs":[{"name":"","type":"bool"}],"type":"function"},
]

uni_router  = w3.eth.contract(address=Web3.to_checksum_address(UNI_V2), abi=UNI_ABI)
aero_router = w3.eth.contract(address=Web3.to_checksum_address(AERO), abi=AERO_ABI)

positions = {}

def tg(msg):
    try:
        requests.post(f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
            json={"chat_id": TG_CHANNEL, "text": msg, "parse_mode": "Markdown"}, timeout=5)
    except: pass

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def get_base_movers():
    found = []
    try:
        urls = [
            'https://api.geckoterminal.com/api/v2/networks/base/trending_pools?page=1',
            'https://api.geckoterminal.com/api/v2/networks/base/pools?sort=h1_price_change_percentage&page=1',
        ]
        all_pools = []
        for url in urls:
            r = requests.get(url, timeout=10)
            all_pools += r.json().get('data', [])
            time.sleep(0.5)

        seen = set()
        for p in all_pools:
            attr = p.get('attributes', {})
            dex  = p.get('relationships', {}).get('dex', {}).get('data', {}).get('id', '')
            name = attr.get('name', '?')
            change1h = float(attr.get('price_change_percentage', {}).get('h1', 0) or 0)
            vol1h    = float(attr.get('volume_usd', {}).get('h1', 0) or 0)
            liq      = float(attr.get('reserve_in_usd', 0) or 0)

            # Tik palaikomi DEX
            if dex not in ['uniswap-v2-base', 'aerodrome-base']:
                continue

            rel = p.get('relationships', {})
            token_id = rel.get('base_token', {}).get('data', {}).get('id', '')
            token_addr = token_id.split('_')[-1] if '_' in token_id else ''

            if not token_addr or token_addr in seen:
                continue
            if token_addr.lower() == WETH.lower():
                continue
            seen.add(token_addr.lower())

            if (change1h >= MIN_CHANGE_1H and change1h <= MAX_CHANGE_1H and
                liq >= MIN_LIQUIDITY and vol1h >= MIN_VOLUME_1H):
                found.append({
                    'symbol':   name.split('/')[0].strip(),
                    'address':  token_addr,
                    'change1h': change1h,
                    'liq':      liq,
                    'vol1h':    vol1h,
                    'dex':      dex,
                })
    except Exception as e:
        log(f'GeckoTerminal klaida: {e}')

    found.sort(key=lambda x: x['change1h'], reverse=True)
    return found

def buy_token(token_address, dex):
    try:
        token  = Web3.to_checksum_address(token_address)
        amount = w3.to_wei(BUY_AMOUNT_ETH, 'ether')
        deadline = int(time.time()) + 120
        gas_price = int(w3.eth.gas_price * 1.5)
        nonce = w3.eth.get_transaction_count(acc)

        if dex == 'uniswap-v2-base':
            out = uni_router.functions.getAmountsOut(amount, [Web3.to_checksum_address(WETH), token]).call()
            min_out = int(out[1] * 0.85)
            tx = uni_router.functions.swapExactETHForTokens(
                min_out, [Web3.to_checksum_address(WETH), token], acc, deadline
            ).build_transaction({'from':acc,'value':amount,'gas':300000,'gasPrice':gas_price,'nonce':nonce,'chainId':8453})

        elif dex == 'aerodrome-base':
            routes = [{'from': Web3.to_checksum_address(WETH), 'to': token, 'stable': False, 'factory': Web3.to_checksum_address(AERO_FACTORY)}]
            out = aero_router.functions.getAmountsOut(amount, routes).call()
            min_out = int(out[-1] * 0.85)
            tx = aero_router.functions.swapExactETHForTokens(
                min_out, routes, acc, deadline
            ).build_transaction({'from':acc,'value':amount,'gas':400000,'gasPrice':gas_price,'nonce':nonce,'chainId':8453})
        else:
            return False, 'Nežinomas DEX', 0

        signed  = w3.eth.account.sign_transaction(tx, pk)
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)
        if receipt.status == 1:
            token_c = w3.eth.contract(address=token, abi=ERC20_ABI)
            bal = token_c.functions.balanceOf(acc).call()
            return True, w3.to_hex(tx_hash), bal
        return False, w3.to_hex(tx_hash), 0
    except Exception as e:
        return False, str(e), 0

def sell_token(token_address, balance, dex):
    try:
        token   = Web3.to_checksum_address(token_address)
        token_c = w3.eth.contract(address=token, abi=ERC20_ABI)
        nonce   = w3.eth.get_transaction_count(acc)
        approve_tx = token_c.functions.approve(
            Web3.to_checksum_address(AERO if dex == 'aerodrome-base' else UNI_V2), 2**256-1
        ).build_transaction({'from':acc,'gas':100000,'gasPrice':int(w3.eth.gas_price*1.5),'nonce':nonce,'chainId':8453})
        w3.eth.send_raw_transaction(w3.eth.account.sign_transaction(approve_tx, pk).raw_transaction)
        time.sleep(4)

        nonce    = w3.eth.get_transaction_count(acc)
        deadline = int(time.time()) + 120

        if dex == 'uniswap-v2-base':
            sell_tx = uni_router.functions.swapExactTokensForETHSupportingFeeOnTransferTokens(
                balance, 0, [token, Web3.to_checksum_address(WETH)], acc, deadline
            ).build_transaction({'from':acc,'gas':300000,'gasPrice':int(w3.eth.gas_price*1.5),'nonce':nonce,'chainId':8453})
        else:
            routes = [{'from': token, 'to': Web3.to_checksum_address(WETH), 'stable': False, 'factory': Web3.to_checksum_address(AERO_FACTORY)}]
            sell_tx = aero_router.functions.swapExactTokensForETHSupportingFeeOnTransferTokens(
                balance, 0, routes, acc, deadline
            ).build_transaction({'from':acc,'gas':400000,'gasPrice':int(w3.eth.gas_price*1.5),'nonce':nonce,'chainId':8453})

        signed  = w3.eth.account.sign_transaction(sell_tx, pk)
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)
        return receipt.status == 1, w3.to_hex(tx_hash)
    except Exception as e:
        return False, str(e)

def monitor_position(token_address, symbol, buy_wei, dex):
    token   = Web3.to_checksum_address(token_address)
    token_c = w3.eth.contract(address=token, abi=ERC20_ABI)
    tp = buy_wei * (1 + TAKE_PROFIT)
    sl = buy_wei * (1 - STOP_LOSS)

    while token_address in positions:
        try:
            bal = token_c.functions.balanceOf(acc).call()
            if bal == 0:
                break
            if dex == 'uniswap-v2-base':
                out = uni_router.functions.getAmountsOut(bal, [token, Web3.to_checksum_address(WETH)]).call()
                val = out[1]
            else:
                routes = [{'from': token, 'to': Web3.to_checksum_address(WETH), 'stable': False, 'factory': Web3.to_checksum_address(AERO_FACTORY)}]
                out = aero_router.functions.getAmountsOut(bal, routes).call()
                val = out[-1]

            pct = (val - buy_wei) / buy_wei * 100
            log(f"💹 {symbol}: {w3.from_wei(val,'ether'):.5f} ETH ({pct:+.1f}%)")

            if val >= tp:
                log(f"🚀 TP! {symbol} +{pct:.1f}%")
                tg(f"🚀 *TAKE PROFIT* +{pct:.1f}%\n🪙 {symbol}")
                sell_token(token_address, bal, dex)
                break
            elif val <= sl:
                log(f"🩸 SL! {symbol} {pct:.1f}%")
                tg(f"🩸 *STOP LOSS* {pct:.1f}%\n🪙 {symbol}")
                sell_token(token_address, bal, dex)
                break
        except Exception as e:
            log(f"Monitor klaida: {e}")
        time.sleep(5)

    positions.pop(token_address, None)

def main():
    eth_bal = w3.from_wei(w3.eth.get_balance(acc), 'ether')
    log("=" * 55)
    log("📈 METAVISION MOMENTUM SCANNER v2.0")
    log(f"💰 ETH: {eth_bal:.4f} | Buy: {BUY_AMOUNT_ETH} ETH")
    log(f"📈 TP: +{TAKE_PROFIT*100:.0f}% | 📉 SL: -{STOP_LOSS*100:.0f}%")
    log(f"🔍 DEX: Uniswap V2 + Aerodrome")
    log("=" * 55)

    tg(f"📈 *MOMENTUM SCANNER v2.0*\n💰 ETH: {eth_bal:.4f}\n🔍 Uniswap V2 + Aerodrome")

    scan = 0
    while True:
        scan += 1
        log(f"\n🔍 Skenavimas #{scan}...")
        movers = get_base_movers()

        if movers:
            log(f"✅ Rasta {len(movers)} kandidatų:")
            for m in movers[:5]:
                log(f"  {m['symbol']} [{m['dex']}]: +{m['change1h']:.1f}% Vol={m['vol1h']:.0f} Liq={m['liq']:.0f}")

            best = movers[0]
            addr = best['address']

            if addr not in positions and len(positions) < 2:
                eth_b = w3.eth.get_balance(acc)
                if eth_b > w3.to_wei(BUY_AMOUNT_ETH + 0.005, 'ether'):
                    log(f"🔫 PERKAME {best['symbol']} [{best['dex']}] +{best['change1h']:.1f}%")
                    tg(f"🔫 *PERKAME:* {best['symbol']}\n📈 +{best['change1h']:.1f}%\n💧 ${best['liq']:.0f}")
                    ok, tx, bal = buy_token(addr, best['dex'])
                    if ok:
                        positions[addr] = best['symbol']
                        tg(f"✅ *NUPIRKTA:* {best['symbol']}")
                        t = threading.Thread(target=monitor_position,
                            args=(addr, best['symbol'], w3.to_wei(BUY_AMOUNT_ETH,'ether'), best['dex']), daemon=True)
                        t.start()
                    else:
                        log(f"❌ Nepavyko: {tx[:80]}")
                else:
                    log("⚠️ Per mažai ETH")
        else:
            log("Kandidatų nerasta – laukiame...")

        time.sleep(300)

if __name__ == "__main__":
    main()
