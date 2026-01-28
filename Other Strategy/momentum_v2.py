"""
Momentum Trading Strategy - Version 2 (Regime-Aware)
Z-Score based momentum with dynamic position sizing via volatility regime detection

Author: Edouard Lavalard
License: MIT
"""

import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
import yfinance as yf
from datetime import datetime
import warnings
import os
warnings.filterwarnings('ignore')

plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")


class MomentumStrategyV2:
    """
    Regime-Aware Momentum Strategy - Dynamic Position Sizing
    
    Configuration:
    - Formation: 6 months
    - Holding: 1 month
    - Signal Filter: Z-score > ±1.5
    - Position Sizing: DYNAMIC 0.5x-1.0x (volatility regime detection)
    - Regime Detection: Volatility Z-score with rolling 252-day window
    - Transaction Costs: 1 bp per trade
    """
    
    def __init__(self):
        self.end_date = '2024-12-31'
        self.start_date = '2019-01-01'
        
        # Universe: European large-caps (CAC 40 + DAX 30)
        self.tickers = [
            # CAC 40
            'AI.PA', 'AIR.PA', 'ALO.PA', 'MT.AS', 'CS.PA', 'BNP.PA',
            'EN.PA', 'CAP.PA', 'CA.PA', 'ACA.PA', 'BN.PA', 'ENGI.PA',
            'EL.PA', 'RMS.PA', 'KER.PA', 'OR.PA', 'LR.PA', 'MC.PA',
            'ML.PA', 'ORA.PA', 'RI.PA', 'PUB.PA', 'RNO.PA', 'SAF.PA',
            'SGO.PA', 'SAN.PA', 'SU.PA', 'GLE.PA', 'STLAP.PA', 'STMPA.PA',
            'TEP.PA', 'HO.PA', 'TTE.PA', 'URW.PA', 'VIE.PA', 'DG.PA', 'VIV.PA',
            # DAX 30
            'ADS.DE', 'ALV.DE', 'BAS.DE', 'BAYN.DE', 'BMW.DE', 'CON.DE',
            'MBG.DE', 'DB1.DE', 'DBK.DE', 'DHL.DE', 'DTE.DE',
            'EOAN.DE', 'FRE.DE', 'HEI.DE', 'HEN3.DE', 'IFX.DE', 'LIN.DE',
            'MRK.DE', 'MTX.DE', 'MUV2.DE', 'RWE.DE', 'SAP.DE', 'SIE.DE',
            'VOW3.DE', 'VNA.DE'
        ]
        
        self.formation_months = 6
        self.holding_months = 1
        self.z_score_threshold = 1.5
        self.transaction_cost_bps = 1
        
        # Regime detection parameters
        self.vol_window = 20
        self.vol_z_low = 1.0
        self.vol_z_high = 1.5
        
        self.price_data = None
        self.returns_data = None
        self.volatility_regime = None
        self.results = []
        self.previous_positions = {}
        
        print("=" * 70)
        print("MOMENTUM STRATEGY V2 - REGIME-AWARE (DYNAMIC SIZING)")
        print("=" * 70)
        print(f"Period: {self.start_date} to {self.end_date}")
        print(f"Universe: {len(self.tickers)} European large-caps")
        print(f"Position Sizing: DYNAMIC 0.5x-1.0x (volatility regime detection)")
        print(f"Regime Thresholds: Vol Z-score {self.vol_z_low}/{self.vol_z_high}")
        print("=" * 70)
    
    def fetch_data(self):
        """Download historical price data"""
        print("\n[1/8] Fetching data...")
        
        start_dt = pd.to_datetime(self.start_date)
        end_dt = pd.to_datetime(self.end_date)
        
        all_data = {}
        success_count = 0
        
        for ticker in self.tickers:
            try:
                stock = yf.Ticker(ticker)
                hist = stock.history(start=start_dt, end=end_dt, auto_adjust=True)
                
                if not hist.empty and len(hist) > 100:
                    all_data[ticker] = hist['Close']
                    success_count += 1
                    if success_count % 10 == 0:
                        print(f"  Progress: {success_count}/{len(self.tickers)}")
            except:
                continue
        
        if len(all_data) == 0:
            raise RuntimeError("No data available")
        
        self.price_data = pd.DataFrame(all_data)
        self.price_data = self.price_data.dropna(thresh=len(self.price_data)*0.7, axis=1)
        self.returns_data = self.price_data.pct_change().dropna()
        
        print(f"  Dataset: {self.price_data.shape[1]} stocks, {len(self.price_data)} days")
        return self.price_data
    
    def calculate_volatility_regime(self):
        """Calculate volatility regime using Z-scores"""
        print("\n[2/8] Calculating volatility regime...")
        
        portfolio_returns = self.returns_data.mean(axis=1)
        rolling_vol = portfolio_returns.rolling(window=self.vol_window).std() * np.sqrt(252)
        
        # Rolling 252-day (1 year) window for mean/std
        vol_mean = rolling_vol.rolling(window=252, min_periods=63).mean()
        vol_std = rolling_vol.rolling(window=252, min_periods=63).std()
        
        vol_std = vol_std.replace(0, np.nan)
        vol_z_score = (rolling_vol - vol_mean) / vol_std
        vol_z_score = vol_z_score.fillna(0)
        
        high_vol_regime = (vol_z_score > self.vol_z_high).astype(int)
        
        print(f"  Vol Z-score mean: {vol_z_score.mean():.2f}")
        print(f"  High-vol periods: {high_vol_regime.sum()/len(high_vol_regime):.1%}")
        
        self.volatility_regime = pd.DataFrame({
            'rolling_vol': rolling_vol,
            'vol_mean': vol_mean,
            'vol_std': vol_std,
            'vol_z_score': vol_z_score,
            'high_vol_regime': high_vol_regime
        })
        
        return self.volatility_regime
    
    def get_position_multiplier(self, date):
        """Get dynamic position size based on volatility regime"""
        if date not in self.volatility_regime.index:
            return 1.0
        
        vol_z = self.volatility_regime.loc[date, 'vol_z_score']
        
        if pd.isna(vol_z):
            return 1.0
        
        # Dynamic sizing based on volatility Z-score
        if vol_z <= self.vol_z_low:
            return 1.0  # Normal regime
        elif vol_z >= self.vol_z_high:
            return 0.5  # High volatility regime - reduce exposure
        else:
            # Linear interpolation between thresholds
            ratio = (vol_z - self.vol_z_low) / (self.vol_z_high - self.vol_z_low)
            return 1.0 - 0.5 * ratio
    
    def calculate_z_scores(self, start_date, end_date):
        """Calculate Z-scores for momentum signals"""
        mask = (self.returns_data.index >= start_date) & (self.returns_data.index <= end_date)
        period_returns = self.returns_data[mask]
        
        momentum_scores = (1 + period_returns).prod() - 1
        momentum_scores = momentum_scores.dropna()
        
        mean = momentum_scores.mean()
        std = momentum_scores.std()
        
        if std == 0:
            return pd.Series(dtype=float)
        
        z_scores = (momentum_scores - mean) / std
        return z_scores
    
    def form_portfolios(self, z_scores):
        """Form winner/loser portfolios using Z-score filtering"""
        strong_signals = z_scores[abs(z_scores) > self.z_score_threshold]
        
        if len(strong_signals) < 2:
            return [], []
        
        sorted_signals = strong_signals.sort_values(ascending=False)
        n_select = max(1, int(len(sorted_signals) * 0.10))
        
        winners = sorted_signals.head(n_select).index.tolist()
        losers = sorted_signals.tail(n_select).index.tolist()
        
        return winners, losers
    
    def calculate_turnover(self, new_winners, new_losers):
        """Calculate portfolio turnover"""
        new_positions = set(new_winners + new_losers)
        old_positions = set(self.previous_positions.keys())
        
        if len(old_positions) == 0:
            turnover = 1.0
        else:
            changed = len(new_positions.symmetric_difference(old_positions))
            total = max(len(new_positions), len(old_positions))
            turnover = changed / total if total > 0 else 0
        
        self.previous_positions = {ticker: 'winner' for ticker in new_winners}
        self.previous_positions.update({ticker: 'loser' for ticker in new_losers})
        
        return turnover
    
    def calculate_portfolio_returns(self, stocks, start_date, end_date, position_multiplier):
        """Calculate portfolio returns with dynamic position sizing"""
        mask = (self.returns_data.index >= start_date) & (self.returns_data.index <= end_date)
        period_returns = self.returns_data[mask][stocks]
        
        # Apply position multiplier
        adjusted_return = period_returns.mean(axis=1).mean() * position_multiplier
        return adjusted_return
    
    def run_backtest(self):
        """Execute backtest with regime-aware sizing"""
        print("\n[3/8] Running backtest...")
        
        returns_dates = self.returns_data.index
        current_date = returns_dates[126]
        end_backtest = returns_dates[-63]
        
        month_count = 0
        
        while current_date <= end_backtest:
            formation_end = current_date
            formation_start = formation_end - pd.DateOffset(months=self.formation_months)
            holding_start = formation_end
            holding_end = holding_start + pd.DateOffset(months=self.holding_months)
            
            if holding_end > returns_dates[-1]:
                break
            
            z_scores = self.calculate_z_scores(formation_start, formation_end)
            
            if len(z_scores) < 10:
                current_date += pd.DateOffset(months=1)
                continue
            
            winners, losers = self.form_portfolios(z_scores)
            
            if len(winners) == 0 or len(losers) == 0:
                current_date += pd.DateOffset(months=1)
                continue
            
            # Get dynamic position multiplier
            position_multiplier = self.get_position_multiplier(holding_start)
            
            vol_z_score = self.volatility_regime.loc[holding_start, 'vol_z_score'] if holding_start in self.volatility_regime.index else 0
            
            turnover = self.calculate_turnover(winners, losers)
            
            winner_return = self.calculate_portfolio_returns(winners, holding_start, holding_end, position_multiplier)
            loser_return = self.calculate_portfolio_returns(losers, holding_start, holding_end, position_multiplier)
            
            gross_return = winner_return - loser_return
            transaction_cost = turnover * (self.transaction_cost_bps / 10000)
            net_return = gross_return - transaction_cost
            
            self.results.append({
                'formation_start': formation_start,
                'formation_end': formation_end,
                'holding_start': holding_start,
                'holding_end': holding_end,
                'winner_return': winner_return,
                'loser_return': loser_return,
                'gross_return': gross_return,
                'turnover': turnover,
                'transaction_cost': transaction_cost,
                'net_return': net_return,
                'n_winners': len(winners),
                'n_losers': len(losers),
                'avg_winner_zscore': z_scores[winners].mean() if len(winners) > 0 else 0,
                'avg_loser_zscore': z_scores[losers].mean() if len(losers) > 0 else 0,
                'position_size': position_multiplier,  # DYNAMIC
                'vol_z_score': vol_z_score
            })
            
            month_count += 1
            if month_count % 6 == 0:
                print(f"  Progress: {month_count} periods")
            
            current_date += pd.DateOffset(months=1)
        
        self.results_df = pd.DataFrame(self.results)
        print(f"  Complete: {len(self.results_df)} periods")
        return self.results_df
    
    def calculate_max_drawdown(self, cumulative_returns):
        """Calculate maximum drawdown"""
        running_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - running_max) / running_max
        return drawdown.min()
    
    def analyze_performance(self):
        """Calculate performance metrics"""
        print("\n[4/8] Analyzing performance...")
        
        avg_net = self.results_df['net_return'].mean()
        std_net = self.results_df['net_return'].std()
        sharpe = (avg_net / std_net * np.sqrt(12)) if std_net > 0 else 0
        
        cumulative_net = (1 + self.results_df['net_return']).cumprod()
        max_dd = self.calculate_max_drawdown(cumulative_net)
        
        annual_return = avg_net * 12
        win_rate = (self.results_df['net_return'] > 0).mean()
        avg_position_size = self.results_df['position_size'].mean()
        
        print("\n" + "=" * 70)
        print("V2 PERFORMANCE (REGIME-AWARE SIZING)")
        print("=" * 70)
        print(f"Annual Return:      {annual_return:.2%}")
        print(f"Sharpe Ratio:       {sharpe:.2f}")
        print(f"Max Drawdown:       {max_dd:.2%}")
        print(f"Win Rate:           {win_rate:.1%}")
        print(f"Avg Position Size:  {avg_position_size:.2f}x")
        
        self.performance_metrics = {
            'annual_return': annual_return,
            'sharpe_ratio': sharpe,
            'max_drawdown': max_dd,
            'win_rate': win_rate,
            'avg_position_size': avg_position_size
        }
        
        return self.performance_metrics
    
    def create_visualizations(self):
        """Generate charts"""
        print("\n[5/8] Creating visualizations...")
        
        fig = plt.figure(figsize=(15, 10))
        
        dates = pd.to_datetime(self.results_df['holding_end'])
        cumulative = (1 + self.results_df['net_return']).cumprod()
        
        # 1. Cumulative Performance
        ax1 = plt.subplot(2, 2, 1)
        ax1.plot(dates, cumulative.values, linewidth=2, color='darkgreen')
        ax1.axhline(y=1, color='black', linestyle='--', alpha=0.3)
        ax1.set_title('V2: Cumulative Performance', fontweight='bold')
        ax1.set_ylabel('Cumulative Return')
        ax1.grid(True, alpha=0.3)
        
        # 2. Dynamic Position Sizing
        ax2 = plt.subplot(2, 2, 2)
        ax2.plot(dates, self.results_df['position_size'].values, linewidth=2, color='orange')
        ax2.axhline(y=1.0, color='blue', linestyle='--', alpha=0.5, label='Full')
        ax2.axhline(y=0.5, color='red', linestyle='--', alpha=0.5, label='Reduced')
        ax2.set_title('V2: Dynamic Position Sizing', fontweight='bold')
        ax2.set_ylabel('Position Multiplier')
        ax2.set_ylim([0.4, 1.1])
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 3. Volatility Z-Score
        ax3 = plt.subplot(2, 2, 3)
        ax3.plot(dates, self.results_df['vol_z_score'].values, linewidth=2, color='navy')
        ax3.axhline(y=self.vol_z_low, color='green', linestyle='--', alpha=0.5, label=f'Low ({self.vol_z_low})')
        ax3.axhline(y=self.vol_z_high, color='red', linestyle='--', alpha=0.5, label=f'High ({self.vol_z_high})')
        ax3.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        ax3.set_title('V2: Volatility Z-Score', fontweight='bold')
        ax3.set_ylabel('Z-Score')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. Drawdown
        ax4 = plt.subplot(2, 2, 4)
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        ax4.fill_between(dates, drawdown.values, 0, alpha=0.5, color='red')
        ax4.set_title('V2: Drawdown', fontweight='bold')
        ax4.set_ylabel('Drawdown')
        ax4.grid(True, alpha=0.3)
        
        plt.suptitle('Momentum Strategy V2 - Regime-Aware', fontsize=14, fontweight='bold')
        plt.tight_layout()
        
        os.makedirs('results_v2', exist_ok=True)
        plt.savefig('results_v2/performance_v2.png', dpi=300, bbox_inches='tight')
        print("  Chart saved: results_v2/performance_v2.png")
        plt.close()
    
    def save_results(self):
        """Save results"""
        print("\n[6/8] Saving results...")
        
        os.makedirs('results_v2', exist_ok=True)
        
        self.results_df.to_csv('results_v2/trades_v2.csv', index=False)
        print("  Trades saved")
        
        summary = pd.DataFrame({
            'Metric': list(self.performance_metrics.keys()),
            'Value': list(self.performance_metrics.values())
        })
        summary.to_csv('results_v2/summary_v2.csv', index=False)
        print("  Summary saved")
        
        self.volatility_regime.to_csv('results_v2/volatility_regime.csv')
        print("  Volatility regime saved")
    
    def run_complete_analysis(self):
        """Run complete analysis"""
        print("\n[7/8] Running complete V2 analysis...")
        
        try:
            self.fetch_data()
            self.calculate_volatility_regime()
            self.run_backtest()
            self.analyze_performance()
            self.create_visualizations()
            self.save_results()
            
            print("\n" + "=" * 70)
            print("V2 ANALYSIS COMPLETE")
            print("=" * 70)
            print("\nRegime Detection:")
            print("  - Volatility Z-score based position sizing")
            print("  - Dynamic exposure: 0.5x - 1.0x")
            print("  - Reduces risk during high volatility periods")
            
            return self.results_df, self.performance_metrics
            
        except Exception as e:
            print(f"\nError: {str(e)}")
            raise


def main():
    """Main execution"""
    print("\n" + "=" * 70)
    print("MOMENTUM STRATEGY V2 - REGIME-AWARE IMPLEMENTATION")
    print("=" * 70)
    
    strategy = MomentumStrategyV2()
    strategy.run_complete_analysis()


if __name__ == "__main__":
    main()
