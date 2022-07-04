from cgitb import text
import json
import os
import requests
import toml
import base64

def checkExist(api_url):
    with open('status.txt', 'r') as stats_file:
        a: int = int(stats_file.readline())
        req = requests.get("http://" + api_url + "/article/delete/" + str(a))
        if req.status_code == 200:
            print("Updated!!")

class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (bytes, bytearray)):
            return obj.decode("UTF8") # <- or any other encoding of your choice
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)

if __name__ == "__main__":
    config = toml.load("settings/config.toml")
    api_url = config["ip"] + ":" + config["port"]

    checkExist(api_url)
    
    with open("icon/" + config['article']['icon_name'], "rb") as image_file:
        icon = base64.b64encode(image_file.read()).decode("UTF8")

    article = config["article"]
    article["icon"] = icon

    response = requests.post("http://" + api_url + "/article", data=json.dumps(article))
    article_id = response.json()

    for dir in os.listdir('steps'):
        step = toml.load("steps/" + dir + "/config.toml")
        with open("steps/" + dir + "/content.html", "r") as step_content_file:
            step["content"] = step_content_file.read()
        print(article_id)
        step["article_id"] = article_id
        step["num"] = int(dir)

        response = requests.post("http://" + api_url + "/step", data=json.dumps(step))
        step_id = response.json()

        imgs = []

        for image in os.listdir('steps/' + dir + "/images"):
            with open('steps/' + dir + "/images/" + image, "rb") as image_file:
                img = {}
                img["step_id"] = step_id
                img["image"] = base64.b64encode(image_file.read()).decode("UTF8")
                img["image_name"] = image
                imgs.append(img)
        
        response = requests.post("http://" + api_url + "/images", data=json.dumps(imgs))
        if (response.status_code == 200):
            with open('status.txt', 'w') as stats_file:
                stats_file.write(str(step_id))

        print("Complete!")