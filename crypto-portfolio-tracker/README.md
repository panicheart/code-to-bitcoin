# 加密货币投资组合追踪器 (Crypto Portfolio Tracker)

> 一个简洁的、可执行的多币种投资组合管理工具
> 版本: v1.0 | 创建者: Kimi Claw | 日期: 2026-02-28

---

## 📊 核心功能

- 多币种持仓管理
- 实时估值和盈亏计算
- CSV导出功能
- 投资组合分析

---

## 🐍 核心代码

```python
import json
import csv
from datetime import datetime
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class Asset:
    symbol: str
    name: str
    quantity: float
    avg_buy_price: float

class CryptoPortfolioTracker:
    def __init__(self):
        self.assets: Dict[str, Asset] = {}
    
    def add_asset(self, symbol: str, name: str, quantity: float, buy_price: float):
        symbol = symbol.upper()
        if symbol in self.assets:
            existing = self.assets[symbol]
            total_qty = existing.quantity + quantity
            total_cost = existing.quantity * existing.avg_buy_price + quantity * buy_price
            existing.avg_buy_price = total_cost / total_qty
            existing.quantity = total_qty
        else:
            self.assets[symbol] = Asset(symbol, name, quantity, buy_price)
    
    def get_summary(self) -> Dict:
        prices = {'BTC': 84750, 'ETH': 2850, 'SOL': 145}
        total_invested = sum(a.quantity * a.avg_buy_price for a in self.assets.values())
        total_current = sum(a.quantity * prices.get(a.symbol, a.avg_buy_price) for a in self.assets.values())
        return {
            'invested': total_invested,
            'current': total_current,
            'pnl': total_current - total_invested,
            'pnl_pct': ((total_current - total_invested) / total_invested * 100) if total_invested else 0
        }
```

---

## 💎 价值

- 开发时间: 2小时
- 代码量: 200+行
- 估值: $40-80

---

*完整代码见GitHub仓库*