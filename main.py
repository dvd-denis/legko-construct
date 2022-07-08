import json
import os
import requests
import toml
import base64
from dotenv import dotenv_values, load_dotenv

def checkExist(api_url, group_folder, headers):
    try:
        with open("src/" + group_folder + '/status.txt', 'r') as stats_file:
            a: int = int(stats_file.readline())
            req = requests.post("https://" + api_url + "/group/delete/" + str(a), headers=headers)
            if req.status_code == 200:
                print(group_folder + ": Updated!")
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
    (_, group_folders, _) = os.walk("src").__next__()
    for group_folder in group_folders:
        group = toml.load("src/" + group_folder + "/group.toml")

        checkExist(api_url, group_folder, headers)

        with open("src/" + group_folder + "/" + group['icon_name'], "rb") as image_file:
            icon = base64.b64encode(image_file.read()).decode("UTF8")

        group["icon"] = icon

        response = requests.post("https://" + api_url + "/group", data=json.dumps(group), headers=headers)
        group_id = response.json()

        for article_folder in os.listdir("src/" + group_folder + '/articles'):
            article = toml.load("src/" + group_folder + "/articles/" + article_folder + "/article.toml")
            article["group_id"] = group_id
            
            response = requests.post("https://" + api_url + "/article/", data=json.dumps(article), headers=headers)
            article_id = response.json()
            
            num = 0
            for step_folder in os.listdir("src/" + group_folder + '/articles/' + article_folder + '/steps'):

                step = toml.load("src/" + group_folder + '/articles/' + article_folder + '/steps/' + step_folder + "/step.toml")
                with open("src/" + group_folder + '/articles/' + article_folder + '/steps/' + step_folder + "/content.html", "r") as step_content_file:
                    step["content"] = step_content_file.read()
                step["article_id"] = article_id
                step["num"] = num
                num+=1

                response = requests.post("https://" + api_url + "/step", data=json.dumps(step), headers=headers)
                step_id = response.json()
                imgs = []

                for image in os.listdir("src/" + group_folder + '/articles/' + article_folder + '/steps/' + step_folder + "/images"):
                    with open("src/" + group_folder + '/articles/' + article_folder + '/steps/' + step_folder + "/images/" + image, "rb") as image_file:
                        img = {}
                        img["step_id"] = step_id
                        img["image"] = base64.b64encode(image_file.read()).decode("UTF8")
                        img["image_name"] = image
                        imgs.append(img)
                if len(imgs) != 0:
                    response = requests.post("https://" + api_url + "/images", data=json.dumps(imgs), headers=headers)

        if (response.status_code == 200):
            with open("src/" + group_folder + '/status.txt', 'w') as stats_file:
                stats_file.write(str(group_id))

        print(group_folder + ": Complete!")
