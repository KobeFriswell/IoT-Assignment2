import requests
import json
import os


class PushbulletAccess:
    """
        access for pushbullet notifications to engineer account
    """
    

    def __init__(self):
        self.ACCESS_TOKEN="TOKEN"


    def send_notification(self,title, body):
        """ Sending notification via pushbullet.
            Args:
                title (str) : title of text.
                body (str) : Body of text.
        """
        data_send = {"type": "note", "title": title, "body": body}
    
        resp = requests.post('https://api.pushbullet.com/v2/pushes', data=json.dumps(data_send),
                            headers={'Authorization': 'Bearer ' + self.ACCESS_TOKEN, 
                            'Content-Type': 'application/json'})
        if resp.status_code != 200:
            return False
        else:
            return True
