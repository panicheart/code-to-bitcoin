"""
加密货币市场情绪追踪器
Crypto Sentiment Tracker v1.0

一个原创的、可执行的金融市场情绪分析框架
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
from typing import Dict, List, Tuple, Optional
import json


class CryptoSentimentTracker:
    """
    综合加密货币市场情绪分析器
    
    使用方法:
        tracker = CryptoSentimentTracker()
        sentiment = tracker.get_comprehensive_sentiment()
        print(f"当前情绪: {sentiment['overall']}")
    """
    
    def __init__(self):
        self.weights = {
            'social': 0.30,
            'search': 0.25,
            'onchain': 0.25,
            'volatility': 0.20
        }
        self.sentiment_levels = {
            (0, 20): "极度恐惧 (Extreme Fear)",
            (20, 40): "恐惧 (Fear)",
            (40, 60): "中性 (Neutral)",
            (60, 80): "贪婪 (Greed)",
            (80, 100): "极度贪婪 (Extreme Greed)"
        }
    
    # ==================== 1. 社交媒体热度 ====================
    
    def calculate_social_heat(self, mentions_data: Dict) -> float:
        """
        计算社交媒体热度指数 (0-100)
        
        Args:
            mentions_data: {
                'positive_mentions': int,
                'negative_mentions': int,
                'total_mentions': int
            }
        """
        positive = mentions_data.get('positive_mentions', 0)
        negative = mentions_data.get('negative_mentions', 0)
        total = mentions_data.get('total_mentions', 1)
        
        # 情绪净值得分 (-1 到 1)
        net_sentiment = (positive - negative) / total
        
        # 热度因子 (总提及量的对数缩放)
        volume_factor = min(np.log10(total + 1) / 6, 1.0)
        
        # 综合得分映射到 0-100
        raw_score = (net_sentiment + 1) / 2  # 映射到 0-1
        heat_score = raw_score * 50 + volume_factor * 50
        
        return round(min(max(heat_score, 0), 100), 2)
    
    def analyze_twitter_sentiment(self, tweets: List[str]) -> Dict:
        """
        简单的Twitter情绪分析
        
        正面词库和负面词库基于加密货币社区常用语
        """
        positive_words = [
            'moon', 'bull', 'bullish', 'breakout', 'accumulate', 'hodl', 
            'diamond hands', 'pump', ' ATH', 'all time high', 'buy the dip',
            'generational wealth', 'rocket', 'lambo', 'wagmi', 'gm'
        ]
        
        negative_words = [
            'crash', 'bear', 'bearish', 'dump', 'panic', 'sell', 'exit',
            'rug', 'scam', 'dead', 'bottom', 'capitulation', 'paper hands',
            'ngmi', 'rekt', 'liquidated'
        ]
        
        positive_count = sum(1 for tweet in tweets 
                           for word in positive_words if word in tweet.lower())
        negative_count = sum(1 for tweet in tweets 
                           for word in negative_words if word in tweet.lower())
        
        return {
            'positive_mentions': positive_count,
            'negative_mentions': negative_count,
            'total_mentions': len(tweets)
        }
    
    # ==================== 2. 搜索趋势分析 ====================
    
    def calculate_search_momentum(self, trend_data: Dict) -> float:
        """
        计算搜索趋势动量 (0-100)
        
        Args:
            trend_data: {
                'buy_bitcoin': [周搜索量列表],
                'crypto_crash': [周搜索量列表],
                'altcoin_season': [周搜索量列表]
            }
        """
        # 计算各关键词的周环比变化
        def growth_rate(series):
            if len(series) < 2 or series[-2] == 0:
                return 0
            return (series[-1] - series[-2]) / series[-2]
        
        buy_growth = growth_rate(trend_data.get('buy_bitcoin', [0, 0]))
        crash_growth = growth_rate(trend_data.get('crypto_crash', [0, 0]))
        alt_growth = growth_rate(trend_data.get('altcoin_season', [0, 0]))
        
        # 买入兴趣上升 = 看涨信号
        # 崩盘搜索上升 = 看跌信号
        # 山寨季搜索上升 = 风险偏好高
        
        sentiment_score = (
            buy_growth * 40 +           # 买入兴趣权重
            (1 - crash_growth) * 30 +   # 崩盘恐惧反向权重
            alt_growth * 30             # 山寨季热度
        )
        
        # 映射到 0-100
        normalized = (sentiment_score + 1) * 50
        return round(min(max(normalized, 0), 100), 2)
    
    # ==================== 3. 链上数据分析 ====================
    
    def analyze_onchain_signals(self, chain_data: Dict) -> float:
        """
        分析链上信号 (0-100)
        
        Args:
            chain_data: {
                'exchange_netflow': float,  # 正值=流入交易所，负值=流出
                'lth_supply_change': float, # 长期持有者持仓变化%
                'sopr': float               # 花费输出利润率 (>1盈利，<1亏损)
            }
        """
        signals = []
        
        # 信号1: 交易所净流出 = 持有者转移去冷钱包 = 看涨
        netflow = chain_data.get('exchange_netflow', 0)
        if netflow < -1000:  # 大额流出
            signals.append(80)
        elif netflow < 0:
            signals.append(60)
        else:
            signals.append(40)
        
        # 信号2: 长期持有者增持 = 看涨
        lth_change = chain_data.get('lth_supply_change', 0)
        if lth_change > 1:
            signals.append(75)
        elif lth_change > 0:
            signals.append(60)
        else:
            signals.append(45)
        
        # 信号3: SOPR指标
        sopr = chain_data.get('sopr', 1.0)
        if sopr > 1.05:  # 大量获利了结，可能顶部
            signals.append(40)
        elif sopr > 1.0:  # 健康获利
            signals.append(65)
        elif sopr < 0.95:  # 亏损抛售，可能底部
            signals.append(70)
        else:
            signals.append(50)
        
        return round(np.mean(signals), 2)
    
    # ==================== 4. 波动率分析 ====================
    
    def calculate_volatility_sentiment(self, price_data: List[float]) -> float:
        """
        基于波动率的逆向情绪指标 (0-100)
        
        逻辑: 高波动率通常伴随恐惧，低波动率可能预示变盘
        """
        if len(price_data) < 30:
            return 50
        
        # 计算30日波动率
        returns = pd.Series(price_data).pct_change().dropna()
        current_vol = returns.tail(7).std() * np.sqrt(365)  # 年化
        avg_vol = returns.std() * np.sqrt(365)
        
        # 波动率偏离度
        vol_deviation = (current_vol - avg_vol) / avg_vol
        
        # 高波动率 = 恐惧 (低分)
        # 极低波动率 = 压抑后的爆发可能 (中高分)
        if vol_deviation > 0.5:  # 波动率激增
            score = 30
        elif vol_deviation > 0.2:
            score = 45
        elif vol_deviation < -0.3:  # 波动率极低
            score = 65  # 变盘前兆
        else:
            score = 55
        
        return score
    
    # ==================== 综合计算 ====================
    
    def get_comprehensive_sentiment(self, data: Dict = None) -> Dict:
        """
        获取综合市场情绪评分
        
        Args:
            data: 可选的自定义数据，不传则使用示例数据
        
        Returns:
            {
                'overall': str,           # 情绪描述
                'score': float,           # 0-100分数
                'components': Dict,       # 各分项得分
                'signal': str,            # 交易信号
                'timestamp': str
            }
        """
        # 使用示例数据（实际使用时应接入真实API）
        sample_data = data or {
            'social': {
                'positive_mentions': 12500,
                'negative_mentions': 8300,
                'total_mentions': 45000
            },
            'search': {
                'buy_bitcoin': [45, 52, 48, 61, 58],
                'crypto_crash': [30, 35, 42, 38, 33],
                'altcoin_season': [25, 28, 35, 45, 52]
            },
            'onchain': {
                'exchange_netflow': -2500,  # 净流出
                'lth_supply_change': 0.8,   # 长期持有者增持0.8%
                'sopr': 1.02                # 小幅盈利
            },
            'price_history': [42000, 43500, 42800, 45100, 46700, 
                            45800, 47200, 48900, 47600, 49500] * 3
        }
        
        # 计算各分项
        social_score = self.calculate_social_heat(sample_data['social'])
        search_score = self.calculate_search_momentum(sample_data['search'])
        onchain_score = self.analyze_onchain_signals(sample_data['onchain'])
        vol_score = self.calculate_volatility_sentiment(sample_data['price_history'])
        
        # 加权综合
        composite = (
            social_score * self.weights['social'] +
            search_score * self.weights['search'] +
            onchain_score * self.weights['onchain'] +
            vol_score * self.weights['volatility']
        )
        
        # 确定情绪等级
        sentiment_desc = "未知"
        for (low, high), desc in self.sentiment_levels.items():
            if low <= composite < high:
                sentiment_desc = desc
                break
        
        # 生成交易信号
        if composite < 25:
            signal = "🔴 极度恐惧 - 可能是买入机会"
        elif composite < 40:
            signal = "🟠 恐惧 - 考虑分批建仓"
        elif composite < 60:
            signal = "🟡 中性 - 观望或小额参与"
        elif composite < 80:
            signal = "🟢 贪婪 - 考虑获利了结"
        else:
            signal = "🔵 极度贪婪 - 警惕回调风险"
        
        return {
            'overall': sentiment_desc,
            'score': round(composite, 2),
            'components': {
                'social_heat': social_score,
                'search_momentum': search_score,
                'onchain_signals': onchain_score,
                'volatility_sentiment': vol_score
            },
            'signal': signal,
            'timestamp': datetime.now().isoformat()
        }
    
    def export_report(self, output_path: str = None) -> str:
        """
        生成并导出情绪分析报告
        
        Args:
            output_path: 导出路径，默认生成时间戳文件名
        
        Returns:
            报告文件路径
        """
        result = self.get_comprehensive_sentiment()
        
        if output_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = f"sentiment_report_{timestamp}.json"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        return output_path


# ==================== 数据获取辅助函数 ====================

def fetch_coingecko_price(coin_id: str = 'bitcoin', days: int = 30) -> List[float]:
    """
    从CoinGecko获取历史价格数据
    
    Args:
        coin_id: 币种ID (bitcoin, ethereum, etc.)
        days: 获取天数
    
    Returns:
        价格列表
    """
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {'vs_currency': 'usd', 'days': days}
    
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        prices = [p[1] for p in data.get('prices', [])]
        return prices
    except Exception as e:
        print(f"获取价格数据失败: {e}")
        return []


def fetch_fear_greed_index() -> Optional[Dict]:
    """
    获取Alternative.me的恐惧贪婪指数作为对比参考
    
    Returns:
        包含指数值和分类的字典
    """
    url = "https://api.alternative.me/fng/"
    
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        if data.get('data'):
            return {
                'value': int(data['data'][0]['value']),
                'classification': data['data'][0]['value_classification'],
                'timestamp': data['data'][0]['timestamp']
            }
    except Exception as e:
        print(f"获取恐惧贪婪指数失败: {e}")
    
    return None


# ==================== 使用示例 ====================

if __name__ == "__main__":
    print("=" * 60)
    print("🪙 加密货币市场情绪追踪器 v1.0")
    print("=" * 60)
    
    # 初始化追踪器
    tracker = CryptoSentimentTracker()
    
    # 获取综合情绪分析
    result = tracker.get_comprehensive_sentiment()
    
    print(f"\n📊 综合情绪: {result['overall']}")
    print(f"📈 情绪得分: {result['score']}/100")
    
    print(f"\n📋 分项指标:")
    for component, score in result['components'].items():
        bar = "█" * int(score / 5) + "░" * (20 - int(score / 5))
        print(f"   {component:20s} {bar} {score:.1f}")
    
    print(f"\n💡 交易信号: {result['signal']}")
    print(f"\n🕐 生成时间: {result['timestamp']}")
    
    # 对比官方恐惧贪婪指数
    print("\n" + "-" * 60)
    official = fetch_fear_greed_index()
    if official:
        print(f"📊 Alternative.me 官方恐惧贪婪指数: {official['value']} ({official['classification']})")
    
    # 导出报告
    report_path = tracker.export_report()
    print(f"\n📄 报告已导出: {report_path}")
