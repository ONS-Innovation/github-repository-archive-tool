import requests
import dotenv
import os
# from PIL import Image


def clearTerminal():
    os.system('cls' if os.name == 'nt' else 'clear')

# APIHandler class to manage all API interactions
class APIHandler():
    def __init__(self) -> None:
        dotenv.load_dotenv(verbose=True, override=True)
        token = os.getenv("TOKEN")
        self.headers = {"Authorization": "token " + token}

    def get(self, url):
        url = "https://api.github.com" + url
        return requests.get(url=url, headers=self.headers)
    
    def patch(self, url, params):
        url = "https://api.github.com" + url
        return requests.patch(url=url, headers=self.headers, json=params)

# User Functions
def viewProfile():
    print(":)")

def editBio():
    oldBio = gh.get("/user").json()["bio"]
    print(f"Old Bio: {oldBio}")
    newBio = input("Input the new BIO: ")
    params = {"bio":newBio}
    response = gh.patch(url="/user", params=params)
    if response.status_code == 200:
        print("Success")
    else:
        print(f"Error updating bio. Error {response.status_code}, {response.json()["message"]}")


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

        # Output confirmation
        print(f"Authenticated as: {json["name"]} ({json["login"]})")

        # Start CLI
        exitCode = False

        while not exitCode:
            selection = int(input(""" \n
Please Select an Option:
1. View Profile
2. Update Bio
                                  
Type -1 to Quit.
"""))
            clearTerminal()
            match selection:
                case 1:
                    viewProfile()
                case 2:
                    editBio()
                case -1:
                    exitCode = True
                case _:
                    print("Invalid Input")

                    
    else:
        print(f"Error Getting User Data. Error {userData.status_code}, {userData.json()["message"]}")