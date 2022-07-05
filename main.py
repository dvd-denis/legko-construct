from cgitb import text
import json
import os
import requests
import toml
import base64

def checkExist(api_url, article_folder):
    try:
        with open(article_folder + '/status.txt', 'r') as stats_file:
            a: int = int(stats_file.readline())
            req = requests.get("http://" + api_url + "/article/delete/" + str(a))
            if req.status_code == 200:
                print("Updated!")
    except Exception as e:
        pass

if __name__ == "__main__":
    global_config = toml.load("config.toml")
    api_url = global_config["ip"] + ":" + global_config["port"]   

    for article_folder in [d for d in os.listdir('.') if os.path.isdir(d) and not d.startswith(".")]:
        article = toml.load(article_folder + "/settings/config.toml")

        checkExist(api_url, article_folder)
        
        with open(article_folder + "/icon/" + article['icon_name'], "rb") as image_file:
            icon = base64.b64encode(image_file.read()).decode("UTF8")

        article["icon"] = icon

        response = requests.post("http://" + api_url + "/article", data=json.dumps(article))
        article_id = response.json()

        for dir in os.listdir(article_folder + '/steps'):
            step = toml.load(article_folder + "/steps/" + dir + "/config.toml")
            with open(article_folder + "/steps/" + dir + "/content.html", "r") as step_content_file:
                step["content"] = step_content_file.read()
            step["article_id"] = article_id
            step["num"] = int(dir)

            response = requests.post("http://" + api_url + "/step", data=json.dumps(step))
            step_id = response.json()
            if (not step["question"]):
                imgs = []

                for image in os.listdir(article_folder + '/steps/' + dir + "/images"):
                    with open(article_folder + '/steps/' + dir + "/images/" + image, "rb") as image_file:
                        img = {}
                        img["step_id"] = step_id
                        img["image"] = base64.b64encode(image_file.read()).decode("UTF8")
                        img["image_name"] = image
                        imgs.append(img)
                
                response = requests.post("http://" + api_url + "/images", data=json.dumps(imgs))

        if (response.status_code == 200):
            with open(article_folder + '/status.txt', 'w') as stats_file:
                stats_file.write(str(article_id))

        print(article_folder + ": Complete!")