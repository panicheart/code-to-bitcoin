# 加密货币市场情绪追踪器

## 快速开始

### 安装依赖

```bash
pip install pandas numpy requests
```

### 运行演示

```bash
python sentiment_tracker.py
```

### 在项目中使用

```python
from sentiment_tracker import CryptoSentimentTracker, fetch_coingecko_price

# 初始化追踪器
tracker = CryptoSentimentTracker()

# 获取实时情绪分析
result = tracker.get_comprehensive_sentiment()
print(f"当前情绪: {result['overall']} ({result['score']}/100)")
print(f"交易信号: {result['signal']}")

# 获取比特币价格数据
prices = fetch_coingecko_price('bitcoin', days=30)

# 使用真实数据进行分析
real_data = {
    'social': {
        'positive_mentions': 15000,
        'negative_mentions': 6000,
        'total_mentions': 50000
    },
    'search': {
        'buy_bitcoin': [40, 45, 50, 55, 60],
        'crypto_crash': [35, 30, 25, 20, 15],
        'altcoin_season': [20, 25, 35, 45, 55]
    },
    'onchain': {
        'exchange_netflow': -3000,
        'lth_supply_change': 1.2,
        'sopr': 1.05
    },
    'price_history': prices
}

result = tracker.get_comprehensive_sentiment(real_data)
```

## 文件说明

- `sentiment_tracker.py` - 核心分析引擎
- `README.md` - 完整文档和理论说明
- `dashboard.html` - 可视化仪表盘模板
- `demo.py` - 交互式演示脚本

## 自定义配置

```python
# 调整权重
tracker.weights = {
    'social': 0.40,      # 更看重社交媒体
    'search': 0.20,
    'onchain': 0.25,
    'volatility': 0.15
}

# 导出报告
report_path = tracker.export_report('my_report.json')
```

## 数据源接入

### 社交媒体
- Twitter API v2
- LunarCrush API
- Santiment

### 搜索趋势
- Google Trends (pytrends)

### 链上数据
- Glassnode API
- CryptoQuant
- Dune Analytics

### 价格数据
- CoinGecko API
- Binance API

## 许可

CC BY-NC-SA 4.0 - 创意共享署名-非商业性使用-相同方式共享
