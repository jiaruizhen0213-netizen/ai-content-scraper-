# AI 内容每日推送

每天定时抓取 AI 博主最新内容并推送到飞书。

## 功能特点

- ✅ 每天 10:00 AM (UTC+8) 自动运行
- ✅ 抓取 AI 领域最新资讯（RSS feeds）
- ✅ 推送到飞书个人消息
- ✅ GitHub Actions 托管，无需本地运行

## 配置的 AI 博主

### 官方博客
- OpenAI Blog
- Google AI Blog
- DeepMind Blog

### Twitter/X 大V
- Andrew Ng
- Yann LeCun
- Ian Goodfellow
- Andrej Karpathy
- David Ha

## 本地测试

```bash
# 安装依赖
pip install -r requirements.txt

# 测试飞书通知
export FEISHU_APP_ID="cli_a941c9ebab38dbc8"
export FEISHU_APP_SECRET="peDFmN57I3tcyzd5HkhWDheePOJYBQi7"
export FEISHU_USER_OPEN_ID="ou_db8fc2e831d082049a4c6435dcd25226"

python src/feishu_notifier.py
```

## GitHub Secrets

需要在 GitHub 仓库中配置以下 Secrets:

- `FEISHU_APP_ID`: 飞书应用 ID
- `FEISHU_APP_SECRET`: 飞书应用密钥
- `FEISHU_USER_OPEN_ID`: 接收消息的用户 Open ID

## 定时任务

每天 10:00 AM (UTC+8) 自动运行，也可以手动触发。

## 添加更多博主

编辑 `config/ai_bloggers.yaml` 文件添加更多 RSS feeds。
