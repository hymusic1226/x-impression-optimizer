import os
import json
from flask import Flask, render_template, request, Response
from dotenv import load_dotenv

load_dotenv("/tmp/x-impression-optimizer/.env")
os.environ.setdefault("FLASK_SKIP_DOTENV", "1")

app = Flask(__name__, instance_path="/tmp/x-impression-optimizer")

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()


def build_analysis_prompt(profile_data: dict) -> str:
    url = profile_data.get("url", "").strip()
    bio = profile_data.get("bio", "").strip()
    niche = profile_data.get("niche", "").strip()
    followers = profile_data.get("followers", "不明")
    avg_impressions = profile_data.get("avg_impressions", "不明")
    post_frequency = profile_data.get("post_frequency", "不明")
    target_audience = profile_data.get("target_audience", "").strip()
    challenges = profile_data.get("challenges", "").strip()

    prompt = f"""あなたはX（旧Twitter）のグロースハックと SNS マーケティングの世界的エキスパートです。
数千のアカウントを分析し、インプレッションを平均3〜10倍に引き上げてきた実績があります。

以下のXアカウント情報を詳細に分析し、インプレッションを最大化するための具体的な戦略を提案してください。

【アカウント情報】
・プロフィールURL：{url}
・現在のBio（自己紹介）：{bio if bio else '未入力'}
・ジャンル/ニッチ：{niche if niche else '未入力'}
・フォロワー数：{followers}
・月平均インプレッション：{avg_impressions if avg_impressions != '不明' else '未入力'}
・週の投稿頻度：{post_frequency}回/週
・ターゲット層：{target_audience if target_audience else '未入力'}
・現在の課題：{challenges if challenges else '未入力'}

以下の構成で、具体的かつ実践的な分析と提案を日本語で書いてください。

## 🎯 総合スコアと診断

このアカウントの現状を100点満点で採点し、スコアと主な理由を明記してください。
スコアは必ず「**総合スコア：XX点 / 100点**」という形式で書いてください。
現状の強みと弱みを端的にまとめてください。

## ✍️ Bio（自己紹介）最適化

現在のBioを分析し、以下を提案してください：
- 改善版Bioの具体的な文案（140文字以内）
- なぜその文案が効果的か（キーワード、ターゲットへの訴求力、差別化ポイント）
- プロフィール画像・ヘッダー画像についての推奨

## 📅 最適な投稿戦略

以下を具体的に提案してください：
- 推奨投稿頻度（現状との比較）
- インプレッションが最も伸びやすい時間帯（曜日・時間を3パターン）
- 投稿コンテンツの黄金比率（例：情報系60%、意見系20%、エンゲージメント系20%）
- バズりやすいツイートの型（テンプレート付き）

## #️⃣ ハッシュタグ戦略

- おすすめハッシュタグリスト（15〜20個、競合度と効果別に分類）
- ハッシュタグの使い方（1投稿あたりの個数・配置方法）
- ニッチハッシュタグと人気ハッシュタグの使い分け方

## 💬 エンゲージメント向上テクニック

即効性の高い施策を5つ、具体的なアクション付きで提案してください：
1. （施策名）：（具体的なアクション）
2. （施策名）：（具体的なアクション）
3. （施策名）：（具体的なアクション）
4. （施策名）：（具体的なアクション）
5. （施策名）：（具体的なアクション）

## 🚀 30日間アクションプラン

インプレッションを2〜3倍にするための30日間の具体的なロードマップを提案してください：
- 第1週（Day 1〜7）：基盤整備
- 第2週（Day 8〜14）：コンテンツ最適化
- 第3週（Day 15〜21）：エンゲージメント強化
- 第4週（Day 22〜30）：スケールアップ

---

各セクションは具体的で実践可能なアドバイスにしてください。
抽象的なアドバイスではなく、明日から使える具体的なアクションを中心に書いてください。"""

    return prompt


