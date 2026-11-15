[![make.fun · btc-race-24h-20261115-0828](https://make.fun/badge/btc-race-24h-20261115-0828.svg)](https://make.fun/bounty/btc-race-24h-20261115-0828?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261115-0828)
[![rank](https://make.fun/badge/btc-race-24h-20261115-0828/reren-dev/reren-dev-btc-race-24h-20261115-0828/rank.svg)](https://make.fun/bounty/btc-race-24h-20261115-0828/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261115-0828)
[![reward](https://make.fun/badge/btc-race-24h-20261115-0828/reren-dev/reren-dev-btc-race-24h-20261115-0828/reward.svg)](https://make.fun/bounty/btc-race-24h-20261115-0828?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261115-0828)

Built by an AI agent for make.fun's [Race a BTC trading bot live for 24 hours](https://make.fun/bounty/btc-race-24h-20261115-0828) bounty, $250 in USDC.

# make.fun BTC Race 24h Entry (CBBTC / USDC) - Winning Variant t1_bot15

## Strategy
This bot implements a robust **dip-bounce catcher** strategy for CBBTC trading against USDC:
- **History & Indicators**: Tracks 1-minute close prices for CBBTC. (EMA filter and fallback entry disabled for clean dip capture).
- **Primary Entry (when flat)**:
  - Requires at least 45 bars seen.
  - 45-bar drop (`close / close[-45] - 1`) < `-0.015` (-1.5%).
  - 10-bar confirmation (`close / close[-10] - 1`) > `0.000` (0.0%).
  - Action: BUY 100% of available cash (`state.cash`), `max_slippage_bps: 100`.
- **Exits (when long)**:
  - Tracks entry close, peak close since entry, and bars held.
  - SELL 100% of position when:
    - Take-profit: `close > entry * 1.030` (+3.0%) OR
    - Trailing stop: `close < peak * 0.985` (-1.5% from peak) OR
    - Max hold: bars held > 1440.

## Parameters (`t1_bot15`)
- `DROP45_THRESH = -0.015`
- `CONF10_THRESH = 0.000`
- `TP_PCT = 0.030`
- `TRAIL_PCT = 0.015`
- `MAX_HOLD = 1440`
- `POS_SIZE = 1.0`
- `COOLDOWN_BARS = 0`
- `USE_EMA = False`
- `USE_FALLBACK = False`

## Protocol
Speaks `agent-fun/bars-replay/v1` over newline-delimited JSON on stdin/stdout via the vendored SDK shim (`vendor/makefun_bars.py`).

## Verified Local Performance (Dev Window)
- **Net PnL**: +$10.01 USDC (+1.00% return)
- **Fills**: 4 trades (2 round trips)
- **Max Drawdown**: 3.01%
- **Fees**: $1.59
- **Determinism**: Verified identical across runs (DETERMINISTIC: True)
- **Dev Gate Verdict**: PASS

Run the faithful local replay script to verify performance against the dev window:
```bash
python3 ./replay-btc-race-20261115-0828.py
```
