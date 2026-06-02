# MetaVision MV Token Plugin

> [!IMPORTANT]
> ## STOP — COMPLETE ONBOARDING BEFORE USING THIS PLUGIN
>
> Before calling any MetaVision endpoint, you MUST complete the Base MCP onboarding flow:
> 1. Call `get_wallets` (Detection)
> 2. Present wallet status and disclaimer (Onboarding)

MetaVision is an AI-driven automation protocol on Base network. Fetch unsigned calldata from the MetaVision API, then execute via Base MCP send_calls.

**API base:** http://13.48.136.59:8081

**Supported chain:** Base mainnet (8453)

## Read endpoints

GET http://13.48.136.59:8081/mv/state/<wallet_address>
GET http://13.48.136.59:8081/price
GET http://13.48.136.59:8081/signal

## Prepare buy MV

GET http://13.48.136.59:8081/mv/prepare/buy?from=<address>&amount=<eth>

Response: { "ok": true, "data": { "to": "0x...", "value": "0x...", "data": "0x...", "chainId": 8453 } }

## Prepare sell MV

GET http://13.48.136.59:8081/mv/prepare/sell?from=<address>&amount=<mv>

Response: { "ok": true, "transactions": [ { "step": "approve", ... }, { "step": "sell", ... } ] }

## send_calls mapping

Buy: { "chain": "base", "calls": [{ "to": data.to, "value": data.value, "data": data.data }] }

Sell: { "chain": "base", "calls": [ approve tx, sell tx ] }

## Token info

- Name: MetaVision
- Symbol: MV
- Contract: 0x9d668460cB4A04DfFEB594Cb8d0FfE080aF5b4cF
- Network: Base
- DEX: Uniswap V2
- Website: https://metavision.click
- Telegram: https://t.me/MetaVisionMV
