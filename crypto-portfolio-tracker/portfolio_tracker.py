"""
加密货币投资组合追踪器 v1.0
Crypto Portfolio Tracker

一个简洁的多币种投资组合管理工具
"""

import json
import csv
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class Asset:
    """单个资产持仓"""
    symbol: str
    name: str
    quantity: float
    avg_buy_price: float
    
    def __post_init__(self):
        self.symbol = self.symbol.upper()


class CryptoPortfolioTracker:
    """
    加密货币投资组合追踪器
    
    使用方法:
        tracker = CryptoPortfolioTracker()
        tracker.add_asset('BTC', 'Bitcoin', 0.5, 45000)
        summary = tracker.get_portfolio_summary()
    """
    
    def __init__(self):
        self.assets: Dict[str, Asset] = {}
        self.transactions: List[Dict] = []
    
    def add_asset(self, symbol: str, name: str, quantity: float, 
                  buy_price: float, date: str = None) -> None:
        """添加新资产或更新现有资产"""
        symbol = symbol.upper()
        date = date or datetime.now().strftime('%Y-%m-%d')
        
        if symbol in self.assets:
            existing = self.assets[symbol]
            total_qty = existing.quantity + quantity
            total_cost = (existing.quantity * existing.avg_buy_price + 
                         quantity * buy_price)
            existing.avg_buy_price = total_cost / total_qty
            existing.quantity = total_qty
        else:
            self.assets[symbol] = Asset(
                symbol=symbol, name=name, quantity=quantity, 
                avg_buy_price=buy_price
            )
        
        self.transactions.append({
            'date': date, 'symbol': symbol, 'type': 'BUY',
            'quantity': quantity, 'price': buy_price,
            'total': quantity * buy_price
        })
    
    def remove_asset(self, symbol: str, quantity: float = None) -> None:
        """移除或减仓资产"""
        symbol = symbol.upper()
        
        if symbol not in self.assets:
            print(f"错误: 未持有 {symbol}")
            return
        
        asset = self.assets[symbol]
        
        if quantity is None or quantity >= asset.quantity:
            removed_qty = asset.quantity
            del self.assets[symbol]
        else:
            asset.quantity -= quantity
            removed_qty = quantity
        
        self.transactions.append({
            'date': datetime.now().strftime('%Y-%m-%d'),
            'symbol': symbol, 'type': 'SELL',
            'quantity': removed_qty, 'price': 0, 'total': 0
        })
    
    def get_portfolio_summary(self) -> Dict:
        """获取投资组合汇总"""
        mock_prices = {
            'BTC': 84750.50, 'ETH': 2850.75, 'SOL': 145.30,
            'ADA': 0.85, 'DOT': 7.50, 'AVAX': 35.20,
            'MATIC': 0.65, 'LINK': 18.50, 'UNI': 9.80
        }
        
        total_invested = 0
        total_current = 0
        assets_detail = []
        
        for symbol, asset in self.assets.items():
            current_price = mock_prices.get(symbol, asset.avg_buy_price)
            invested = asset.quantity * asset.avg_buy_price
            current = asset.quantity * current_price
            pnl = current - invested
            pnl_pct = (pnl / invested * 100) if invested > 0 else 0
            
            total_invested += invested
            total_current += current
            
            assets_detail.append({
                'symbol': symbol, 'name': asset.name,
                'quantity': asset.quantity,
                'avg_price': asset.avg_buy_price,
                'current_price': current_price,
                'invested': invested, 'current_value': current,
                'pnl': pnl, 'pnl_pct': pnl_pct
            })
        
        total_pnl = total_current - total_invested
        total_pnl_pct = ((total_pnl / total_invested) * 100) if total_invested else 0
        
        return {
            'total_invested': total_invested,
            'total_current_value': total_current,
            'total_pnl': total_pnl, 'total_pnl_pct': total_pnl_pct,
            'assets': assets_detail, 'asset_count': len(self.assets)
        }
    
    def export_to_csv(self, filename: str = 'portfolio.csv'):
        """导出到CSV"""
        summary = self.get_portfolio_summary()
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Symbol', 'Name', 'Quantity', 'Avg Buy Price', 
                           'Current Price', 'Invested', 'Current Value', 'P&L', 'P&L%'])
            for asset in summary['assets']:
                writer.writerow([
                    asset['symbol'], asset['name'], f"{asset['quantity']:.4f}",
                    f"${asset['avg_price']:,.2f}", f"${asset['current_price']:,.2f}",
                    f"${asset['invested']:,.2f}", f"${asset['current_value']:,.2f}",
                    f"${asset['pnl']:,.2f}", f"{asset['pnl_pct']:+.2f}%"
                ])
            writer.writerow([])
            writer.writerow(['TOTAL', '', '', '', '', 
                           f"${summary['total_invested']:,.2f}",
                           f"${summary['total_current_value']:,.2f}",
                           f"${summary['total_pnl']:,.2f}",
                           f"{summary['total_pnl_pct']:+.2f}%"])
    
    def save_to_json(self, filename: str = 'portfolio.json'):
        """保存到JSON"""
        data = {
            'assets': [asdict(a) for a in self.assets.values()],
            'transactions': self.transactions,
            'saved_at': datetime.now().isoformat()
        }
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_from_json(self, filename: str = 'portfolio.json'):
        """从JSON加载"""
        with open(filename, 'r') as f:
            data = json.load(f)
        self.assets = {a['symbol']: Asset(**a) for a in data['assets']}
        self.transactions = data.get('transactions', [])


