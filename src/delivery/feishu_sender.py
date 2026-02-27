import requests

class FeishuSender:
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
        
    def send(self, title: str, markdown_content: str) -> bool:
        if not self.webhook_url:
            return False
            
        payload = {
            "msg_type": "interactive",
            "card": {
                "header": {
                    "title": {
                        "tag": "plain_text",
                        "content": title
                    }
                },
                "elements": [
                    {
                        "tag": "markdown",
                        "content": markdown_content
                    }
                ]
            }
        }
        
        try:
            response = requests.post(
                self.webhook_url,
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            return data.get("code") == 0
        except Exception as e:
            print(f"飞书推送报错: {e}")
            return False
