#!/usr/bin/env python3
"""Base liquidation market stats: Chainlink SVR auctions vs public races. READ-ONLY, standard library only.

Everything comes from the chain itself: blocks where a Chainlink SVR oracle update landed (topic 0x8d530b9d),
the SVR transaction (sent by the Chainlink node, with the winning bid inside), the Morpho Blue / Aave v3
liquidations in it, and the LEFTOVERS fought for in the same block by other bots (gas, priority fee,
who won, who reverted and how much gas the losers burned).

Usage:  python3 base_liquidation_stats.py [hours=24]
Env:    BASE_STATS_RPCS="https://rpc1;https://rpc2"  (default: public Base RPCs), BASE_STATS_SPAN=2000
Note:   the bid paid inside the Atlas auction is internal ETH (not in logs); the gross bonus is its ceiling.
"""
import collections
import json
import sys
import time
import urllib.request

HOURS = float(sys.argv[1]) if len(sys.argv) > 1 else 24.0
import os
RPCS = [u for u in os.getenv("BASE_STATS_RPCS", "https://base-rpc.publicnode.com;https://mainnet.base.org").split(";") if u]
SPAN = int(os.getenv("BASE_STATS_SPAN", "2000"))
SVR = "0x8d530b9ddc4b318d28fdd4c3a21fcfecece54c1a72a824f262985b99afef009b"
MORPHO = "0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb"
T_MORPHO = "0xa4946ede45d0c6f06a0f5ce92c9ad3b4751452d2fe0e25010783bcab57a67e41"  # Liquidate(...)
AAVE_POOL = "0xa238dd80c259a72e81d7e4664a9801593f98d1c5"
T_AAVE = "0xe413a321e8681d831f4dbccbca790d2952b56f977908e45be37335533e005286"   # LiquidationCall(...)
AAVE_ORACLE = "0x2Cc0Fc26eD4563A5ce5e8bdcfe1A2878676Ae156"
SEL_PARAMS = "2c3c9157"  # idToMarketParams(bytes32)
SEL_PRICE = "b3596f07"   # getAssetPrice(address)
SEL_DEC = "313ce567"     # decimals()
WAD = 10**18


def rpc(method, params):
    last = None
    for url in RPCS:
        for _ in range(3):
            try:
                req = urllib.request.Request(url, data=json.dumps({"jsonrpc": "2.0", "id": 1, "method": method,
                                                                   "params": params}).encode(),
                                             headers={"Content-Type": "application/json", "User-Agent": "svr-stats/1"})
                with urllib.request.urlopen(req, timeout=40) as r:
                    body = json.loads(r.read())
                if "result" in body:
                    return body["result"]
                last = body.get("error")
            except Exception as exc:
                last = str(exc)
            time.sleep(1.5)
    raise RuntimeError(f"RPC_FAILED {method}: {str(last)[:120]}")


def call(to, data, block="latest"):
    return rpc("eth_call", [{"to": to, "data": "0x" + data}, block])