def print_portfolio_table(summary: Dict):
    """打印投资组合表格"""
    print("\n" + "=" * 80)
    print(f"{'Symbol':<8} {'Name':<12} {'Qty':<10} {'Avg Price':<12} "
          f"{'Current':<12} {'Value':<14} {'P&L':<14}")
    print("-" * 80)
    
    for asset in summary['assets']:
        pnl_str = f"${asset['pnl']:,.2f} ({asset['pnl_pct']:+.1f}%)"
        print(f"{asset['symbol']:<8} {asset['name']:<12} "
              f"{asset['quantity']:<10.4f} ${asset['avg_price']:<11,.2f} "
              f"${asset['current_price']:<11,.2f} ${asset['current_value']:<13,.2f} "
              f"{pnl_str}")
    
    print("-" * 80)
    total_pnl_str = f"${summary['total_pnl']:,.2f} ({summary['total_pnl_pct']:+.1f}%)"
    print(f"{'TOTAL':<8} {'':<12} {'':<10} {'':<12} "
          f"{'':<12} ${summary['total_current_value']:<13,.2f} {total_pnl_str}")
    print("=" * 80)


if __name__ == "__main__":
    tracker = CryptoPortfolioTracker()
    
    # 添加示例持仓
    tracker.add_asset('BTC', 'Bitcoin', 0.5, 45000)
    tracker.add_asset('ETH', 'Ethereum', 4.0, 2500)
    tracker.add_asset('SOL', 'Solana', 25.0, 120)
    tracker.add_asset('ADA', 'Cardano', 5000.0, 0.75)
    
    # 获取汇总
    summary = tracker.get_portfolio_summary()
    
    # 打印报告
    print("\n" + "💰" * 20)
    print("\n     加密货币投资组合追踪器 v1.0")
    print("\n" + "💰" * 20)
    
    print(f"\n📊 投资概览:")
    print(f"   总投资:    ${summary['total_invested']:,.2f}")
    print(f"   当前价值:  ${summary['total_current_value']:,.2f}")
    
    pnl_emoji = "🟢" if summary['total_pnl'] >= 0 else "🔴"
    print(f"   总盈亏:    {pnl_emoji} ${summary['total_pnl']:,.2f} ({summary['total_pnl_pct']:+.2f}%)")
    
    print(f"\n📈 持仓详情:")
    print_portfolio_table(summary)
    
    # 导出
    tracker.export_to_csv()
    print(f"\n📁 已导出到 portfolio.csv")
    
    tracker.save_to_json()
    print(f"📁 已保存到 portfolio.json")