DEMO_TEXT = """## 🎯 総合スコアと診断

**総合スコア：52点 / 100点**

現状分析では、アカウントの方向性は明確ですが、いくつかの重要な最適化ポイントが見受けられます。

**強み：**
- ジャンルが明確でターゲット層が絞られている
- 定期的な投稿習慣がある

**弱み：**
- Bioが検索されにくいキーワード構成になっている
- 投稿時間が最適化されていない
- エンゲージメントを促すCTA（行動喚起）が不足している

## ✍️ Bio（自己紹介）最適化

**改善版Bio案：**
「📊 [ジャンル]の専門家｜毎日役立つ情報を発信中✨ フォローで[具体的なベネフィット]が手に入る｜実績：〇〇」

**効果的な理由：**
- 絵文字で視認性UP・検索キーワードを自然に含有
- 「フォローするメリット」を明示することでフォロー率が向上
- 実績の数字を入れることで信頼性が増す

**プロフィール画像推奨：**
顔写真（認知度2倍）またはブランドロゴ（統一感重視の場合）。背景は白か単色がベスト。

## 📅 最適な投稿戦略

**推奨投稿頻度：** 現状から週3〜5回に増加（質を落とさない範囲で）

**最もインプレッションが伸びやすい時間帯：**
- 🌅 平日7:00〜8:00（通勤・朝の情報収集タイム）
- 🌆 平日12:00〜13:00（ランチタイム）
- 🌙 平日21:00〜22:00（夜のリラックスタイム）

**投稿コンテンツの黄金比率：**
- 情報・教育系：50%（ノウハウ、Tips、業界情報）
- 意見・コラム系：30%（自分の考え・経験）
- エンゲージメント系：20%（質問・投票・コミュニティ形成）

**バズりやすいツイートの型：**
「〇〇な人へ。実は△△するだけで□□できます。具体的には…（1）〜 （2）〜 （3）〜 保存して活用してください👇」

## #️⃣ ハッシュタグ戦略

**ニッチ系（競合低・効果高）：** #〇〇初心者 #〇〇勉強中 #〇〇tips

**人気系（拡散力あり）：** #〇〇 #〇〇好きと繋がりたい #朝活

**1投稿あたりの推奨個数：** 2〜3個（多すぎるとスパム判定のリスク）

**配置：** 本文末尾または最初のリプライ欄に入れると可読性UP

## 💬 エンゲージメント向上テクニック

1. **質問ツイート**：「〇〇派？それとも△△派？」でリプライを誘発
2. **スレッド投稿**：1ツイートを複数に分けてインプレッション滞在時間を延ばす
3. **インフルエンサーへの価値あるリプライ**：フォロワーへの露出を増やす
4. **朝イチの「おはようツイート」廃止**：代わりに価値ある情報を最初に投稿
5. **固定ツイートの最適化**：最も反応が良かったツイートをプロフィールトップに固定

## 🚀 30日間アクションプラン

**第1週（Day 1〜7）：基盤整備**
- Bio・プロフィール画像を最適化
- 投稿時間を分析して最適な時間帯に変更
- 過去の投稿のインプレッションデータを確認

**第2週（Day 8〜14）：コンテンツ最適化**
- バズった投稿の型を分析して横展開
- スレッド投稿を週2回試す
- ハッシュタグを見直して最適な組み合わせを発見

**第3週（Day 15〜21）：エンゲージメント強化**
- 同ジャンルのインフルエンサー10人に価値あるリプライ
- 質問ツイートを週2回投稿
- コメントへの返信率を100%に

**第4週（Day 22〜30）：スケールアップ**
- 最も反応が良かったコンテンツ形式に集中
- インプレッション数を集計・分析
- 次月の戦略を立案"""


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/result")
def result():
    return render_template("result.html")


@app.route("/api/analyze", methods=["POST"])
def analyze():
    data = request.json
    url = data.get("url", "").strip()

    if not url:
        return json.dumps({"error": "プロフィールURLを入力してください"}), 400

    prompt = build_analysis_prompt(data)

    def generate():
        if not GEMINI_API_KEY:
            import time
            chunk_size = 25
            for i in range(0, len(DEMO_TEXT), chunk_size):
                chunk = DEMO_TEXT[i:i + chunk_size]
                yield f"data: {json.dumps({'type': 'text', 'content': chunk})}\n\n"
                time.sleep(0.02)
            yield 'data: {"type": "done"}\n\n'
            return

        try:
            from google import genai as google_genai
            client = google_genai.Client(api_key=GEMINI_API_KEY)
            resp = client.models.generate_content_stream(
                model="gemini-2.5-flash-lite",
                contents=prompt
            )
            for chunk in resp:
                if chunk.text:
                    yield f"data: {json.dumps({'type': 'text', 'content': chunk.text})}\n\n"
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "rate" in error_msg.lower():
                msg = "APIの利用制限に達しました。しばらくしてからお試しください。"
            elif "403" in error_msg or "key" in error_msg.lower():
                msg = "APIキーが無効です。設定を確認してください。"
            else:
                msg = f"エラーが発生しました: {error_msg[:120]}"
            yield f"data: {json.dumps({'type': 'error', 'content': msg})}\n\n"

        yield 'data: {"type": "done"}\n\n'

    return Response(
        generate(),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5002))
    app.run(debug=True, port=port)
