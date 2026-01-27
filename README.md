# European Equity Momentum Strategy with Z-Score Filtering

A quantitative momentum trading strategy for European large-cap equities, implementing standardized Z-score signal filtering, transaction cost modeling, and comprehensive performance analytics.

**Author:** Edouard Lavalard  
**Period:** 2019-2024

---

## Project Overview

This project implements a long-short momentum strategy on European equity markets (CAC 40 + DAX 30), based on the seminal research by Jegadeesh & Titman (1993). The strategy uses Z-score normalization to filter momentum signals and includes explicit transaction cost modeling for institutional realism.

### Key Features

- **Z-Score Signal Filtering**: Standardized momentum scores filter noise and identify statistically significant trends
- **Transaction Cost Modeling**: 1 basis points per trade, reflecting realistic institutional execution costs
- **Portfolio Rebalancing Logic**: Monthly rebalancing with turnover tracking
- **Professional Analytics**: Comprehensive performance metrics, visualizations, and risk analysis

---

## Strategy Configuration

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| **Formation Period** | 6 months | Captures medium-term momentum in European markets |
| **Holding Period** | 1 month | Optimized to capture momentum before reversal |
| **Signal Filter** | Z-score > ±1.5 | Trades only statistically significant signals (top/bottom ~15%) |
| **Portfolio Selection** | Top/Bottom 10% deciles | Concentrated positions maximize momentum premium |
| **Position Sizing** | Equal-weighted, constant 1.0x | Assumes constant market volatility |
| **Transaction Costs** | 1 bp per trade | Large-cap European bid-ask spread |
| **Rebalancing Frequency** | Monthly | Balances momentum capture vs transaction costs |

---

## Methodology

### Z-Score Momentum Signal

For each stock in the universe during the formation period:

```
Momentum Score = Cumulative Return over 6 months
Z-Score = (Momentum Score - Mean) / Std Dev
```

**Signal Filtering:**
- **Winners:** Z-score > +1.5 (long position)
- **Losers:** Z-score < -1.5 (short position)
- **Neutral:** |Z-score| < 1.5 (no position, filtered out)

This approach reduces noise by trading only momentum signals that are statistically significant (>1.5 standard deviations from mean).

### Portfolio Construction

- Select top 10% of filtered winners for long portfolio
- Select bottom 10% of filtered losers for short portfolio
- Equal-weight within each portfolio
- Rebalance monthly with transaction cost application

### Transaction Cost Modeling

```python
Turnover = (New Positions ⊕ Old Positions) / Total Positions
Transaction Cost = Turnover × 1 bp
Net Return = Gross Return - Transaction Cost
```

Average turnover: approximately 100% monthly (complete portfolio refresh)

With 1 bp transaction costs (realistic for large-cap European equities), total costs represent approximately 0.6% annually.

---

## Results Summary

### Performance Metrics (2019-2024)

| Metric | Value |
|--------|-------|
| **Annual Return (Net)** | 1.23% |
| **Annual Return (Gross)** | 1.35% |
| **Sharpe Ratio** | 0.61 |
| **Max Drawdown** | -2.34% |
| **Calmar Ratio** | 0.53 |
| **Win Rate** | 54.1% |
| **Annual Volatility** | 2.03% |
| **Avg Winner Z-Score** | +2.78 |
| **Avg Loser Z-Score** | -2.42 |
| **Z-Score Spread** | 5.19 |

### Cost Analysis

| Metric | Value |
|--------|-------|
| **Transaction Costs (Annual)** | 0.62% |
| **Average Turnover** | 101.6% monthly |
| **Cost per Rebalancing** | 0.010% |

### Annual Performance

| Year | Net Return | Gross Return | Note |
|------|-----------|--------------|------|
| 2019 | +0.3% | +0.4% | Initial period |
| 2020 | +4.5% | +4.6% | Strong momentum capture during volatility |
| 2021 | +0.7% | +0.8% | Consolidation period |
| 2022 | +0.0% | +0.1% | Challenging market conditions |
| 2023 | +2.9% | +3.0% | Recovery and positive momentum |
| 2024 | **-1.7%** | **-1.6%** | **Failed during French elections** |
| **Cumulative** | **+6.7%** | **+7.3%** | Over 5-year period |

---

### What Went Wrong in 2024

Despite achieving a positive Sharpe ratio (0.61) and 54% win rate over the full period, the strategy suffered a -1.7% loss in 2024 during the June-July French elections. The strategy assumed constant market volatility by using equal position sizing (1.0x) throughout all periods. This assumption proved incorrect when:

1. **Volatility spiked unexpectedly** during political uncertainty
2. **Momentum signals reversed rapidly** as markets reassessed risk
3. **Full exposure amplified losses** with no defensive adjustment mechanism

The monthly rebalancing frequency (optimized for momentum capture) meant the strategy maintained full exposure during the entire volatility spike, unable to adapt mid-month.

#
## Academic Foundation

This implementation builds on:

- **Jegadeesh & Titman (1993)**: "Returns to Buying Winners and Selling Losers"
- **Carhart (1997)**: Four-factor model including momentum
- **Asness et al. (2013)**: "Value and Momentum Everywhere"

The Z-score normalization approach follows standard practice in quantitative finance for cross-sectional signal filtering.

## Contact

**Edouard Lavalard**  

---

## License

MIT License - See LICENSE file for details
