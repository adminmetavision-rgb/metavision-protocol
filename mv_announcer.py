#!/usr/bin/env python3
import os, time, requests
from web3 import Web3
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
w3 = Web3(Web3.HTTPProvider(os.getenv('RPC_URL')))

TOKEN      = '8721989598:AAHvaiUOjyCRKlgkCpGR7_jejiYlACOnt8Q'
CHANNEL_ID = '-1003586688256'

MV   = Web3.to_checksum_address('0x9d668460cB4A04DfFEB594Cb8d0FfE080aF5b4cF')
WETH = Web3.to_checksum_address('0x4200000000000000000000000000000000000006')
UNI  = Web3.to_checksum_address('0x4752ba5DBc23f44D87826276BF6Fd6b1C372aD24')

UNI_ABI = [{'constant':True,'inputs':[{'name':'amountIn','type':'uint256'},{'name':'path','type':'address[]'}],'name':'getAmountsOut','outputs':[{'name':'amounts','type':'uint256[]'}],'type':'function'}]

def send(msg):
    try:
        requests.post(f'https://api.telegram.org/bot{TOKEN}/sendMessage', json={
            'chat_id': CHANNEL_ID,
            'text': msg,
            'parse_mode': 'Markdown'
        }, timeout=10)
        print(f'[+] Išsiųsta: {msg[:50]}...')
    except Exception as e:
        print(f'[-] Klaida: {e}')

def get_mv_price():
    try:
        uni = w3.eth.contract(address=UNI, abi=UNI_ABI)
        amount = w3.to_wei(1000000, 'ether')  # 1M MV
        out = uni.functions.getAmountsOut(amount, [MV, WETH]).call()
        weth_per_mv = out[1] / 1e18 / 1000000
        return weth_per_mv
    except:
        return None

def get_eth_price():
    try:
        r = requests.get('https://api.coinbase.com/v2/prices/ETH-USD/spot', timeout=5)
        return float(r.json()['data']['amount'])
    except:
        return None

def get_dex_volume():
    try:
        r = requests.get('https://api.dexscreener.com/latest/dex/pairs/base/0xbce91776bc88630b9c28c0f4859191554fccb628', timeout=10)
        data = r.json()
        pair = data.get('pair', {})
        volume = pair.get('volume', {}).get('h24', 0)
        price_usd = pair.get('priceUsd', '0')
        txns = pair.get('txns', {}).get('h24', {})
        buys = txns.get('buys', 0)
        sells = txns.get('sells', 0)
        return float(volume), float(price_usd), buys, sells
    except:
        return None, None, None, None

def send_hourly_update():
    eth_price = get_eth_price()
    mv_price_weth = get_mv_price()
    volume, price_usd, buys, sells = get_dex_volume()

    if mv_price_weth and eth_price:
        mv_price_usd = mv_price_weth * eth_price
    elif price_usd:
        mv_price_usd = price_usd
    else:
        mv_price_usd = 0

    msg = (
        f"📊 *METAVISION — Hourly Update*\n\n"
        f"🪙 *MV Price:* ${mv_price_usd:.10f}\n"
        f"💎 *ETH Price:* ${eth_price:,.2f}\n"
        f"📈 *24h Volume:* ${volume or 0:,.2f}\n"
        f"🟢 Buys: {buys} | 🔴 Sells: {sells}\n\n"
        f"🔗 [Buy MV](https://app.uniswap.org/swap?outputCurrency=0x9d668460cB4A04DfFEB594Cb8d0FfE080aF5b4cF&chain=base) | "
        f"[Chart](https://dexscreener.com/base/0xbce91776bc88630b9c28c0f4859191554fccb628) | "
        f"[Website](https://metavision.click)\n\n"
        f"_Updated: {datetime.now().strftime('%H:%M UTC')}_"
    )
    send(msg)

def main():
    print('🚀 MV Announcer paleistas')

    # Pirma žinutė iš karto
    send(
        "🚀 *METAVISION PROTOCOL — LIVE*\n\n"
        "MetaVision is an AI-driven automation protocol on Base network.\n\n"
        "🤖 DeFi arbitrage engine — active\n"
        "💱 Market making — active\n"
        "🧠 Human-AI development team\n\n"
        "🔗 [Buy MV on Uniswap](https://app.uniswap.org/swap?outputCurrency=0x9d668460cB4A04DfFEB594Cb8d0FfE080aF5b4cF&chain=base)\n"
        "📊 [Live Chart](https://dexscreener.com/base/0xbce91776bc88630b9c28c0f4859191554fccb628)\n"
        "🌐 [Website](https://metavision.click)\n\n"
        "Contract: `0x9d668460cB4A04DfFEB594Cb8d0FfE080aF5b4cF`"
    )

    last_hour = -1

    while True:
        current_hour = datetime.now().hour
        if current_hour != last_hour:
            send_hourly_update()
            last_hour = current_hour
        time.sleep(60)

if __name__ == '__main__':
    main()
