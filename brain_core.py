#!/usr/bin/env python3
import os, time, json, logging, threading, requests
from collections import deque
from datetime import datetime
from flask import Flask, jsonify, request
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
log = logging.getLogger("METAVISION_BRAIN")

app = Flask(__name__)
w3 = Web3(Web3.HTTPProvider(os.getenv("BASE_RPC")))
account = w3.eth.account.from_key(os.getenv("PRIVATE_KEY"))
price_history = deque(maxlen=40)

MV   = Web3.to_checksum_address("0x9d668460cB4A04DfFEB594Cb8d0FfE080aF5b4cF")
WETH = Web3.to_checksum_address("0x4200000000000000000000000000000000000006")
UNI  = Web3.to_checksum_address("0x4752ba5DBc23f44D87826276BF6Fd6b1C372aD24")
UNI_ABI = [{"constant":True,"inputs":[{"name":"amountIn","type":"uint256"},{"name":"path","type":"address[]"}],"name":"getAmountsOut","outputs":[{"name":"amounts","type":"uint256[]"}],"type":"function"}]

def get_state_from_main():
    try:
        with open("/home/ubuntu/metavision_core/bot_state.json", "r") as f:
            return json.load(f)
    except:
        return {"current_price": 2130, "position": "WETH", "last_signal": "HOLD"}

def get_mv_price():
    try:
        uni = w3.eth.contract(address=UNI, abi=UNI_ABI)
        out = uni.functions.getAmountsOut(w3.to_wei(1000000, 'ether'), [MV, WETH]).call()
        weth_per_mv = out[1] / 1e18 / 1000000
        eth_price = get_eth_price()
        return {
            "weth": weth_per_mv,
            "usd": weth_per_mv * eth_price if eth_price else 0,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"weth": 0, "usd": 0, "error": str(e)}

def get_eth_price():
    try:
        r = requests.get("https://api.coinbase.com/v2/prices/ETH-USD/spot", timeout=5)
        return float(r.json()["data"]["amount"])
    except:
        return None

def get_momentum_signal():
    state = get_state_from_main()
    price = state.get("current_price", 2130)
    price_history.append(price)
    if len(price_history) < 10:
        return "HOLD"
    short = sum(list(price_history)[-5:]) / 5
    long  = sum(list(price_history)[-15:-5]) / 10
    change = (short - long) / long
    if change > 0.009:
        return "BUY"
    elif change < -0.009:
        return "SELL"
    return "HOLD"

def get_dex_stats():
    try:
        r = requests.get("https://api.dexscreener.com/latest/dex/pairs/base/0xbce91776bc88630b9c28c0f4859191554fccb628", timeout=10)
        pair = r.json().get("pair", {})
        return {
            "volume_24h": pair.get("volume", {}).get("h24", 0),
            "price_usd":  pair.get("priceUsd", "0"),
            "liquidity":  pair.get("liquidity", {}).get("usd", 0),
            "txns_24h":   pair.get("txns", {}).get("h24", {}),
        }
    except:
        return {}

# ============================================================
# A2A ENDPOINTS
# ============================================================

@app.route('/agent-card')
def agent_card():
    state = get_state_from_main()
    return jsonify({
        "name": "Metavision Brain v9.0 A2A",
        "address": account.address,
        "status": "active",
        "version": "9.0",
        "capabilities": ["price-oracle", "trading-signal", "arbitrage-monitor", "mv-token", "a2a", "base"],
        "description": "MetaVision A2A Protocol — AI-driven automation on Base network",
        "endpoints": {
            "price":     "/price",
            "signal":    "/signal",
            "arbitrage": "/arbitrage",
            "execute":   "/execute",
            "stats":     "/stats",
            "agent_card":"/agent-card"
        },
        "token": {
            "symbol":   "MV",
            "contract": "0x9d668460cB4A04DfFEB594Cb8d0FfE080aF5b4cF",
            "network":  "Base",
            "dex":      "Uniswap V2"
        },
        "last_update": datetime.now().strftime("%H:%M:%S")
    })

@app.route('/price')
def price_endpoint():
    """MV Price Oracle – grąžina realią MV kainą"""
    mv = get_mv_price()
    eth = get_eth_price()
    return jsonify({
        "token": "MV",
        "network": "Base",
        "price_weth": mv["weth"],
        "price_usd":  mv["usd"],
        "eth_usd":    eth,
        "contract":   "0x9d668460cB4A04DfFEB594Cb8d0FfE080aF5b4cF",
        "source":     "Uniswap V2",
        "timestamp":  datetime.now().isoformat()
    })

