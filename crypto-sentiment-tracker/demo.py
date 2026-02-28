"""
交互式演示脚本
展示加密货币市场情绪追踪器的各种功能
"""

from sentiment_tracker import CryptoSentimentTracker, fetch_coingecko_price, fetch_fear_greed_index
import json


def print_header(text):
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def demo_basic_usage():
    """基础用法演示"""
    print_header("演示 1: 基础情绪分析")
    
    tracker = CryptoSentimentTracker()
    result = tracker.get_comprehensive_sentiment()
    
    print(f"\n📊 综合情绪: {result['overall']}")
    print(f"📈 情绪得分: {result['score']}/100")
    print(f"\n📋 分项指标:")
    for component, score in result['components'].items():
        bar = "█" * int(score / 5) + "░" * (20 - int(score / 5))
        print(f"   {component:20s} {bar} {score:.1f}")
    print(f"\n💡 交易信号: {result['signal']}")


def demo_custom_weights():
    """自定义权重演示"""
    print_header("演示 2: 自定义权重配置")
    
    tracker = CryptoSentimentTracker()
    
    # 原始权重结果
    print("\n📊 原始权重 (社交媒体30%):")
    result1 = tracker.get_comprehensive_sentiment()
    print(f"   情绪得分: {result1['score']:.1f}")
    
    # 调整权重 - 更看重链上数据
    tracker.weights = {
        'social': 0.15,
        'search': 0.20,
        'onchain': 0.45,  # 链上数据权重提高到45%
        'volatility': 0.20
    }
    
    print("\n📊 调整后权重 (链上数据45%):")
    result2 = tracker.get_comprehensive_sentiment()
    print(f"   情绪得分: {result2['score']:.1f}")


def demo_different_market_conditions():
    """不同市场条件下的情绪分析"""
    print_header("演示 3: 不同市场条件对比")
    
    tracker = CryptoSentimentTracker()
    
    scenarios = [
        {
            'name': '🐻 熊市恐慌',
            'data': {
                'social': {'positive_mentions': 2000, 'negative_mentions': 15000, 'total_mentions': 20000},
                'search': {'buy_bitcoin': [20, 15, 12, 10, 8], 'crypto_crash': [80, 90, 95, 100, 95], 'altcoin_season': [10, 8, 5, 3, 2]},
                'onchain': {'exchange_netflow': 5000, 'lth_supply_change': -2.5, 'sopr': 0.85},
                'price_history': [60000, 58000, 55000, 52000, 48000, 45000, 42000, 40000, 38000, 35000] * 3
            }
        },
        {
            'name': '🐂 牛市狂热',
            'data': {
                'social': {'positive_mentions': 25000, 'negative_mentions': 2000, 'total_mentions': 30000},
                'search': {'buy_bitcoin': [30, 50, 70, 90, 100], 'crypto_crash': [20, 15, 10, 5, 3], 'altcoin_season': [40, 60, 80, 95, 100]},
                'onchain': {'exchange_netflow': -5000, 'lth_supply_change': 3.0, 'sopr': 1.15},
                'price_history': [40000, 42000, 45000, 48000, 52000, 56000, 60000, 65000, 70000, 75000] * 3
            }
        },
        {
            'name': '😴 横盘整理',
            'data': {
                'social': {'positive_mentions': 5000, 'negative_mentions': 5000, 'total_mentions': 12000},
                'search': {'buy_bitcoin': [50, 52, 48, 51, 49], 'crypto_crash': [30, 28, 32, 29, 31], 'altcoin_season': [40, 42, 38, 41, 39]},
                'onchain': {'exchange_netflow': 100, 'lth_supply_change': 0.1, 'sopr': 1.0},
                'price_history': [45000, 45200, 44800, 45100, 44900, 45300, 44700, 45000, 45200, 44900] * 3
            }
        }
    ]
    
    for scenario in scenarios:
        print(f"\n{scenario['name']}:")
        result = tracker.get_comprehensive_sentiment(scenario['data'])
        print(f"   情绪: {result['overall']}")
        print(f"   得分: {result['score']:.1f}/100")
        print(f"   信号: {result['signal']}")


def demo_real_data():
    """使用真实数据演示"""
    print_header("演示 4: 获取真实市场数据")
    
    print("\n🌐 正在获取比特币价格数据...")
    prices = fetch_coingecko_price('bitcoin', days=30)
    
    if prices:
        print(f"   ✓ 获取到 {len(prices)} 个价格数据点")
        print(f"   ✓ 最新价格: ${prices[-1]:,.2f}")
        print(f"   ✓ 30天前价格: ${prices[0]:,.2f}")
        print(f"   ✓ 涨跌幅: {((prices[-1] - prices[0]) / prices[0] * 100):+.2f}%")
    else:
        print("   ✗ 获取失败，使用模拟数据")
    
    print("\n🌐 正在获取官方恐惧贪婪指数...")
    official = fetch_fear_greed_index()
    if official:
        print(f"   ✓ 官方指数: {official['value']} ({official['classification']})")
    else:
        print("   ✗ 获取失败")


def demo_export():
    """导出功能演示"""
    print_header("演示 5: 导出分析报告")
    
    tracker = CryptoSentimentTracker()
    report_path = tracker.export_report()
    
    print(f"\n📄 报告已导出: {report_path}")
    
    # 读取并显示报告内容
    with open(report_path, 'r', encoding='utf-8') as f:
        report = json.load(f)
    
    print(f"\n报告内容预览:")
    print(json.dumps(report, ensure_ascii=False, indent=2)[:500] + "...")


def main():
    """运行所有演示"""
    print("\n" + "🪙" * 30)
    print("\n   加密货币市场情绪追踪器 - 交互式演示")
    print("\n" + "🪙" * 30)
    
    demo_basic_usage()
    demo_custom_weights()
    demo_different_market_conditions()
    demo_real_data()
    demo_export()
    
    print_header("演示完成")
    print("\n💡 提示: 查看 README.md 获取完整文档")
    print("💡 提示: 编辑 sentiment_tracker.py 自定义你的分析逻辑")
    print()


if __name__ == "__main__":
    main()
