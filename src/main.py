#!/usr/bin/env python3
"""
AI 内容抓取主程序
每天定时抓取 AI 博主最新内容并推送到飞书
"""

import os
import sys
from datetime import datetime

# 添加当前目录到 Python 路径，确保能正确导入模块
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from content_scraper import ContentScraper
from feishu_notifier import FeishuNotifier


def main():
    """主函数"""
    print(f"🚀 AI 内容抓取任务开始 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 初始化配置
    app_id = os.getenv("FEISHU_APP_ID")
    app_secret = os.getenv("FEISHU_APP_SECRET")
    user_open_id = os.getenv("FEISHU_USER_OPEN_ID")

    if not all([app_id, app_secret, user_open_id]):
        print("❌ 缺少必要的环境变量")
        print("请检查 GitHub Secrets 配置")
        sys.exit(1)

    # 抓取内容
    print("📰 开始抓取 AI 内容...")
    scraper = ContentScraper()
    articles = scraper.scrape_all()

    if not articles:
        print("⚠️  未找到新内容")
        # 仍然发送通知告知无新内容
        notifier = FeishuNotifier(app_id, app_secret, user_open_id)
        notifier.send_text_message(f"📅 {datetime.now().strftime('%Y年%m月%d日')} AI 每日资讯\n\n暂无新内容更新")
        return

    print(f"✅ 抓取到 {len(articles)} 篇文章")

    # 推送到飞书
    print("📤 正在推送到飞书...")
    notifier = FeishuNotifier(app_id, app_secret, user_open_id)
    result = notifier.send_ai_news(articles)

    if result.get("code") == 0:
        print("✅ 推送成功！")
    else:
        print(f"❌ 推送失败: {result}")
        sys.exit(1)

    print(f"🎉 任务完成 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
