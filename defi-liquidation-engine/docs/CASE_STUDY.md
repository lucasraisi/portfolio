# Case study: why a correct liquidation bot still loses on Base

## Problem
On 2026-11-07 the bot's simulations kept reverting at step 0 (`liquidate`) right after oracle moves.

## Investigation (all on chain)
- Morpho's API listed the liquidations at 03:17, 03:35 and 04:14 UTC; the positions were exactly the ones the bot
  had armed.
- Each of those blocks contains the **Chainlink SVR** update topic `0x8d530b9d…` *inside the same transaction*
  that liquidated up to 33 positions (sent by a Chainlink node, priority fee 15 gwei).
- The bot only sees the new price after the block is sealed: by then the positions no longer exist.
- In the 03:17 block, 20 other bots fought for the leftovers at 3–193 gwei; one reverted attempt burned 0.139 ETH.

## Changes shipped
- Self-diagnosis on revert: reads the position at the simulation's parent block and reports
  `ALREADY_LIQUIDATED_SVR` with liquidator, block and tx; a partially liquidated remainder is re-planned.
- Execution context waits for the detection block (a lagging private RPC no longer produces false "healthy").
- Found and fixed an aggregator bug: `slippageTolerance=0` made every KyberSwap sell revert (measured
  0.12–0.89 bps under-delivery on chain).
- Open-source market tool (`tools/base_liquidation_stats.py`) to size the opportunity before spending capital.

## Result
Large-position routes went from "rejected" to passing in simulation (12/14 WETH-debt, 8/8 cbXRP), and the business
decision became data-driven: the next step is auction access, not more code.
