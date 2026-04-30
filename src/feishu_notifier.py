#!/usr/bin/env python3
"""
飞书消息推送模块
使用 HTTP API 直接调用
"""

import os
import json
import requests
from datetime import datetime
from typing import List, Dict


class FeishuNotifier:
    def __init__(self, app_id: str, app_secret: str, user_open_id: str):
        self.app_id = app_id.strip() if app_id else ""
        self.app_secret = app_secret.strip() if app_secret else ""
        self.user_open_id = user_open_id.strip() if user_open_id else ""
        self.api_base = "https://open.feishu.cn/open-apis"
        self.access_token = None

        if not self.app_id or not self.app_secret:
            raise ValueError("App ID 和 App Secret 不能为空")

    def get_access_token(self) -> str:
        """获取 app_access_token"""
        url = f"{self.api_base}/auth/v3/app_access_token/internal"

        payload = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }

        print(f"🔑 正在获取 access_token...")
        print(f"   URL: {url}")
        print(f"   App ID: {self.app_id[:10]}...")

        response = requests.post(
            url,
            json=payload,
            headers={"Content-Type": "application/json"}
        )

        print(f"   响应状态码: {response.status_code}")
        data = response.json()
        print(f"   响应: code={data.get('code')}, msg={data.get('msg')}")

        if data.get("code") == 0:
            self.access_token = data.get("app_access_token")
            print(f"✅ 获取 token 成功")
            return self.access_token
        else:
            raise Exception(f"获取 token 失败: {data}")

    def send_text_message(self, content: str) -> dict:
        """发送纯文本消息"""
        if not self.access_token:
            self.get_access_token()

        url = f"{self.api_base}/im/v1/messages?receive_id_type=open_id"

        payload = {
            "receive_id": self.user_open_id,
            "msg_type": "text",
            "content": json.dumps({"text": content})
        }

        response = requests.post(
            url,
            json=payload,
            headers={
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
        )

        return response.json()

    def send_card_message(self, elements: List[Dict]) -> dict:
        """发送消息卡片"""
        if not self.access_token:
            self.get_access_token()

        url = f"{self.api_base}/im/v1/messages?receive_id_type=open_id"

        card_content = {
            "config": {"wide_screen_mode": True},
            "elements": elements
        }

        payload = {
            "receive_id": self.user_open_id,
            "msg_type": "interactive",
            "content": json.dumps(card_content)
        }

        print(f"📤 发送消息卡片...")

        response = requests.post(
            url,
            json=payload,
            headers={
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
        )

        data = response.json()
        print(f"   响应: code={data.get('code')}, msg={data.get('msg')}")

        return data

    def send_ai_news(self, articles: List[Dict]) -> dict:
        """发送 AI 资讯消息卡片"""
        elements = [
            {
                "tag": "div",
                "text": {
                    "content": f"📅 {datetime.now().strftime('%Y年%m月%d日')} AI 每日资讯",
                    "tag": "lark_md"
                }
            },
            {
                "tag": "hr"
            }
        ]

        for article in articles[:10]:
            elements.extend([
                {
                    "tag": "div",
                    "text": {
                        "content": f"### {article.get('title', '无标题')}",
                        "tag": "lark_md"
                    }
                },
                {
                    "tag": "div",
                    "text": {
                        "content": f"📰 {article.get('source', '未知来源')} | 👤 {article.get('author', '未知作者')}",
                        "tag": "lark_md"
                    }
                },
                {
                    "tag": "action",
                    "actions": [
                        {
                            "tag": "button",
                            "text": {
                                "content": "查看原文",
                                "tag": "plain_text"
                            },
                            "url": article.get('url', ''),
                            "type": "default"
                        }
                    ]
                },
                {
                    "tag": "hr"
                }
            ])

        print(f"📤 准备发送 {len(articles)} 条资讯")
        return self.send_card_message(elements)


def main():
    """测试函数"""
    app_id = os.getenv("FEISHU_APP_ID")
    app_secret = os.getenv("FEISHU_APP_SECRET")
    user_open_id = os.getenv("FEISHU_USER_OPEN_ID")

    if not all([app_id, app_secret, user_open_id]):
        print("❌ 缺少必要的环境变量")
        return

    print(f"🔧 初始化飞书通知器")
    notifier = FeishuNotifier(app_id, app_secret, user_open_id)

    test_articles = [
        {
            "title": "测试消息",
            "source": "系统测试",
            "author": "GitHub Actions",
            "url": "https://github.com"
        }
    ]

    print("📤 发送测试消息...")
    result = notifier.send_ai_news(test_articles)
    print(f"发送结果: {result}")


if __name__ == "__main__":
    main()
