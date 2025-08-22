import requests

class PushoverClient:
    def __init__(self, user_key, api_token):
        self.user_key = user_key
        self.api_token = api_token
        self.api_url = "https://api.pushover.net/1/messages.json"
    
    def send_summary(self, title, message, priority=0):
        try:
            data = {
                "token": self.api_token,
                "user": self.user_key,
                "message": message,
                "title": title,
                "priority": priority,
                "html": 1
            }
            
            response = requests.post(self.api_url, data=data)
            response.raise_for_status()
            
            result = response.json()
            return result.get("status", 0) == 1
        except Exception as e:
            print(f"Error sending Pushover notification: {e}")
            return False