#!/usr/bin/env python3
"""
AI 内容抓取模块
支持从 RSS feed 抓取最新 AI 资讯
"""

import feedparser
import requests
from datetime import datetime, timedelta
from typing import List, Dict
import yaml
import os


class ContentScraper:
    def __init__(self, config_path: str = None):
        if config_path is None:
            # 自动定位配置文件路径
            script_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(script_dir, "../config/ai_bloggers.yaml")
        self.config = self.load_config(config_path)
        self.since_days = 7  # 抓取最近 7 天的内容

    def load_config(self, config_path: str) -> Dict:
        """加载配置文件"""
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def translate_to_chinese(self, text: str) -> str:
        """翻译文本到中文（简单实现）"""
        if not text:
            return text

        # 检查是否已经是中文
        chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
        if chinese_chars > len(text) * 0.3:
            return text  # 已经是中文，不需要翻译

        try:
            # 使用 LibreTranslate (免费翻译服务)
            url = "https://libretranslate.com/translate"
            payload = {
                "q": text,
                "source": "en",
                "target": "zh",
                "format": "text"
            }

            response = requests.post(url, json=payload, timeout=5)
            result = response.json()

            if response.status_code == 200 and "translatedText" in result:
                return result["translatedText"]
            else:
                # 翻译失败，返回原文
                return text
        except:
            # 翻译服务不可用，返回原文
            return text

    def scrape_rss_feeds(self) -> List[Dict]:
        """抓取 RSS feeds"""
        articles = []

        print(f"📰 开始抓取 RSS feeds (最近 {self.since_days} 天)...")

        for feed_config in self.config.get('rss_feeds', []):
            try:
                feed_name = feed_config.get('name', '未知来源')
                feed_url = feed_config['url']

                print(f"   抓取: {feed_name}...")

                feed = feedparser.parse(feed_url)

                feed_articles = 0
                for entry in feed.entries[:10]:  # 每个 feed 取最新 10 条
                    # 检查发布时间
                    published = entry.get('published_parsed')
                    if published:
                        pub_date = datetime(*published[:6])
                        if pub_date < datetime.now() - timedelta(days=self.since_days):
                            continue

                    # 获取原始标题
                    original_title = entry.get('title', '无标题')
                    # 翻译标题到中文
                    translated_title = self.translate_to_chinese(original_title)

                    articles.append({
                        'title': translated_title,
                        'url': entry.get('link', ''),
                        'source': feed_name,
                        'author': entry.get('author', feed_name),
                        'published': entry.get('published', ''),
                        'summary': entry.get('summary', '')[:200]
                    })
                    feed_articles += 1

                print(f"      ✅ 获取 {feed_articles} 篇文章")

            except Exception as e:
                print(f"      ❌ 抓取 {feed_config.get('name')} 失败: {e}")

        print(f"📰 总共抓取 {len(articles)} 篇文章")
        return articles

    def scrape_all(self) -> List[Dict]:
        """抓取所有配置的内容源"""
        all_articles = []

        # 目前只实现 RSS 抓取
        # TODO: 添加 Twitter 和 YouTube 抓取
        all_articles.extend(self.scrape_rss_feeds())

        # 按时间排序
        all_articles.sort(key=lambda x: x.get('published', ''), reverse=True)

        return all_articles


def main():
    """测试函数"""
    scraper = ContentScraper()
    articles = scraper.scrape_all()

    print(f"📰 抓取到 {len(articles)} 篇文章:")
    for article in articles:
        print(f"\n标题: {article['title']}")
        print(f"来源: {article['source']}")
        print(f"链接: {article['url']}")


if __name__ == "__main__":
    main()
