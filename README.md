# metavision-protocol
AI-driven automation protocol on Base network. DeFi arbitrage, momentum trading, A2A agents, and Base MCP plugin.
# MetaVision Protocol

> AI-driven automation protocol on Base network, built by a human-AI development team.

[![Live](https://img.shields.io/badge/Status-Live-green)](https://metavision.click)
[![Network](https://img.shields.io/badge/Network-Base-blue)](https://base.org)
[![Token](https://img.shields.io/badge/Token-MV-purple)](https://dexscreener.com/base/0xbce91776bc88630b9c28c0f4859191554fccb628)

## Overview

MetaVision is an autonomous DeFi protocol and agent network running live on Base mainnet. Built by a single founder working in close collaboration with AI — demonstrating that a human-AI creative team can build and deploy functional financial infrastructure.

## Live Systems

| System | Status | Description |
|--------|--------|-------------|
| MV Token | ✅ Live | Base mainnet, Uniswap V2 |
| A2A Protocol | ✅ Live | Agent-to-agent API on port 8081 |
| Momentum Scanner | ✅ Active | GeckoTerminal-based trading signals |
| Telegram Bot | ✅ Active | @MetaVisionMV auto-announcements |
| Web Interface | ✅ Live | metavision.click |
| Base MCP Plugin | ✅ Live | metavision.click/plugin |

## MV Token

- **Contract:** `0x9d668460cB4A04DfFEB594Cb8d0FfE080aF5b4cF`
- **Network:** Base mainnet
- **DEX:** Uniswap V2
- **Chart:** [DexScreener](https://dexscreener.com/base/0xbce91776bc88630b9c28c0f4859191554fccb628)

## A2A Protocol Endpoints
GET /agent-card    — Agent discovery card
GET /price         — MV token price oracle
GET /signal        — ETH trading signal (BUY/SELL/HOLD)
GET /stats         — Protocol statistics
GET /arbitrage     — Arbitrage opportunities
POST /execute      — Cross-agent task execution
GET /mv/state/:address    — MV balance and price
GET /mv/prepare/buy       — Buy MV unsigned calldata
GET /mv/prepare/sell      — Sell MV unsigned calldata
## Base MCP Plugin

MetaVision is integrated with Base MCP ecosystem. Skill plugin available at:
## Base MCP Plugin

https://metavision.click/plugin
Any Claude or ChatGPT agent can buy/sell MV tokens using this plugin.

## Tech Stack

- **Backend:** Python, Flask, Web3.py
- **Infrastructure:** AWS EC2, Ubuntu 24
- **Blockchain:** Base mainnet, Uniswap V2, Aerodrome
- **AI:** Claude API, A2A Protocol
- **Monitoring:** GeckoTerminal API, DexScreener API

## Links

- 🌐 Website: [metavision.click](https://metavision.click)
- 📊 Chart: [DexScreener](https://dexscreener.com/base/0xbce91776bc88630b9c28c0f4859191554fccb628)
- 💬 Telegram: [@MetaVisionMV](https://t.me/MetaVisionMV)
- 🤖 A2A Catalog: [View Agent](https://a2acatalog.com)

## License

MIT

