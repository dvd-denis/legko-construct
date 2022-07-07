from cgitb import text
import json
import os
from time import process_time_ns
import requests
import toml
import base64
from dotenv import dotenv_values, load_dotenv 

def checkExist(api_url, article_folder, headers):
    try:
        with open("src/" + article_folder + '/status.txt', 'r') as stats_file:
            a: int = int(stats_file.readline())
            req = requests.post("https://" + api_url + "/article/delete/" + str(a), headers=headers)
            if req.status_code == 200:
                print(article_folder + ": Updated!")
    except Exception as e:
        pass

if __name__ == "__main__":

    load_dotenv()

    env_config = dotenv_values(".env")

    headers = {
        "Key": env_config["KEY"]
    }

    global_config = toml.load("config.toml")
    api_url = global_config["ip"]   
    (_, article_folders, _) = os.walk("src").__next__()
    for article_folder in article_folders:
        print(article_folders)
        print(article_folder)

        article = toml.load("src/" + article_folder + "/settings/config.toml")

        checkExist(api_url, article_folder, headers)
        
        with open("src/" + article_folder + "/icon/" + article['icon_name'], "rb") as image_file:
            icon = base64.b64encode(image_file.read()).decode("UTF8")

        article["icon"] = icon

        response = requests.post("https://" + api_url + "/article", data=json.dumps(article), headers=headers)
        article_id = response.json()

        for dir in os.listdir("src/" + article_folder + '/steps'):
            step = toml.load("src/" + article_folder + "/steps/" + dir + "/config.toml")
            with open("src/" + article_folder + "/steps/" + dir + "/content.html", "r") as step_content_file:
                step["content"] = step_content_file.read()
            step["article_id"] = article_id
            step["num"] = int(dir)

            response = requests.post("https://" + api_url + "/step", data=json.dumps(step), headers=headers)
            step_id = response.json()
            imgs = []

            for image in os.listdir("src/" + article_folder + '/steps/' + dir + "/images"):
                with open("src/" + article_folder + '/steps/' + dir + "/images/" + image, "rb") as image_file:
                    img = {}
                    img["step_id"] = step_id
                    img["image"] = base64.b64encode(image_file.read()).decode("UTF8")
                    img["image_name"] = image
                    imgs.append(img)
            if len(imgs) != 0:
                response = requests.post("https://" + api_url + "/images", data=json.dumps(imgs), headers=headers)

        if (response.status_code == 200):
            with open("src/" + article_folder + '/status.txt', 'w') as stats_file:
                stats_file.write(str(article_id))

        print(article_folder + ": Complete!")