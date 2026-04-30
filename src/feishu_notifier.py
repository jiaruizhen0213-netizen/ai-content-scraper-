#!/usr/bin/env python3
"""
飞书消息推送模块
支持向指定用户发送消息卡片
"""

import os
import json
import requests
from datetime import datetime
from typing import List, Dict


class FeishuNotifier:
    def __init__(self, app_id: str, app_secret: str, user_open_id: str):
        self.app_id = app_id
        self.app_secret = app_secret
        self.user_open_id = user_open_id
        self.tenant_access_token = None
        self.api_base = "https://open.feishu.cn/open-apis"

    def get_tenant_access_token(self) -> str:
        """获取 app_access_token (自建应用)"""
        url = f"{self.api_base}/auth/v3/app_access_token/internal"
        payload = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }

        print(f"🔑 正在获取飞书 app_access_token...")
        print(f"   请求 URL: {url}")
        print(f"   App ID: {self.app_id[:10]}...")
        print(f"   App Secret 长度: {len(self.app_secret)}")

        headers = {
            "Content-Type": "application/json"
        }

        print(f"   请求头: {headers}")
        print(f"   请求体: app_id={self.app_id[:10]}..., app_secret=***")

        response = requests.post(url, json=payload, headers=headers)

        print(f"   响应状态码: {response.status_code}")
        print(f"   响应内容: {response.text[:500]}")

        data = response.json()

        print(f"   API 响应: code={data.get('code')}, msg={data.get('msg')}")

        if data.get("code") != 0:
            error_msg = data.get('msg', 'unknown error')
            print(f"❌ 飞书 API 错误:")
            print(f"   错误码: {data.get('code')}")
            print(f"   错误信息: {error_msg}")
            print(f"   完整响应: {data}")
            raise Exception(f"Failed to get app_access_token: {data}")

        self.tenant_access_token = data.get("app_access_token")
        print(f"✅ 获取 token 成功")
        return self.tenant_access_token

    def send_text_message(self, content: str) -> dict:
        """发送纯文本消息"""
        if not self.tenant_access_token:
            self.get_tenant_access_token()

        url = f"{self.api_base}/im/v1/messages?receive_id_type=open_id"
        headers = {
            "Authorization": f"Bearer {self.tenant_access_token}",
            "Content-Type": "application/json"
        }

        payload = {
            "receive_id": self.user_open_id,
            "msg_type": "text",
            "content": json.dumps({"text": content})
        }

        response = requests.post(url, headers=headers, json=payload)
        return response.json()

    def send_card_message(self, elements: List[Dict]) -> dict:
        """发送消息卡片"""
        if not self.tenant_access_token:
            self.get_tenant_access_token()

        url = f"{self.api_base}/im/v1/messages?receive_id_type=open_id"
        headers = {
            "Authorization": f"Bearer {self.tenant_access_token}",
            "Content-Type": "application/json"
        }

        card_content = {
            "config": {"wide_screen_mode": True},
            "elements": elements
        }

        payload = {
            "receive_id": self.user_open_id,
            "msg_type": "interactive",
            "content": json.dumps(card_content)
        }

        response = requests.post(url, headers=headers, json=payload)
        return response.json()

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

        for article in articles[:10]:  # 最多显示 10 条
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

        return self.send_card_message(elements)


def main():
    """测试函数"""
    app_id = os.getenv("FEISHU_APP_ID")
    app_secret = os.getenv("FEISHU_APP_SECRET")
    user_open_id = os.getenv("FEISHU_USER_OPEN_ID")

    if not all([app_id, app_secret, user_open_id]):
        print("❌ 缺少必要的环境变量")
        return

    notifier = FeishuNotifier(app_id, app_secret, user_open_id)

    # 测试发送消息
    test_articles = [
        {
            "title": "测试消息：飞书通知已配置成功",
            "source": "系统测试",
            "author": "GitHub Actions",
            "url": "https://github.com"
        }
    ]

    result = notifier.send_ai_news(test_articles)
    print(f"发送结果: {result}")


if __name__ == "__main__":
    main()
