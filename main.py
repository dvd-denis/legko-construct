from cgitb import text
import json
import os
import requests
import toml
import base64


class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (bytes, bytearray)):
            return obj.decode("UTF8") # <- or any other encoding of your choice
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)

if __name__ == "__main__":
    config = toml.load("settings/config.toml")
    api_url = config["ip"] + ":" + config["port"]
    print(config)

    with open("icon/" + config['article']['icon_name'], "rb") as image_file:
        icon = base64.b64encode(image_file.read()).decode("UTF8")

    article = config["article"]
    article["icon"] = icon

    response = requests.post("http://" + api_url + "/article", data=json.dumps(article))
    article_id = response.json()

    steps = []
    images = []

    # for dir in os.listdir('steps'):
    #     step = toml.load("steps/" + dir + "/config.toml")
    #     with open("steps/" + dir + "/content.html", "r") as step_content_file:
    #         step["content"] = step_content_file.read()

    #     content["steps"][int(dir)] = step
        
    #     for images in os.listdir('steps/' + dir + "/images"):
    #         for image in images:
    #             with open('steps/' + dir + "/images/" + image, "r") as image_file:
    #                 img = {}
    #                 img["step_id"] =                     
        

    # print(content)