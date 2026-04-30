#!/usr/bin/env python3
"""
飞书消息推送模块（使用官方 SDK）
支持向指定用户发送消息卡片
"""

import os
import json
from datetime import datetime
from typing import List, Dict

try:
    from lark_oapi.api.bot.v1 import *
    from lark_oapi.api.auth.v3 import *
    from lark_oapi import *
except ImportError:
    print("请安装飞书官方 SDK: pip install lark-oapi")
    raise


class FeishuNotifier:
    def __init__(self, app_id: str, app_secret: str, user_open_id: str):
        # 清理可能的空格和换行符
        self.app_id = app_id.strip() if app_id else ""
        self.app_secret = app_secret.strip() if app_secret else ""
        self.user_open_id = user_open_id.strip() if user_open_id else ""

        # 创建客户端
        self.client = Client.builder() \
            .app_id(self.app_id) \
            .app_secret(self.app_secret) \
            .build()

    def send_text_message(self, content: str) -> dict:
        """发送纯文本消息"""
        try:
            request = CreateMessageRequest.builder() \
                .receive_id_type("open_id") \
                .request_body(CreateMessageRequestBody.builder()
                    .receive_id(self.user_open_id)
                    .msg_type("text")
                    .content(json.dumps({"text": content}))
                    .build()) \
                .build()

            response = self.client.message.v1.message.create(request)

            if response.success():
                return {"code": 0, "msg": "success"}
            else:
                return {
                    "code": response.code,
                    "msg": response.msg,
                    "error": response.error
                }
        except Exception as e:
            return {"code": -1, "msg": str(e)}

    def send_card_message(self, elements: List[Dict]) -> dict:
        """发送消息卡片"""
        try:
            card_content = {
                "config": {"wide_screen_mode": True},
                "elements": elements
            }

            request = CreateMessageRequest.builder() \
                .receive_id_type("open_id") \
                .request_body(CreateMessageRequestBody.builder()
                    .receive_id(self.user_open_id)
                    .msg_type("interactive")
                    .content(json.dumps(card_content))
                    .build()) \
                .build()

            response = self.client.message.v1.message.create(request)

            print(f"📤 飞书 API 响应:")
            print(f"   code: {response.code}")
            print(f"   msg: {response.msg}")

            if response.success():
                return {"code": 0, "msg": "success"}
            else:
                return {
                    "code": response.code,
                    "msg": response.msg,
                    "error": response.error
                }
        except Exception as e:
            print(f"❌ 发送消息卡片异常: {e}")
            return {"code": -1, "msg": str(e)}

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

    print(f"🔧 初始化飞书通知器:")
    print(f"   App ID: {app_id[:10]}...")
    print(f"   User Open ID: {user_open_id[:10]}...")

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

    print("📤 发送测试消息...")
    result = notifier.send_ai_news(test_articles)
    print(f"发送结果: {result}")


if __name__ == "__main__":
    main()
