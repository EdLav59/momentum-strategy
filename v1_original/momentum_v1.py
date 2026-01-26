"""
Momentum Trading Strategy - Version 1 (Original)
Based on Jegadeesh & Titman (1993)

Original implementation with constant volatility assumption.
No adjustment for market regime changes.

LIMITATION: This strategy suffered significant drawdowns during 
high-volatility periods in 2024 (French political uncertainty).

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

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")


class MomentumStrategyV1:
    """
    Original Momentum Strategy - No Regime Detection
    
    Configuration:
    - Formation Period: 12 months
    - Holding Period: 6 months
    - Top/Bottom: 20% (quintile portfolios)
    - Rebalancing: Monthly
    - Position Sizing: CONSTANT (equal-weighted, no volatility adjustment)
    """
    
    def __init__(self):
        # Dates
        self.end_date = '2024-12-31'
        self.start_date = '2019-01-01'
        
        # Universe: European large-cap stocks (CAC 40 + DAX 30)
        self.tickers = [
            # CAC 40 - France (Paris Exchange)
            'AI.PA',      # Air Liquide
            'AIR.PA',     # Airbus
            'ALO.PA',     # Alstom
            'MT.AS',      # ArcelorMittal
            'CS.PA',      # AXA
            'BNP.PA',     # BNP Paribas
            'EN.PA',      # Bouygues
            'CAP.PA',     # Capgemini
            'CA.PA',      # Carrefour
            'ACA.PA',     # Credit Agricole
            'BN.PA',      # Danone
            'ENGI.PA',    # ENGIE
            'EL.PA',      # EssilorLuxottica
            'RMS.PA',     # Hermes
            'KER.PA',     # Kering
            'OR.PA',      # L'Oreal
            'LR.PA',      # Legrand
            'MC.PA',      # LVMH
            'ML.PA',      # Michelin
            'ORA.PA',     # Orange
            'RI.PA',      # Pernod Ricard
            'PUB.PA',     # Publicis
            'RNO.PA',     # Renault
            'SAF.PA',     # Safran
            'SGO.PA',     # Saint-Gobain
            'SAN.PA',     # Sanofi
            'SU.PA',      # Schneider Electric
            'GLE.PA',     # Societe Generale
            'STLAP.PA',   # Stellantis
            'STMPA.PA',   # STMicroelectronics
            'TEP.PA',     # Teleperformance
            'HO.PA',      # Thales
            'TTE.PA',      # TotalEnergies
            'URW.PA',     # Unibail-Rodamco-Westfield
            'VIE.PA',     # Veolia
            'DG.PA',      # Vinci
            'VIV.PA',     # Vivendi
            
            # DAX 30 - Germany (Frankfurt Exchange)
            'ADS.DE',     # Adidas
            'ALV.DE',     # Allianz
            'BAS.DE',     # BASF
            'BAYN.DE',    # Bayer
            'BMW.DE',     # BMW
            'CON.DE',     # Continental
            'MBG.DE',     # Daimler (Mercedes-Benz)
            '1COV.DE',    # Covestro
            'DB1.DE',     # Deutsche Boerse
            'DBK.DE',     # Deutsche Bank
            'DHL.DE',     # Deutsche Post
            'DTE.DE',     # Deutsche Telekom
            'EOAN.DE',    # E.ON
            'FRE.DE',     # Fresenius
            'HEI.DE',     # HeidelbergCement
            'HEN3.DE',    # Henkel
            'IFX.DE',     # Infineon
            'LIN.DE',     # Linde
            'MRK.DE',     # Merck KGaA
            'MTX.DE',     # MTU Aero Engines
            'MUV2.DE',    # Munich Re
            'RWE.DE',     # RWE
            'SAP.DE',     # SAP
            'SIE.DE',     # Siemens
            'VOW3.DE',    # Volkswagen
            'VNA.DE',     # Vonovia
        ]
        
        # Strategy parameters
        self.formation_months = 12
        self.holding_months = 6
        self.top_percentile = 20
        self.bottom_percentile = 20
        
        # Data storage
        self.price_data = None
        self.returns_data = None
        self.results = []
        
        print("=" * 70)
        print("MOMENTUM STRATEGY V1 - ORIGINAL (NO REGIME DETECTION)")
        print("=" * 70)
        print(f"Period: {self.start_date} to {self.end_date}")
        print(f"Universe: {len(self.tickers)} large-cap European stocks (CAC 40 + DAX)")
        print(f"Formation Period: {self.formation_months} months")
        print(f"Holding Period: {self.holding_months} months")
        print(f"IMPORTANT: This version assumes CONSTANT volatility")
        print("=" * 70)
    
    def fetch_data(self):
        """Download historical price data from Yahoo Finance"""
        print("\n[1/6] Fetching historical data...")
        print("  Downloading stocks one by one (this takes 10-15 minutes)...")
        
        all_data = {}
        success_count = 0
        
        for ticker in self.tickers:
            try:
                # Create ticker object
                stock = yf.Ticker(ticker)
                
                # Get historical data using history() method instead of download()
                hist = stock.history(start=self.start_date, end=self.end_date, auto_adjust=True)
                
                if not hist.empty and len(hist) > 100:  # At least 100 days of data
                    all_data[ticker] = hist['Close']
                    success_count += 1
                    if success_count % 10 == 0:
                        print(f"  Downloaded {success_count}/{len(self.tickers)} stocks...")
            except Exception as e:
                continue
        
        if len(all_data) == 0:
            raise RuntimeError("No price data available")
        
        self.price_data = pd.DataFrame(all_data)
        
        # Clean data
        initial_stocks = self.price_data.shape[1]
        self.price_data = self.price_data.dropna(thresh=len(self.price_data)*0.7, axis=1)
        removed = initial_stocks - self.price_data.shape[1]
        
        if removed > 0:
            print(f"  Removed {removed} stocks due to insufficient data")
        
        if self.price_data.empty or self.price_data.shape[1] == 0:
            raise RuntimeError("No price data available")
        
        print(f"Data loaded: {self.price_data.shape[1]} stocks, {len(self.price_data)} days")
        
        # Calculate returns
        self.returns_data = self.price_data.pct_change().dropna()
        
        return self.price_data
    
    def calculate_momentum_scores(self, start_date, end_date):
        """Calculate momentum scores for formation period"""
        mask = (self.returns_data.index >= start_date) & (self.returns_data.index <= end_date)
        period_returns = self.returns_data[mask]
        
        # Cumulative returns = momentum scores
        momentum_scores = (1 + period_returns).prod() - 1
        momentum_scores = momentum_scores.dropna()
        
        return momentum_scores
    
    def form_portfolios(self, momentum_scores):
        """Form winner and loser portfolios"""
        n_stocks = len(momentum_scores)
        n_winners = max(1, int(n_stocks * self.top_percentile / 100))
        n_losers = max(1, int(n_stocks * self.bottom_percentile / 100))
        
        sorted_scores = momentum_scores.sort_values(ascending=False)
        
        winners = sorted_scores.head(n_winners).index.tolist()
        losers = sorted_scores.tail(n_losers).index.tolist()
        
        return winners, losers
    
    def calculate_portfolio_returns(self, stocks, start_date, end_date):
        """Calculate equal-weighted portfolio returns"""
        mask = (self.returns_data.index >= start_date) & (self.returns_data.index <= end_date)
        period_returns = self.returns_data[mask][stocks]
        
        # Equal-weighted - NO VOLATILITY ADJUSTMENT
        portfolio_return = period_returns.mean(axis=1).mean()
        
        return portfolio_return
    
    def run_backtest(self):
        """Execute backtest"""
        print("\n[2/6] Running backtest (constant position sizing)...")
        
        returns_dates = self.returns_data.index
        current_date = returns_dates[252]  # Start after 1 year
        end_backtest = returns_dates[-126]  # Stop 6 months before end
        
        month_count = 0
        
        while current_date <= end_backtest:
            formation_end = current_date
            formation_start = formation_end - pd.DateOffset(months=self.formation_months)
            
            holding_start = formation_end
            holding_end = holding_start + pd.DateOffset(months=self.holding_months)
            
            if holding_end > returns_dates[-1]:
                break
            
            momentum_scores = self.calculate_momentum_scores(formation_start, formation_end)
            
            if len(momentum_scores) < 10:
                current_date += pd.DateOffset(months=1)
                continue
            
            winners, losers = self.form_portfolios(momentum_scores)
            
            winner_return = self.calculate_portfolio_returns(winners, holding_start, holding_end)
            loser_return = self.calculate_portfolio_returns(losers, holding_start, holding_end)
            momentum_return = winner_return - loser_return
            
            self.results.append({
                'formation_start': formation_start,
                'formation_end': formation_end,
                'holding_start': holding_start,
                'holding_end': holding_end,
                'winner_return': winner_return,
                'loser_return': loser_return,
                'momentum_return': momentum_return,
                'n_winners': len(winners),
                'n_losers': len(losers),
                'position_size': 1.0  # CONSTANT
            })
            
            month_count += 1
            if month_count % 6 == 0:
                print(f"  Processed {month_count} periods...")
            
            current_date += pd.DateOffset(months=1)
        
        self.results_df = pd.DataFrame(self.results)
        print(f"Backtest complete: {len(self.results_df)} periods analyzed")
        
        return self.results_df
    
    def calculate_max_drawdown(self, cumulative_returns):
        """Calculate maximum drawdown"""
        running_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - running_max) / running_max
        max_dd = drawdown.min()
        return max_dd
    
    def analyze_performance(self):
        """Calculate performance metrics"""
        print("\n[3/6] Analyzing performance...")
        
        # Basic stats
        avg_return = self.results_df['momentum_return'].mean()
        std_return = self.results_df['momentum_return'].std()
        sharpe_ratio = (avg_return / std_return * np.sqrt(12)) if std_return > 0 else 0
        
        # Cumulative returns
        cumulative = (1 + self.results_df['momentum_return']).cumprod()
        max_dd = self.calculate_max_drawdown(cumulative)
        
        # Calmar ratio
        annual_return = avg_return * 12
        calmar = annual_return / abs(max_dd) if max_dd != 0 else 0
        
        # Statistical significance
        t_stat, p_value = stats.ttest_1samp(self.results_df['momentum_return'], 0)
        win_rate = (self.results_df['momentum_return'] > 0).mean()
        
        print("\n" + "=" * 60)
        print("V1 PERFORMANCE SUMMARY (CONSTANT VOLATILITY ASSUMPTION)")
        print("=" * 60)
        print(f"\nAnnualized Metrics:")
        print(f"  Return:        {annual_return:.2%}")
        print(f"  Volatility:    {std_return*np.sqrt(12):.2%}")
        print(f"  Sharpe Ratio:  {sharpe_ratio:.4f}")
        print(f"  Max Drawdown:  {max_dd:.2%}")
        print(f"  Calmar Ratio:  {calmar:.4f}")
        print(f"  Win Rate:      {win_rate:.2%}")
        print(f"\nNOTE: This version suffered during 2024 volatility spikes")
        
        self.performance_metrics = {
            'annual_return': annual_return,
            'annual_volatility': std_return*np.sqrt(12),
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_dd,
            'calmar_ratio': calmar,
            'win_rate': win_rate
        }
        
        return self.performance_metrics
    
    def create_visualizations(self):
        """Generate performance charts"""
        print("\n[4/6] Creating visualizations...")
        
        fig = plt.figure(figsize=(18, 10))
        
        # 1. Cumulative Returns with 2024 highlight
        ax1 = plt.subplot(2, 3, 1)
        cumulative = (1 + self.results_df['momentum_return']).cumprod()
        dates = pd.to_datetime(self.results_df['holding_end'])
        
        ax1.plot(dates, cumulative.values, linewidth=2.5, color='darkblue', label='Momentum Strategy')
        ax1.axhline(y=1, color='black', linestyle='--', alpha=0.3)
        
        # Highlight 2024 period
        mask_2024 = dates.dt.year == 2024
        if mask_2024.any():
            ax1.axvspan(dates[mask_2024].min(), dates[mask_2024].max(), 
                       alpha=0.2, color='red', label='2024 Volatility Period')
        
        ax1.set_title('V1: Cumulative Performance', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Cumulative Return')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. Drawdown Analysis
        ax2 = plt.subplot(2, 3, 2)
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        
        ax2.fill_between(dates, drawdown.values, 0, alpha=0.5, color='red')
        ax2.set_title('V1: Drawdown Over Time', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Drawdown')
        ax2.grid(True, alpha=0.3)
        
        # 3. Monthly Returns Distribution
        ax3 = plt.subplot(2, 3, 3)
        ax3.hist(self.results_df['momentum_return'], bins=25, alpha=0.7, 
                color='navy', edgecolor='black')
        ax3.axvline(0, color='red', linestyle='--', linewidth=2)
        ax3.set_title('V1: Returns Distribution', fontsize=12, fontweight='bold')
        ax3.set_xlabel('Monthly Return')
        ax3.set_ylabel('Frequency')
        ax3.grid(True, alpha=0.3)
        
        # 4. Rolling Sharpe Ratio
        ax4 = plt.subplot(2, 3, 4)
        rolling_mean = self.results_df['momentum_return'].rolling(12).mean()
        rolling_std = self.results_df['momentum_return'].rolling(12).std()
        rolling_sharpe = (rolling_mean / rolling_std) * np.sqrt(12)
        
        ax4.plot(dates, rolling_sharpe.values, linewidth=2, color='green')
        ax4.axhline(y=0, color='black', linestyle='--', alpha=0.3)
        ax4.set_title('V1: Rolling 12M Sharpe Ratio', fontsize=12, fontweight='bold')
        ax4.set_ylabel('Sharpe Ratio')
        ax4.grid(True, alpha=0.3)
        
        # 5. Annual Returns
        ax5 = plt.subplot(2, 3, 5)
        self.results_df['year'] = dates.dt.year
        annual_returns = self.results_df.groupby('year')['momentum_return'].apply(
            lambda x: (1 + x).prod() - 1
        )
        
        colors = ['green' if x > 0 else 'red' for x in annual_returns.values]
        bars = ax5.bar(annual_returns.index, annual_returns.values, 
                      color=colors, alpha=0.7, edgecolor='black')
        ax5.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        ax5.set_title('V1: Annual Returns', fontsize=12, fontweight='bold')
        ax5.set_xlabel('Year')
        ax5.set_ylabel('Return')
        ax5.grid(True, alpha=0.3, axis='y')
        
        # Add value labels
        for bar in bars:
            height = bar.get_height()
            ax5.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1%}',
                    ha='center', va='bottom' if height > 0 else 'top',
                    fontsize=9)
        
        # 6. Position Sizing (constant)
        ax6 = plt.subplot(2, 3, 6)
        ax6.plot(dates, self.results_df['position_size'].values, 
                linewidth=2, color='blue', label='Position Size')
        ax6.set_title('V1: Position Sizing (Constant)', fontsize=12, fontweight='bold')
        ax6.set_ylabel('Position Size')
        ax6.set_ylim([0, 1.2])
        ax6.axhline(y=1.0, color='red', linestyle='--', alpha=0.5, label='Fixed at 1.0')
        ax6.legend()
        ax6.grid(True, alpha=0.3)
        
        plt.suptitle('Momentum Strategy V1 - Original (No Regime Detection)', 
                    fontsize=14, fontweight='bold')
        plt.tight_layout()
        
        # Save
        output_dir = 'results_v1'
        os.makedirs(output_dir, exist_ok=True)
        plt.savefig(f'{output_dir}/performance_v1.png', dpi=300, bbox_inches='tight')
        print(f"Chart saved to {output_dir}/performance_v1.png")
        
        plt.close()
    
    def save_results(self):
        """Save results to CSV"""
        print("\n[5/6] Saving results...")
        
        output_dir = 'results_v1'
        os.makedirs(output_dir, exist_ok=True)
        
        # Save trades
        self.results_df.to_csv(f'{output_dir}/trades_v1.csv', index=False)
        print(f"Trades saved to {output_dir}/trades_v1.csv")
        
        # Save summary
        summary = pd.DataFrame({
            'Metric': list(self.performance_metrics.keys()),
            'Value': list(self.performance_metrics.values())
        })
        summary.to_csv(f'{output_dir}/summary_v1.csv', index=False)
        print(f"Summary saved to {output_dir}/summary_v1.csv")
    
    def run_complete_analysis(self):
        """Run complete analysis"""
        print("\n[6/6] Running complete V1 analysis...")
        
        try:
            self.fetch_data()
            self.run_backtest()
            self.analyze_performance()
            self.create_visualizations()
            self.save_results()
            
            print("\n" + "=" * 70)
            print("V1 ANALYSIS COMPLETE")
            print("=" * 70)
            print("\nKey Limitation:")
            print("  This version assumes constant volatility and suffered")
            print("  significant drawdowns during 2024 market turbulence.")
            
            return self.results_df, self.performance_metrics
            
        except Exception as e:
            print(f"\nError in V1 analysis: {str(e)}")
            raise


def main():
    """Main execution"""
    print("\n" + "=" * 70)
    print("MOMENTUM STRATEGY V1 - ORIGINAL IMPLEMENTATION")
    print("=" * 70)
    
    strategy = MomentumStrategyV1()
    strategy.run_complete_analysis()


if __name__ == "__main__":
    main()
