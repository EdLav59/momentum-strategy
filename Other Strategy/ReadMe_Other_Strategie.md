# V2 - Regime-Aware Momentum Strategy

---

## Overview

This version enhances the baseline momentum strategy by adding volatility regime detection with dynamic position sizing, while maintaining the same Z-score momentum signal filtering as V1.

---

## What's Different from V1?

**Both V1 and V2 use:**
- Z-score filtering for momentum signals (threshold ±1.5)
- Same formation period (6 months) and holding period (1 month)
- Same transaction costs (1 bp per trade)
- Same universe (62 European large-caps)

**V2 adds:**
- Volatility regime detection via volatility Z-scores
- Dynamic position sizing (0.5x-1.0x) based on volatility regime
- Adaptive exposure during high-volatility periods

| Feature | V1 (Baseline) | V2 (Regime-Aware) |
|---------|---------------|-------------------|
| **Momentum Signal** | Z-score > ±1.5 | Z-score > ±1.5 (same) |
| **Position Sizing** | Constant 1.0x | Dynamic 0.5x-1.0x |
| **Regime Detection** | None | Volatility Z-score |
| **Risk Management** | Static | Adaptive |

---

## Implementation Details

### Momentum Signals (Same as V1)

```python
# Calculate momentum Z-scores (same as V1)
momentum_scores = cumulative_returns_6M
momentum_z_scores = (momentum_scores - mean) / std

# Filter signals (same as V1)
winners = stocks where momentum_z > +1.5
losers = stocks where momentum_z < -1.5
```

### Volatility Regime Detection

```python
# Calculate rolling volatility
rolling_vol = returns.rolling(20).std() * sqrt(252)

# Standardize volatility to Z-scores (1-year rolling window)
vol_mean = rolling_vol.rolling(252, min_periods=63).mean()
vol_std = rolling_vol.rolling(252, min_periods=63).std()
vol_z_score = (rolling_vol - vol_mean) / vol_std

# Regime classification
if vol_z_score <= 1.0:
    regime = "Normal"       # Volatility below 1 std dev
elif vol_z_score >= 1.5:
    regime = "High Vol"     # Volatility above 1.5 std dev
else:
    regime = "Elevated"     # Between 1.0 and 1.5
```

### Dynamic Position Sizing

```python
if vol_z_score <= 1.0:
    position_size = 1.0x  # Full exposure in normal regime
elif vol_z_score >= 1.5:
    position_size = 0.5x  # Reduced exposure in high volatility
else:
    # Linear interpolation between thresholds
    ratio = (vol_z_score - 1.0) / (1.5 - 1.0)
    position_size = 1.0 - 0.5 * ratio
```

---

## Configuration

| Parameter | Value | Purpose |
|-----------|-------|---------|
| **Volatility Window** | 20 days | Short-term volatility measure |
| **Rolling Statistics Window** | 252 days (1 year) | Long-term mean/std for Z-score |
| **Low Volatility Threshold** | Vol Z-score ≤ 1.0 | Normal regime |
| **High Volatility Threshold** | Vol Z-score ≥ 1.5 | High volatility regime |
| **Min Position Size** | 0.5x | Maximum risk reduction |
| **Max Position Size** | 1.0x | Full exposure |

---

## Results Comparison

### Performance Metrics (2019-2024)

| Metric | V1 (Baseline) | V2 (Regime-Aware) | Difference |
|--------|---------------|-------------------|------------|
| **5-Year Return** | +8.0% | +6.5% | -1.5% |
| **Sharpe Ratio** | 0.61 | ~0.55 | -0.06 |
| **Max Drawdown** | -2.5% | -2.0% | +0.5% |
| **Win Rate** | 54.1% | ~53% | -1.1% |
| **Avg Position** | 1.0x | 0.92x | -8% exposure |

### Regime Detection Activity

**Position sizing reduced only 3-4 times over 5 years:**

| Date | Vol Z-Score | Position Size | Market Event |
|------|-------------|---------------|--------------|
| **Mar 2020** | 4.0 | 0.5x | COVID crash |
| **Jun 2023** | 1.5 | 0.8x | Banking concerns |
| **Jul 2024** | 2.0 | 0.6x | French elections |

**Observation:** System at full 1.0x exposure **95% of the time**

---

## Why V2 Underperformed

### 1. Opportunity Cost > Protection Value

**Trade-off analysis:**
- Protection gained: -0.5% drawdown improvement (2.5% to 2.0%)
- Cost paid: -1.5% return reduction (8.0% to 6.5%)
- Net result: Unfavorable (3:1 cost-to-benefit ratio)

**Why:** Momentum strategies exhibit **strong post-crash rebounds**
- When position = 0.5x during volatility spike
- Also captures only 50% of the subsequent recovery
- Misses 50% of rebound gains

### 2. Thresholds Too Conservative

Volatility Z-score thresholds (1.0 / 1.5) trigger **very rarely:**
- Only during extreme events (COVID: Z=4.0, way above threshold)
- Misses moderate volatility spikes (Z=0.5 to 1.0)
- System defensive only ~5% of time

### 3. Monthly Rebalancing Lag

**Problem:** Volatility events evolve faster than monthly rebalancing
- June 2024 French elections: spike and partial recovery within 20 days
- V2 held reduced position (0.6x) through entire month including recovery
- Missed 40% of rebound gains during recovery phase

### 4. Asymmetric Recovery Dynamics

Momentum strategies exhibit specific crash/recovery pattern:
- **Drawdown phase:** Sharp, rapid losses (captured by regime detection)
- **Recovery phase:** Fast, aggressive rebounds (missed by defensive sizing)
- V2's symmetric sizing (reduces by 50% both ways) doesn't match asymmetric dynamics

---

## Visualizations

V2 generates 4-panel chart showing:
1. **Cumulative Performance:** Total returns over time
2. **Dynamic Position Sizing:** When and how much exposure was reduced
3. **Volatility Z-Score:** Regime detection signals with thresholds
4. **Drawdown:** Risk exposure and recovery patterns