def lif(lltv):
    den = WAD - 3 * 10**17 * (WAD - lltv) // WAD
    return min(115 * 10**16, WAD * WAD // den)


_params, _price = {}, {}


def market(mid):
    if mid not in _params:
        r = call(MORPHO, SEL_PARAMS + mid[2:])
        w = [r[2 + 64 * i: 2 + 64 * (i + 1)] for i in range(5)]
        loan = "0x" + w[0][-40:]
        _params[mid] = (loan, int(w[4], 16))
    return _params[mid]


def usd(token, raw):
    token = token.lower()
    if token not in _price:
        try:
            p = int(call(AAVE_ORACLE, SEL_PRICE + token[2:].rjust(64, "0")), 16) / 1e8
        except Exception:
            p = 0.0
        if token == "0x833589fcd6edb6e08f4c7c32d4f71b54bda02913":
            p = p or 1.0
        try:
            d = int(call(token, SEL_DEC), 16)
        except Exception:
            d = 18
        _price[token] = (p, d)
    p, d = _price[token]
    return raw / 10**d * p


def main():
    head = int(rpc("eth_blockNumber", []), 16)
    ts_head = int(rpc("eth_getBlockByNumber", [hex(head), False])["timestamp"], 16)
    ts_old = int(rpc("eth_getBlockByNumber", [hex(head - 1000), False])["timestamp"], 16)
    per_block = max(0.05, (ts_head - ts_old) / 1000)
    start = head - int(HOURS * 3600 / per_block)
    # Public RPCs refuse address-less getLogs over ranges (publicnode: "specify an address"), so the
    # scan starts from the LIQUIDATIONS (Morpho Blue + Aave, filtered by address) and then checks, per
    # block, whether that block carried an SVR oracle update (1-block topic query, accepted).
    liq_blocks, b, falhas, faixas = set(), start, 0, 0
    while b <= head:
        e = min(head, b + SPAN - 1)
        for addr, topic in ((MORPHO, T_MORPHO), (AAVE_POOL, T_AAVE)):
            faixas += 1
            try:
                for l in rpc("eth_getLogs", [{"fromBlock": hex(b), "toBlock": hex(e), "address": addr, "topics": [topic]}]):
                    liq_blocks.add(int(l["blockNumber"], 16))
            except RuntimeError:
                falhas += 1
        b = e + 1
    svr_logs, publicos = [], []
    for bn in sorted(liq_blocks):
        lg = rpc("eth_getLogs", [{"fromBlock": hex(bn), "toBlock": hex(bn), "topics": [SVR]}])
        (svr_logs.extend(lg) if lg else publicos.append(bn))
    blocks = sorted({int(l["blockNumber"], 16) for l in svr_logs})
    print(f"== BASE LIQUIDATIONS (Morpho+Aave) — last {HOURS:g} h — blocks {start}..{head} ({per_block:.2f} s/block) ==")
    print(f"ranges read {faixas} | failed {falhas}" + ("  << INCOMPLETE: run again or set BASE_STATS_RPCS" if falhas else ""))
    print(f"blocks with liquidations: {len(liq_blocks)} | with an SVR update in the same block: {len(blocks)} | without SVR (public race): {len(publicos)}")
    blocks = sorted(liq_blocks)
    tot = collections.Counter()
    vencedores, sobra_liq = collections.Counter(), collections.Counter()
    for bn in blocks:
        svr_tx = {l["transactionHash"] for l in svr_logs if int(l["blockNumber"], 16) == bn}
        publico = not svr_tx
        liqs = rpc("eth_getLogs", [{"fromBlock": hex(bn), "toBlock": hex(bn), "address": MORPHO, "topics": [T_MORPHO]}]) + \
            rpc("eth_getLogs", [{"fromBlock": hex(bn), "toBlock": hex(bn), "address": AAVE_POOL, "topics": [T_AAVE]}])
        blk = rpc("eth_getBlockByNumber", [hex(bn), True])
        by_tx = collections.defaultdict(lambda: {"n": 0, "usd": 0.0, "bonus": 0.0})
        for l in liqs:
            row = by_tx[l["transactionHash"]]
            row["n"] += 1
            data = l["data"][2:]
            if l["address"].lower() == MORPHO:
                loan, lltv = market(l["topics"][1])
                repaid = int(data[0:64], 16)
                v = usd(loan, repaid)
                row["usd"] += v
                row["bonus"] += v * (lif(lltv) - WAD) / WAD
            else:
                debt = "0x" + l["topics"][2][-40:]  # LiquidationCall(collateral, debt, user)
                v = usd(debt, int(data[0:64], 16))
                row["usd"] += v
        # every tx of the block that called Morpho/Aave after the SVR update = the leftover race (won or reverted)
        # the race = SVR tx + every liquidation tx + REVERTED txs sent to the same bot contracts (or
        # straight to Morpho/Aave): the losers, who also paid gas. Ordinary user ops are left out.
        bots = {(t.get("to") or "").lower() for t in blk["transactions"] if t["hash"] in by_tx} | {MORPHO, AAVE_POOL}
        race = [t for t in blk["transactions"] if t["hash"] in svr_tx or t["hash"] in by_tx or
                (t.get("to") or "").lower() in bots]
        print(f"\nBLOCO {bn} ({time.strftime('%d/%m %H:%M:%S', time.gmtime(int(blk['timestamp'], 16)))} UTC) "
              f"block gas {int(blk['gasUsed'], 16):,}/{int(blk['gasLimit'], 16):,}")
        for t in race:
            r = rpc("eth_getTransactionReceipt", [t["hash"]])
            gas, price = int(r["gasUsed"], 16), int(r["effectiveGasPrice"], 16)
            cost = gas * price / 1e18
            row = by_tx.get(t["hash"], {"n": 0, "usd": 0.0, "bonus": 0.0})
            senders = {x["from"].lower() for x in blk["transactions"] if x["hash"] in svr_tx}
            kind = "SVR" if (t["hash"] in svr_tx or t["from"].lower() in senders) else ("PUBLIC" if publico else "LEFTOVER")
            ok = int(r["status"], 16) == 1
            if ok and t["hash"] not in by_tx and t["hash"] not in svr_tx:
                continue  # a successful non-liquidation call (normal user operation)
            print(f"  {kind:5} idx {int(t['transactionIndex'], 16):3} {'OK ' if ok else 'REV'} from {t['from'][:10]} "
                  f"liq {row['n']:3} repaid US$ {row['usd']:>11,.2f} bonus~ US$ {row['bonus']:>9,.2f} | gas {gas:>9,} "
                  f"@ {price / 1e9:8.3f} gwei = {cost:.5f} ETH")
            tot[kind + "_tx"] += 1
            tot[kind + "_liq"] += row["n"]
            tot[kind + "_usd"] += row["usd"]
            tot[kind + "_bonus"] += row["bonus"]
            tot[kind + "_gas_eth"] += cost
            if not ok:
                tot[kind + "_revert"] += 1
                tot[kind + "_revert_eth"] += cost
            if kind == "SVR" and row["n"]:
                vencedores[t["from"][:10]] += 1
            if kind == "LEFTOVER" and row["n"]:
                sobra_liq[t["from"][:10]] += 1
    print("\n== TOTALS ==")
    print(f"SVR  : {tot['SVR_tx']} tx | {tot['SVR_liq']} liquidations | repaid US$ {tot['SVR_usd']:,.2f} | "
          f"gross bonus~ US$ {tot['SVR_bonus']:,.2f} (bid ceiling) | gas {tot['SVR_gas_eth']:.4f} ETH")
    print(f"LEFTOVER: {tot['LEFTOVER_tx']} tx | {tot['LEFTOVER_liq']} liquidations | repaid US$ {tot['LEFTOVER_usd']:,.2f} | "
          f"gross bonus~ US$ {tot['LEFTOVER_bonus']:,.2f} | gas {tot['LEFTOVER_gas_eth']:.4f} ETH | "
          f"reverted {tot['LEFTOVER_revert']} (burned {tot['LEFTOVER_revert_eth']:.4f} ETH of gas)")
    print(f"PUBLIC (no SVR in block): {tot['PUBLIC_tx']} tx | {tot['PUBLIC_liq']} liquidations | repaid US$ {tot['PUBLIC_usd']:,.2f} | "
          f"gross bonus~ US$ {tot['PUBLIC_bonus']:,.2f} | gas {tot['PUBLIC_gas_eth']:.4f} ETH | reverted {tot['PUBLIC_revert']}")
    print("SVR senders (Chainlink nodes):", dict(vencedores.most_common(5)))
    print("leftover winners:", dict(sobra_liq.most_common(8)))


if __name__ == "__main__":
    main()
