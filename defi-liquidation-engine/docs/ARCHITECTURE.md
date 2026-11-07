# Architecture

## Two chains, two small servers
- **VM1 (Base):** Python services under systemd: liquidation engine (Morpho Blue, Moonwell, Aave v3 radar),
  fast arbitrage scanner, CEX price signals, Telegram alerting, hourly summary, watchdog.
- **VM2 (Solana):** Node.js engine: arbitrage (Meteora DLMM / Jupiter), liquidations (Kamino, Jupiter Lend),
  coherent account snapshots per slot, private RPC execution pool with per-provider budgets.
- Both run on Oracle Cloud *Always Free* VMs (1 GB RAM). Memory was a hard constraint: e.g. the Kamino scan was
  rewritten to read one market at a time (heap peak 212 MB → 98 MB, restarts 75/night → 0).

## Base liquidation path
1. **Radar:** Morpho's official GraphQL API seeds borrowers by health-factor band; every position is then
   re-read on chain (Multicall3), with the exact Morpho math (shares → assets, Taylor-compounded interest,
   liquidation incentive factor from the market LLTV).
2. **Pre-armed list:** positions with 0.95 < HF < 1.02 get their full plan built every 30 s. A watcher polls only
   those oracles every 0.4 s and, on a price change, recomputes HF locally and fires the ready plan. The same
   call returns the block number, so the execution context never simulates on an older state than the trigger.
3. **Routes:** USDC flash loan (buy the debt token exactly) or a flash loan of the debt token itself for large
   positions; collateral sold on Uniswap V3 / Aerodrome Slipstream, with KyberSwap only where V3 cannot even repay
   the debt (RFQ sources excluded: measured to under-deliver 6%). Two viable routes → the second is simulated
   automatically if the first reverts.
4. **Final check:** `eth_simulateV1` on the sealed parent block with the network's own base fee, P90/P50 priority
   fees, L1 data fee and operator fee; the executor's on-chain guard enforces cost + US$ 0.02.

## Solana liquidation path
- Kamino: SDK `buildLiquidateTxns`; obligations at ≥ 97% of their liquidation LTV are re-read together every other
  turn with fresh oracle prices.
- Jupiter Lend: discovery uses the protocol's own sentinel simulation (the vault answers how much is liquidatable,
  or why not). Smart-collateral DEX vaults were added by fixing optional accounts the SDK filled incorrectly.
- Transactions use an operator-owned Address Lookup Table to fit the 1,232-byte limit.

## Engineering practices
- Every value comes from the network (gas, fees, tips, slippage floors); nothing is hard-coded or guessed.
- "Proof, not status": tools print evidence (positions read, simulations approved/rejected with the reason,
  errors with file:line), never just "active".
- Alerts fire only on persistent problems; transient back-pressure goes to logs and counters.