@app.route('/signal')
def signal_endpoint():
    """Trading Signal – grąžina BUY/SELL/HOLD signalą"""
    signal = get_momentum_signal()
    state  = get_state_from_main()
    eth_price = get_eth_price()
    return jsonify({
        "signal":    signal,
        "eth_price": eth_price,
        "reasoning": "momentum-based MA crossover",
        "confidence": "medium",
        "timestamp": datetime.now().isoformat(),
        "action": {
            "BUY":  "ETH momentum positive – consider buying MV",
            "SELL": "ETH momentum negative – consider selling MV",
            "HOLD": "No clear signal – hold position"
        }.get(signal, "HOLD")
    })

@app.route('/arbitrage')
def arbitrage_endpoint():
    """Arbitrage Monitor – grąžina paskutines arbitražo galimybes"""
    try:
        with open("/home/ubuntu/metavision_arbitrage/defi.out", "r") as f:
            lines = f.readlines()[-20:]
        last_scan = [l.strip() for l in lines if "Geriausia" in l]
        last_top  = [l.strip() for l in lines if "TOP" in l or "->" in l]
        return jsonify({
            "status": "scanning",
            "last_scans": last_scan[-5:],
            "top_opportunities": last_top[-5:],
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)})

@app.route('/stats')
def stats_endpoint():
    """Protocol Stats – bendra protokolo statistika"""
    dex = get_dex_stats()
    mv  = get_mv_price()
    eth_bal = w3.eth.get_balance(account.address)
    return jsonify({
        "protocol": "MetaVision",
        "network":  "Base",
        "token": {
            "symbol":     "MV",
            "price_usd":  mv["usd"],
            "price_weth": mv["weth"],
            "volume_24h": dex.get("volume_24h", 0),
            "liquidity":  dex.get("liquidity", 0),
        },
        "wallet": {
            "address": account.address,
            "eth_balance": float(w3.from_wei(eth_bal, 'ether'))
        },
        "links": {
            "website":    "https://metavision.click",
            "dexscreener":"https://dexscreener.com/base/0xbce91776bc88630b9c28c0f4859191554fccb628",
            "telegram":   "https://t.me/MetaVisionMV"
        },
        "timestamp": datetime.now().isoformat()
    })

@app.route('/execute', methods=['POST'])
def execute_endpoint():
    """Cross-agent Task Execution – priima užduotis iš kitų agentų"""
    try:
        data = request.get_json()
        task = data.get("task", "")
        agent = data.get("agent", "unknown")
        log.info(f"📨 A2A užduotis gauta nuo [{agent}]: {task}")

        if task == "get_price":
            return jsonify({"result": get_mv_price(), "status": "ok"})
        elif task == "get_signal":
            return jsonify({"result": get_momentum_signal(), "status": "ok"})
        elif task == "get_stats":
            return jsonify({"result": get_dex_stats(), "status": "ok"})
        else:
            return jsonify({"status": "unknown_task", "task": task})
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)})

@app.route('/api/data')
def api_data():
    try:
        with open("/home/ubuntu/metavision_core/bot_state.json", "r") as f:
            return jsonify(json.load(f))
    except:
        return jsonify({"current_price": 2135, "last_signal": "HOLD"})

def trading_loop():
    while True:
        try:
            signal = get_momentum_signal()
            if signal != "HOLD":
                log.warning(f"🔴 BRAIN → {signal} SIGNAL")
            time.sleep(12)
        except Exception as e:
            log.error(f"Brain error: {e}")
            time.sleep(10)


# ============================================================
# BASE MCP PLUGIN ENDPOINTS
# ============================================================

