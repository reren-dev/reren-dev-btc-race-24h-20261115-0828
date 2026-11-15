import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor"))
import makefun_bars

closes = []
ema5 = None
ema13 = None
has_filled_ever = False

last_entry_close = None
peak_close = None
bars_held = 0
cooldown_counter = 0

# Parameters for t1_bot15 (Winning Variant)
DROP45_THRESH = -0.015
CONF10_THRESH = 0.000
TP_PCT = 0.030
TRAIL_PCT = 0.015
MAX_HOLD = 1440
POS_SIZE = 1.0
COOLDOWN_BARS = 0
USE_EMA = False
USE_FALLBACK = False

def on_batch(state, batch):
    global ema5, ema13, has_filled_ever, last_entry_close, peak_close, bars_held, cooldown_counter

    if state.warming_up:
        return None

    if cooldown_counter > 0:
        cooldown_counter -= 1

    for f in batch.get("fills", []):
        if f.get("status") == "filled":
            has_filled_ever = True

    cbbtc_bar = None
    for bar in batch.get("bars", []):
        if bar.get("symbol") == "CBBTC":
            cbbtc_bar = bar
            break

    if cbbtc_bar is None:
        return None

    close = int(cbbtc_bar["c"])
    closes.append(close)

    if ema5 is None:
        ema5 = float(close)
        ema13 = float(close)
    else:
        ema5 = ema5 + (close - ema5) * (2.0 / 6.0)
        ema13 = ema13 + (close - ema13) * (2.0 / 14.0)

    is_long = "CBBTC" in state.positions and state.positions["CBBTC"].qty > 0

    if not is_long:
        bars_held = 0
        peak_close = None

        if len(closes) < 45 or cooldown_counter > 0:
            return None

        drop45 = close / closes[-45] - 1.0
        conf10 = close / closes[-10] - 1.0

        ema_ok = (not USE_EMA) or (ema5 > ema13)

        # Primary Entry
        if drop45 < DROP45_THRESH and conf10 > CONF10_THRESH and ema_ok:
            notional = int(state.cash * POS_SIZE)
            if notional <= 0:
                return None
            last_entry_close = close
            peak_close = close
            cooldown_counter = COOLDOWN_BARS
            return [{
                "side": "buy",
                "symbol": "CBBTC",
                "notional_quote_units": str(notional),
                "max_slippage_bps": 100,
            }]

        # Fallback Entry
        if USE_FALLBACK and (not has_filled_ever) and (state.seq >= 1200):
            if drop45 < (DROP45_THRESH / 2.0) and conf10 > (CONF10_THRESH / 2.0) and ema_ok:
                notional = state.cash // 4
                if notional <= 0:
                    return None
                last_entry_close = close
                peak_close = close
                cooldown_counter = COOLDOWN_BARS
                return [{
                    "side": "buy",
                    "symbol": "CBBTC",
                    "notional_quote_units": str(notional),
                    "max_slippage_bps": 100,
                }]

    else:
        bars_held += 1
        if peak_close is None:
            peak_close = close
        else:
            peak_close = max(peak_close, close)

        if last_entry_close is None:
            last_entry_close = close

        tp_thresh = last_entry_close * (1.0 + TP_PCT)
        trail_thresh = peak_close * (1.0 - TRAIL_PCT)

        if close > tp_thresh or close < trail_thresh or bars_held > MAX_HOLD:
            qty = state.positions["CBBTC"].qty
            if qty > 0:
                return [{
                    "side": "sell",
                    "symbol": "CBBTC",
                    "qty": str(qty),
                    "max_slippage_bps": 100,
                }]

    return None

if __name__ == "__main__":
    makefun_bars.run(on_batch)
