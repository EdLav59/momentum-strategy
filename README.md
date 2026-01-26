# Momentum Trading Strategy: From Academic Theory to Market Reality

Implementation of Jegadeesh & Titman (1993) momentum strategy with lessons learned from 2024 market regime changes.

## Overview

This repository documents the evolution of a momentum trading strategy, from initial implementation through crisis adaptation. The project demonstrates how academic theory meets market reality, particularly during volatility spikes.

## The Story

Version 1 implements the classic Jegadeesh & Titman momentum approach:
- 12-month formation period to identify winners and losers
- 6-month holding period
- Equal-weighted portfolios (top and bottom 20%)
- Monthly rebalancing

The strategy assumes **constant volatility** and uses fixed position sizing. This worked well in normal market conditions but proved vulnerable during regime shifts.

During mid-2024, the strategy encountered significant drawdowns when French political uncertainty caused volatility spikes. The constant position sizing assumption meant the strategy maintained full exposure during a period when risk had fundamentally changed.

Key observations:
- Market volatility increased 2+ standard deviations above historical mean
- Fixed position sizing amplified losses during the regime shift
- The strategy needed adaptation to survive changing market conditions

The crisis revealed a critical flaw: **ignoring volatility regimes**. Markets alternate between low-volatility and high-volatility regimes, and position sizing should reflect this reality.

Key insights:
- Momentum strategies work differently in high vs. low volatility environments
- Constant volatility assumptions are dangerous during regime shifts
- Risk management requires dynamic position sizing

Version 2 adds regime detection:
- 20-day rolling volatility window
- Dynamic position sizing: reduce exposure when vol > mean + 2*std
- Position scales from 1.0x (normal) to 0.5x (high volatility)

This approach protects capital during turbulent periods while maintaining exposure during normal markets.

## Results Comparison

| Metric | V1 (Original) | V2 (Regime-Aware) |
|--------|---------------|-------------------|
| Annual Return | Performance dependent on period | Better risk-adjusted returns |
| Max Drawdown | Higher during 2024 | Reduced through position scaling |
| Sharpe Ratio | Lower volatility penalty | Improved risk-adjusted performance |
| Position Sizing | Fixed at 1.0x | Dynamic (0.5x to 1.0x) |

## Repository Structure

```
momentum-trading-strategy/
├── README.md
├── requirements.txt
├── v1_original/
│   ├── README.md
│   ├── momentum_v1.py
│   └── results_v1/
├── v2_regime_aware/
│   ├── README.md
│   ├── momentum_v2.py
│   └── results_v2/
└── analysis/
    └── failure_analysis_2024.ipynb
```

## How to Run

### Setup

```bash
git clone https://github.com/EdLav59/momentum-trading-strategy.git
cd momentum-trading-strategy
pip install -r requirements.txt
```

Requires Python 3.9 or 3.10.

### Run Version 1 (Original)

```bash
cd v1_original
python momentum_v1.py
```
This runs the original strategy and saves results to `results_v1/`.

### Run Version 2 (Regime-Aware)

```bash
cd v2_regime_aware
python momentum_v2.py
```
This runs the improved strategy with regime detection and saves results to `results_v2/`.

### Analyze the Differences

```bash
jupyter notebook analysis/failure_analysis_2024.ipynb
```
This notebook compares both versions and analyzes the 2024 failure in detail.

## What I Learned

### Technical Lessons

1. **Market regimes matter**: Strategies must adapt to changing volatility environments
2. **Position sizing is critical**: Fixed positions amplify losses during regime shifts
3. **Risk management is essential**: Protecting capital matters more than maximizing returns
4. **Simple beats complex**: A basic volatility threshold works better than complex models

### Practical Lessons

1. **Failure teaches more than success**: The 2024 drawdown revealed fundamental flaws
2. **Assumptions must be tested**: "Constant volatility" sounds reasonable until it isn't
3. **Academic theory needs adaptation**: Real markets don't always behave like backtests
4. **Risk-adjusted returns matter**: Lower returns with controlled risk beats high returns with crashes

### Implementation Lessons

1. **Code for clarity**: Future-you will thank present-you for clear documentation
2. **Version control decisions**: Keeping broken code shows learning journey
3. **Real data matters**: Synthetic data would hide the 2024 failure
4. **Visualizations convince**: Charts show problems faster than statistics

## Limitations

This analysis has important limitations:

1. **Hindsight bias**: The regime threshold was calibrated after observing 2024
2. **Parameter sensitivity**: Different vol windows or thresholds yield different results
3. **Transaction costs ignored**: Real implementation has costs and slippage
4. **Small sample size**: One regime shift doesn't prove the solution works generally
5. **Survivorship bias**: Universe selection may affect results

The goal is demonstrating learning from failure, not claiming a perfect solution.

## Technical Details

**Data Source**: Yahoo Finance  
**Universe**: 65+ large-cap European stocks (CAC 40 + DAX 30 components)  
**Period**: January 2019 - December 2024  
**Rebalancing**: Monthly  
**Position Sizing (V1)**: Fixed at 1.0x  
**Position Sizing (V2)**: Dynamic 0.5x - 1.0x based on 20-day rolling volatility  

## References

Jegadeesh, N., & Titman, S. (1993). Returns to buying winners and selling losers: Implications for stock market efficiency. *The Journal of Finance*, 48(1), 65-91.

## Author

Edouard Lavalard  
## License

MIT License
