import requests
import dotenv
import os
from PIL import Image

class APIHandler():
    def __init__(self) -> None:
        dotenv.load_dotenv()
        token = os.getenv("TOKEN")
        self.headers = {"Authorization": "token " + token}

    def get(self, url):
        url = "https://api.github.com" + url
        return requests.get(url=url, headers=self.headers)

if __name__ == "__main__":
    if not os.path.exists(".env"):
        print("Github Access Token Required.")
        token = input("Please enter a Github Access Token for your Account: ")

        if token != "":
            with open(".env", "w") as f:
                f.write(f'TOKEN="{token}"')

    gh = APIHandler()
    userData = gh.get("/user")

    if userData.status_code == 200:
        json = userData.json()

        # Shows User Profile Image
        # userPhoto = requests.get(json["avatar_url"])
        # with open("image.jpg", "wb") as f:
        #     f.write(userPhoto.content)

        # img = Image.open("image.jpg")
        # img.show()


        print(f"Authenticated as: {json["name"]} ({json["login"]})")
    else:
        print(f"Error Getting User Data. Error {userData.status_code}, {userData.json()["message"]}")