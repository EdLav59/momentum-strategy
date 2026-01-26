# Version 1: Original Momentum Strategy

Classic implementation of Jegadeesh & Titman (1993) momentum strategy with constant position sizing.

## Strategy Specification

**Formation Period**: 12 months  
**Holding Period**: 6 months  
**Portfolio Construction**: Top and bottom 20% quintiles  
**Rebalancing**: Monthly  
**Position Sizing**: Fixed at 1.0x (no volatility adjustment)  

## Key Assumption

This version assumes **constant volatility** across all market conditions. Position sizing does not adapt to changes in market regime.

## Why This Version Failed in 2024

During mid-2024, market volatility spiked due to French political uncertainty. The strategy maintained full exposure despite elevated risk, leading to larger-than-expected drawdowns.

The constant position sizing meant:
- Full 1.0x exposure during high volatility periods
- No protection against regime shifts
- Drawdowns amplified by market turbulence

## Files Generated

After running `momentum_v1.py`:

- `results_v1/performance_v1.png` - Performance charts
- `results_v1/trades_v1.csv` - Detailed trade log
- `results_v1/summary_v1.csv` - Performance summary statistics

## Usage

```bash
python momentum_v1.py
```

The script will:
1. Download historical data from Yahoo Finance
2. Run the momentum backtest
3. Calculate performance metrics
4. Generate visualizations
5. Save results to `results_v1/`

## Performance Characteristics

Expected characteristics of this version:
- Works well in stable, low-volatility markets
- Vulnerable to regime shifts and volatility spikes
- Higher maximum drawdown than regime-aware version
- Lower risk-adjusted returns during turbulent periods

The failure of V1 during 2024 motivated the development of V2 with dynamic position sizing.
