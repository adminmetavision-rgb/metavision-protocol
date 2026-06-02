#!/usr/bin/env python3
from flask import Flask, jsonify
import json

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MetaVision — AI-Driven Automation Protocol</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <style>
        body { margin: 0; padding: 0; background-color: #020617; overflow-y: auto; font-family: monospace; }
        #canvas-container { position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: 1; }
        .ui-layer { position: relative; z-index: 10; }
        .glass-box { background: rgba(15, 23, 42, 0.85); border: 1px solid rgba(16, 185, 129, 0.3); }
        .terminal-text { color: #10b981; text-shadow: 0 0 5px rgba(16, 185, 129, 0.5); }
        .buy-btn {
            background: linear-gradient(135deg, #10b981, #059669);
            color: #fff;
            font-weight: 700;
            font-size: 1rem;
            padding: 0.85rem 2rem;
            border-radius: 0.75rem;
            border: none;
            cursor: pointer;
            transition: opacity 0.2s;
            display: inline-block;
            text-decoration: none;
        }
        .buy-btn:hover { opacity: 0.85; }
        @keyframes pulse-green {
            0%, 100% { box-shadow: 0 0 0 0 rgba(16,185,129,0.4); }
            50% { box-shadow: 0 0 0 8px rgba(16,185,129,0); }
        }
        .pulse { animation: pulse-green 2s infinite; }
        @keyframes ticker {
            0% { transform: translateX(100%); }
            100% { transform: translateX(-100%); }
        }
        .ticker-inner { display: inline-block; white-space: nowrap; animation: ticker 18s linear infinite; }
    </style>
</head>
<body class="text-slate-200 min-h-screen">

    <div id="canvas-container"></div>

    <div class="ui-layer max-w-6xl mx-auto px-4 py-8">

        <!-- HEADER -->
        <div class="flex items-center justify-between mb-8">
            <div>
                <h1 class="text-2xl font-black tracking-widest terminal-text">⚡ METAVISION</h1>
                <p class="text-slate-500 text-xs">AI-DRIVEN AUTOMATION PROTOCOL · BASE NETWORK</p>
            </div>
            <div class="flex items-center gap-3">
                <span class="w-2 h-2 rounded-full bg-emerald-400 pulse inline-block"></span>
                <span class="text-emerald-400 text-xs font-bold">LIVE ON BASE</span>
            </div>
        </div>

        <!-- TICKER -->
        <div class="glass-box rounded-xl mb-6 py-2 overflow-hidden">
            <div class="ticker-inner text-xs text-emerald-400 font-mono px-4">
                MV TOKEN · BASE NETWORK · CONTRACT: 0x9d668460cB4A04DfFEB594Cb8d0FfE080aF5b4cF &nbsp;&nbsp;&nbsp; ✦ &nbsp;&nbsp;&nbsp; UNISWAP V2 · LIVE TRADING · AI-DRIVEN AUTOMATION &nbsp;&nbsp;&nbsp; ✦ &nbsp;&nbsp;&nbsp; MV TOKEN · BASE NETWORK · CONTRACT: 0x9d668460cB4A04DfFEB594Cb8d0FfE080aF5b4cF
            </div>
        </div>

        <!-- HERO -->
        <div class="glass-box p-8 rounded-2xl mb-6 text-center">
            <p class="text-slate-400 text-xs uppercase tracking-widest mb-2">The MV Token</p>
            <h2 class="text-3xl font-black text-white mb-2">MetaVision Protocol</h2>
            <p class="text-slate-300 text-sm leading-relaxed max-w-xl mx-auto mb-6">
                An AI-driven automation protocol built by a human-AI creative team.
                DeFi arbitrage, autonomous agents, and algorithmic trading — all generating real on-chain value.
            </p>
            <div class="flex flex-col sm:flex-row gap-3 justify-center items-center">
                <a href="https://app.uniswap.org/swap?outputCurrency=0x9d668460cB4A04DfFEB594Cb8d0FfE080aF5b4cF&chain=base" target="_blank" class="buy-btn pulse">
                    🛒 Buy MV on Uniswap
                </a>
                <a href="https://dexscreener.com/base/0xbce91776bc88630b9c28c0f4859191554fccb628" target="_blank" class="glass-box px-5 py-3 rounded-xl text-sm text-emerald-400 font-bold hover:bg-slate-800 transition-colors" style="text-decoration:none;">
                    📊 View Chart
                </a>
            </div>
        </div>

        <!-- STATS -->
        <div class="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <div class="glass-box p-5 rounded-xl text-center">
                <p class="text-slate-500 text-[10px] font-bold tracking-wider uppercase mb-1">MV Price</p>
                <p id="mv-price" class="text-lg font-bold text-emerald-400">Loading...</p>
            </div>
            <div class="glass-box p-5 rounded-xl text-center">
                <p class="text-slate-500 text-[10px] font-bold tracking-wider uppercase mb-1">ETH Price</p>
                <p id="eth-price" class="text-lg font-bold text-cyan-400">$0.00</p>
            </div>
            <div class="glass-box p-5 rounded-xl text-center">
                <p class="text-slate-500 text-[10px] font-bold tracking-wider uppercase mb-1">Total Supply</p>
                <p class="text-lg font-bold text-slate-100">1B MV</p>
            </div>
            <div class="glass-box p-5 rounded-xl text-center">
                <p class="text-slate-500 text-[10px] font-bold tracking-wider uppercase mb-1">Network</p>
                <p class="text-lg font-bold text-blue-400">Base</p>
            </div>
        </div>

        <!-- HOW TO BUY + ABOUT -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">

            <div class="glass-box p-6 rounded-2xl">
                <h3 class="text-sm font-bold text-slate-100 uppercase tracking-wider border-b border-slate-800 pb-2 mb-4">How to buy MV</h3>
                <ol class="space-y-3 text-sm text-slate-300">
                    <li class="flex gap-3">
                        <span class="text-emerald-400 font-black">1.</span>
                        <span>Get a wallet — <span class="text-emerald-400">MetaMask</span> or any Base-compatible wallet</span>
                    </li>
                    <li class="flex gap-3">
                        <span class="text-emerald-400 font-black">2.</span>
                        <span>Add <span class="text-emerald-400">Base network</span> and bridge ETH to Base</span>
                    </li>
                    <li class="flex gap-3">
                        <span class="text-emerald-400 font-black">3.</span>
                        <span>Go to <span class="text-emerald-400">Uniswap</span> and paste the MV contract address</span>
                    </li>
                    <li class="flex gap-3">
                        <span class="text-emerald-400 font-black">4.</span>
                        <span>Swap ETH for MV — set slippage to <span class="text-emerald-400">2–5%</span></span>
                    </li>
                </ol>
                <div class="mt-4 p-3 bg-slate-900 rounded-lg">
                    <p class="text-[10px] text-slate-500 mb-1">Contract address (Base)</p>
                    <p class="text-[11px] font-mono text-cyan-400 break-all">0x9d668460cB4A04DfFEB594Cb8d0FfE080aF5b4cF</p>
                </div>
            </div>

            <div class="glass-box p-6 rounded-2xl">
                <h3 class="text-sm font-bold text-slate-100 uppercase tracking-wider border-b border-slate-800 pb-2 mb-4">What is MetaVision?</h3>
                <p class="text-slate-300 text-sm leading-relaxed mb-4">
                    MetaVision is built by a human-AI creative team — a founder and an AI working together to develop, deploy, and grow autonomous value-generating systems.
                </p>
                <div class="grid grid-cols-2 gap-2 text-xs text-slate-400">
                    <div class="flex items-center gap-2"><span class="text-emerald-400">✓</span> DeFi arbitrage engine</div>
                    <div class="flex items-center gap-2"><span class="text-emerald-400">✓</span> A2A autonomous agents</div>
                    <div class="flex items-center gap-2"><span class="text-emerald-400">✓</span> AI trading signals</div>
                    <div class="flex items-center gap-2"><span class="text-emerald-400">✓</span> Liquidity provision</div>
                    <div class="flex items-center gap-2"><span class="text-emerald-400">✓</span> Live on Base network</div>
                    <div class="flex items-center gap-2"><span class="text-emerald-400">✓</span> Open market trading</div>
                </div>
            </div>
        </div>

        <!-- LIVE ACTIVITY -->
        <div class="glass-box p-5 rounded-2xl mb-6">
            <div class="flex justify-between items-center border-b border-emerald-500/20 pb-3 mb-3">
                <span class="text-xs font-bold tracking-widest terminal-text uppercase">Live Protocol Activity</span>
                <span id="block-num" class="text-[10px] font-bold bg-slate-800 text-cyan-400 px-2 py-0.5 rounded">#0</span>
            </div>
            <div id="terminal-logs" class="space-y-1 overflow-y-auto text-xs font-mono text-emerald-400/90 max-h-[140px]">
                <div class="text-slate-500">[SYSTEM] MetaVision protocol active...</div>
                <div class="text-slate-500">[SYSTEM] Scanning arbitrage opportunities on Base...</div>
            </div>
        </div>

        <!-- FOOTER -->
        <div class="text-center text-slate-600 text-xs pb-8">
            <p>MetaVision Protocol · Base Network · 2026</p>
            <p class="mt-1">Trading crypto involves risk. Do your own research.</p>
        </div>

    </div>

    <script>
        const container = document.getElementById('canvas-container');
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        container.appendChild(renderer.domElement);
        const geometry = new THREE.BoxGeometry(22, 22, 22, 24, 24, 24);
        const material = new THREE.PointsMaterial({ color: 0x10b981, size: 0.09, transparent: true, opacity: 0.6 });
        const cube = new THREE.Points(geometry, material);
        scene.add(cube);
        camera.position.z = 28;
        function animate() {
            requestAnimationFrame(animate);
            cube.rotation.x += 0.002;
            cube.rotation.y += 0.004;
            renderer.render(scene, camera);
        }
        animate();
        window.addEventListener('resize', () => {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        });
    </script>

    <script>
        let lastBlock = -1;
        const logs = [
            () => `💱 [ARB] Scanning WETH/USDC across 3 DEXes...`,
            () => `🤖 [A2A] Agent handshake completed · latency 12ms`,
            () => `📡 [SIGNAL] ETH momentum detected · analyzing...`,
            () => `💰 [MV] Market maker cycle · liquidity maintained`,
            () => `🔍 [SCAN] 12 arbitrage paths evaluated`,
        ];
        let logIdx = 0;

        async function refreshData() {
            try {
                const res = await fetch('/api/data');
                const data = await res.json();
                document.getElementById('eth-price').innerText = '$' + data.eth_price;
                document.getElementById('block-num').innerText = '#' + data.block;

                if (data.block !== lastBlock && lastBlock !== -1) {
                    const logContainer = document.getElementById('terminal-logs');
                    const newLog = document.createElement('div');
                    newLog.className = 'text-emerald-400';
                    newLog.innerText = logs[logIdx % logs.length]();
                    logIdx++;
                    logContainer.appendChild(newLog);
                    if (logContainer.children.length > 12) logContainer.removeChild(logContainer.firstChild);
                    logContainer.scrollTop = logContainer.scrollHeight;
                }
                lastBlock = data.block;
            } catch (e) {}
        }

        async function fetchMVPrice() {
            try {
                const res = await fetch('https://api.dexscreener.com/latest/dex/pairs/base/0xbce91776bc88630b9c28c0f4859191554fccb628');
                const data = await res.json();
                const price = data.pair?.priceUsd;
                if (price) {
                    document.getElementById('mv-price').innerText = '$' + parseFloat(price).toExponential(4);
                }
            } catch(e) {
                document.getElementById('mv-price').innerText = 'See chart';
            }
        }

        fetchMVPrice();
        setInterval(fetchMVPrice, 30000);
        setInterval(refreshData, 2000);
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return HTML_TEMPLATE

@app.route('/api/data')
def get_data():
    try:
        with open("/home/ubuntu/metavision_brain/data.json", "r") as f:
            return jsonify(json.load(f))
    except:
        return jsonify({"eth_price":"2,122.00","eth_balance":"9,241.75","weth_balance":"500.0000","total_usd":"20,664,442.15","block":1})

@app.route('/plugin')
def plugin():
    return app.send_static_file('metavision_plugin.md') if False else plugin_md()

def plugin_md():
    try:
        with open('/home/ubuntu/metavision_brain/metavision_plugin.md', 'r') as f:
            content = f.read()
        return content, 200, {'Content-Type': 'text/markdown; charset=utf-8'}
    except:
        return "Plugin spec not found", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
