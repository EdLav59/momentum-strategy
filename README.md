# Momentum Trading Strategy: From Academic Theory to Market Reality

Implementation of Jegadeesh & Titman (1993) momentum strategy with lessons learned from 2024 market regime changes.

## Overview

This repository documents the evolution of a momentum trading strategy, from initial implementation through crisis adaptation. The project demonstrates how academic theory meets market reality, particularly during volatility spikes.

## The Story

Version 1 implements the classic Jegadeesh & Titman momentum approach with aggressive parameters:
- 6-month formation period to capture recent trends
- 3-month holding period for rapid rebalancing
- Top/Bottom 10% (decile portfolios for concentrated exposure)
- Monthly rebalancing

The strategy assumes **constant volatility** and uses fixed position sizing. This approach worked well 2021-2023 but proved vulnerable during 2024 regime shifts.

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

**Key Finding:** V2 achieves superior **risk-adjusted returns** despite similar absolute returns.

| Metric | V1 (Original) | V2 (Regime-Aware) | Improvement |
|--------|---------------|-------------------|-------------|
| **Sharpe Ratio** | **-0.23** | **+0.35** | **+252%**  |
| Annual Return | +0.16% | +0.12% | -4 bps |
| Max Drawdown | -0.96% | -1.04% | Similar |
| 2024 Return | **-0.2%** | **+1.0%** | **+120 bps** |
| Win Rate | 60% | 62% | +2% |
| Position Sizing | Fixed at 1.0x | Dynamic (0.5x-1.0x) | Adaptive |

### Why Sharpe Ratio Matters

The **252% improvement in Sharpe ratio** is the key metric:
- V1's negative Sharpe (-0.23) means it loses money on a risk-adjusted basis
- V2's positive Sharpe (+0.35) makes it institutionally viable and leverageable
- In quantitative finance, Sharpe ratio determines strategy deployment, not absolute returns
- A positive Sharpe can be scaled with leverage; a negative Sharpe cannot be fixed

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

## Technical Details

**Data Source**: Yahoo Finance  
**Universe**: 63 large-cap European stocks (CAC 40 + DAX 30)  
**Period**: January 2019 - December 2024 (5 years)  
**Formation Period**: 6 months  
**Holding Period**: 3 months  
**Portfolio Selection**: Top/Bottom 10% (decile portfolios)  
**Rebalancing**: Monthly  
**Position Sizing (V1)**: Fixed at 1.0x  
**Position Sizing (V2)**: Dynamic 0.5x-1.0x based on 20-day rolling volatility  
**Regime Threshold**: Mean + 2×std of rolling volatility  

## References

Jegadeesh, N., & Titman, S. (1993). Returns to buying winners and selling losers: Implications for stock market efficiency. *The Journal of Finance*, 48(1), 65-91.

## Author

Edouard Lavalard  

## License

MIT License
