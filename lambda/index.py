import json
import os
from urllib import request, parse

# FastAPI の URL は CDK で環境変数にセットしておく
FASTAPI_URL = os.environ["FASTAPI_URL"]

def lambda_handler(event, context):
    try:
        # リクエストボディ解析
        body = json.loads(event.get("body", "{}"))
        message = body.get("message", "")
        conversation_history = body.get("conversationHistory", [])

        # conversationHistory に user メッセージを追加
        convo = conversation_history.copy()
        convo.append({"role": "user", "content": message})

        # FastAPI へ投げるペイロード
        payload = json.dumps({"prompt": message}).encode("utf-8")
        req = request.Request(
            url=FASTAPI_URL + "/generate",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with request.urlopen(req, timeout=30) as resp:
            resp_json = json.loads(resp.read().decode("utf-8"))

        assistant_text = resp_json.get("text", "")
        convo.append({"role": "assistant", "content": assistant_text})

        # レスポンス返却
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,Authorization",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            "body": json.dumps({
                "success": True,
                "response": assistant_text,
                "conversationHistory": convo
            })
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,Authorization",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            "body": json.dumps({
                "success": False,
                "error": str(e)
            })
        }