@app.route('/mv/state/<address>')
def mv_state(address):
    """Read endpoint – grąžina MV balansą ir kainą"""
    try:
        erc20_abi = [{"constant":True,"inputs":[{"name":"_owner","type":"address"}],"name":"balanceOf","outputs":[{"name":"balance","type":"uint256"}],"type":"function"}]
        mv_contract = w3.eth.contract(address=MV, abi=erc20_abi)
        mv_balance = mv_contract.functions.balanceOf(Web3.to_checksum_address(address)).call()
        eth_balance = w3.eth.get_balance(Web3.to_checksum_address(address))
        mv_price = get_mv_price()
        return jsonify({
            "address": address,
            "mv_balance": str(mv_balance),
            "mv_balance_human": mv_balance / 1e18,
            "eth_balance": str(eth_balance),
            "eth_balance_human": float(w3.from_wei(eth_balance, 'ether')),
            "mv_price_usd": mv_price["usd"],
            "mv_price_weth": mv_price["weth"],
            "contract": "0x9d668460cB4A04DfFEB594Cb8d0FfE080aF5b4cF",
            "network": "Base",
            "chainId": 8453
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/mv/prepare/buy')
def mv_prepare_buy():
    """Prepare endpoint – grąžina unsigned calldata MV pirkimui"""
    try:
        from_addr = request.args.get('from')
        amount_eth = request.args.get('amount', '0.001')

        if not from_addr:
            return jsonify({"error": "from parameter required"}), 400

        amount_wei = w3.to_wei(float(amount_eth), 'ether')
        amount_hex = hex(amount_wei)

        # Uniswap V2 swapExactETHForTokens calldata
        # swapExactETHForTokens(uint amountOutMin, address[] path, address to, uint deadline)
        import time
        deadline = int(time.time()) + 300
        deadline_hex = hex(deadline)

        # Encode function call
        router_abi = [{"inputs":[{"name":"amountOutMin","type":"uint256"},{"name":"path","type":"address[]"},{"name":"to","type":"address"},{"name":"deadline","type":"uint256"}],"name":"swapExactETHForTokens","outputs":[{"name":"amounts","type":"uint256[]"}],"stateMutability":"payable","type":"function"}]
        router_contract = w3.eth.contract(address=ROUTER, abi=router_abi)

        calldata = router_contract.encodeABI(
            fn_name="swapExactETHForTokens",
            args=[0, [WETH, MV], Web3.to_checksum_address(from_addr), deadline]
        )

        return jsonify({
            "ok": True,
            "action": "buy_mv",
            "amount_eth": float(amount_eth),
            "data": {
                "to": ROUTER,
                "value": amount_hex,
                "data": calldata,
                "chainId": 8453
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/mv/prepare/sell')
def mv_prepare_sell():
    """Prepare endpoint – grąžina unsigned calldata MV pardavimui"""
    try:
        from_addr = request.args.get('from')
        amount_mv = request.args.get('amount')

        if not from_addr:
            return jsonify({"error": "from parameter required"}), 400

        # Jei amount nenurodytas – parduodame viską
        if not amount_mv:
            erc20_abi = [{"constant":True,"inputs":[{"name":"_owner","type":"address"}],"name":"balanceOf","outputs":[{"name":"balance","type":"uint256"}],"type":"function"}]
            mv_contract = w3.eth.contract(address=MV, abi=erc20_abi)
            amount_wei = mv_contract.functions.balanceOf(Web3.to_checksum_address(from_addr)).call()
        else:
            amount_wei = int(float(amount_mv) * 1e18)

        import time
        deadline = int(time.time()) + 300
        max_uint = 2**256 - 1

        # Approve calldata
        erc20_abi2 = [{"inputs":[{"name":"spender","type":"address"},{"name":"amount","type":"uint256"}],"name":"approve","outputs":[{"name":"","type":"bool"}],"type":"function"}]
        mv_contract2 = w3.eth.contract(address=MV, abi=erc20_abi2)
        approve_data = mv_contract2.encodeABI(fn_name="approve", args=[ROUTER, max_uint])

        # Sell calldata
        router_abi = [{"inputs":[{"name":"amountIn","type":"uint256"},{"name":"amountOutMin","type":"uint256"},{"name":"path","type":"address[]"},{"name":"to","type":"address"},{"name":"deadline","type":"uint256"}],"name":"swapExactTokensForETHSupportingFeeOnTransferTokens","outputs":[],"type":"function"}]
        router_contract = w3.eth.contract(address=ROUTER, abi=router_abi)
        sell_data = router_contract.encodeABI(
            fn_name="swapExactTokensForETHSupportingFeeOnTransferTokens",
            args=[amount_wei, 0, [MV, WETH], Web3.to_checksum_address(from_addr), deadline]
        )

        return jsonify({
            "ok": True,
            "action": "sell_mv",
            "amount_mv": amount_wei / 1e18,
            "transactions": [
                {"step": "approve", "to": MV, "value": "0x0", "data": approve_data, "chainId": 8453},
                {"step": "sell",    "to": ROUTER, "value": "0x0", "data": sell_data, "chainId": 8453}
            ]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    log.info("✅ METAVISION BRAIN v9.0 A2A STARTED")
    log.info("📡 Endpoints: /agent-card /price /signal /arbitrage /stats /execute /mv/state /mv/prepare/buy /mv/prepare/sell")
    threading.Thread(target=trading_loop, daemon=True).start()
    app.run(host="0.0.0.0", port=8081, debug=False)
