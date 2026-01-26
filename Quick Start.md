# Quick Start Guide

## Installation

```bash
git clone https://github.com/EdLav59/momentum-trading-strategy.git
cd momentum-trading-strategy
pip install -r requirements.txt
```

## Running the Analysis

### Option 1: Run Both Versions Sequentially

```bash
# Run V1 (takes ~5-10 minutes)
cd v1_original
python momentum_v1.py
cd ..

# Run V2 (takes ~5-10 minutes)
cd v2_regime_aware
python momentum_v2.py
cd ..

# Analyze results
jupyter notebook analysis/failure_analysis_2024.ipynb
```

### Option 2: Quick Test

```bash
# Verify both versions work without running full backtest
python test_strategies.py
```

## Expected Output

### V1 (Original) produces:
- `v1_original/results_v1/performance_v1.png` - Performance visualization
- `v1_original/results_v1/trades_v1.csv` - Detailed trade log
- `v1_original/results_v1/summary_v1.csv` - Summary statistics

### V2 (Regime-Aware) produces:
- `v2_regime_aware/results_v2/performance_v2.png` - Performance visualization
- `v2_regime_aware/results_v2/trades_v2.csv` - Detailed trade log
- `v2_regime_aware/results_v2/summary_v2.csv` - Summary statistics
- `v2_regime_aware/results_v2/volatility_regime.csv` - Regime detection data

### Jupyter Notebook produces:
- `analysis/regime_comparison.png` - Side-by-side comparison chart

## Troubleshooting

### ModuleNotFoundError: No module named 'yfinance'

```bash
pip install -r requirements.txt
```

### Data download fails

Check internet connection and try again. yfinance occasionally has rate limiting.

### Charts don't display in Jupyter

Make sure matplotlib is properly installed:
```bash
pip install matplotlib==3.7.3
```

## Project Structure

```
momentum-trading-strategy/
├── README.md              Main documentation
├── requirements.txt       Python dependencies
├── test_strategies.py     Quick verification script
├── v1_original/          Original implementation
│   ├── README.md
│   ├── momentum_v1.py
│   └── results_v1/
├── v2_regime_aware/      Improved implementation
│   ├── README.md
│   ├── momentum_v2.py
│   └── results_v2/
└── analysis/             Comparative analysis
    └── failure_analysis_2024.ipynb
```

## Key Files

- `momentum_v1.py`: Original strategy with constant volatility
- `momentum_v2.py`: Improved strategy with regime detection
- `failure_analysis_2024.ipynb`: Detailed comparison and 2024 analysis

## Runtime

- V1 execution: ~5-10 minutes (depends on network speed for data download)
- V2 execution: ~5-10 minutes
- Jupyter analysis: ~2-3 minutes

## Questions?

Read the main README.md for detailed explanation of the learning journey.
