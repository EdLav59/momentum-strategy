# Version 2: Regime-Aware Momentum Strategy

Improved implementation with dynamic position sizing based on volatility regime detection.

## Strategy Specification

**Formation Period**: 12 months  
**Holding Period**: 6 months  
**Portfolio Construction**: Top and bottom 20% quintiles  
**Rebalancing**: Monthly  
**Position Sizing**: **Dynamic** - scales from 0.5x to 1.0x based on volatility regime  

## Key Improvement: Regime Detection

This version adds volatility regime detection:
- Calculates 20-day rolling volatility
- Defines threshold as mean + 2*std
- Reduces position size when volatility exceeds threshold
- Position multiplier scales linearly from 1.0x (low vol) to 0.5x (high vol)

## Why This Version Works Better

During market turbulence (like 2024), this strategy:
- Reduces exposure when volatility spikes
- Protects capital during regime shifts
- Maintains exposure during normal conditions
- Provides better risk-adjusted returns

## Position Sizing Logic

```
if volatility < mean:
    position_size = 1.0x  (full exposure)
elif volatility > threshold:
    position_size = 0.5x  (half exposure)
else:
    position_size = linear interpolation between 1.0x and 0.5x
```

## Files Generated

After running `momentum_v2.py`:

- `results_v2/performance_v2.png` - Performance charts including position sizing
- `results_v2/trades_v2.csv` - Detailed trade log with position multipliers
- `results_v2/summary_v2.csv` - Performance summary statistics
- `results_v2/volatility_regime.csv` - Volatility regime data

## Usage

```bash
python momentum_v2.py
```

The script will:
1. Download historical data from Yahoo Finance
2. Calculate volatility regime indicators
3. Run the regime-aware backtest
4. Calculate performance metrics
5. Generate visualizations including position sizing chart
6. Save results to `results_v2/`

## Performance Characteristics

Expected improvements over V1:
- Lower maximum drawdown during volatility spikes
- Better Sharpe ratio (risk-adjusted returns)
- Higher Calmar ratio (return/max drawdown)
- More stable performance across different market regimes

## Implementation Details

**Volatility Calculation**: Equal-weighted portfolio of all stocks  
**Rolling Window**: 20 trading days  
**Threshold**: Historical mean + 2 * historical standard deviation  
**Position Range**: 0.5x (minimum) to 1.0x (maximum)  

## Limitations

This approach has limitations:
- Reduces exposure in all high-volatility periods (some may be profitable)
- Parameters (window, threshold, min position) were chosen after observing 2024
- May underperform V1 in persistent bull markets with higher volatility
- Backward-looking volatility may not predict forward regime changes

## What This Version Teaches

Dynamic position sizing based on market conditions improves risk-adjusted returns. While this version doesn't maximize absolute returns, it provides **better risk management** during regime shifts.

The key insight: **adapt position sizing to market reality** rather than assuming constant conditions.
