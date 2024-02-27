import requests
import dotenv
import os
import datetime
# import pprint
# from PIL import Image


def clearTerminal():
    os.system('cls' if os.name == 'nt' else 'clear')

# APIHandler class to manage all API interactions
class APIHandler():
    def __init__(self) -> None:
        dotenv.load_dotenv(verbose=True, override=True)
        token = os.getenv("TOKEN")
        self.headers = {"Authorization": "token " + token}

    def get(self, url, params, addPrefix: bool = True):
        if addPrefix:
            url = "https://api.github.com" + url
        return requests.get(url=url, headers=self.headers, params=params)
    
    def patch(self, url, params, addPrefix: bool = True):
        url = "https://api.github.com" + url
        return requests.patch(url=url, headers=self.headers, json=params)
    
    def post(self, url, params, addPrefix: bool = True):
        url = "https://api.github.com" + url
        return requests.post(url=url, headers=self.headers, json=params)
    
    def delete(self, url, addPrefix: bool = True):
        url = "https://api.github.com" + url

        return requests.delete(url=url, headers=self.headers)

# User Functions
def viewProfile(json: dict):
    # print(json)
    # print("\n")

    # Basic User Data

    username = json["login"]
    name = json["name"]
    bio = json["bio"]
    blog = json["blog"]
    follows = f"{json["followers"]} / {json["following"]}"
    created = json["created_at"]
    modified = json["updated_at"]
    link = json["html_url"]

    print(
        f"username: {username} \n" +
        f"name: {name} \n" +
        f"bio: {bio} \n" +
        f"blog: {blog} \n" +
        f"followers / following: {follows} \n" +
        f"member since: {datetime.datetime.strptime(created, "%Y-%m-%dT%H:%M:%SZ").strftime("%d %B %Y %H:%M")} \n" +
        f"last updated: {datetime.datetime.strptime(modified, "%Y-%m-%dT%H:%M:%SZ").strftime("%d %B %Y %H:%M")} \n" +
        f"link: {link} \n"
    )

def viewFollows(json: dict):
    noFollowers = json["followers"]
    noFollowing = json["following"]

    response = gh.get(json["followers_url"], {}, False)
    if response.status_code == 200:
        followersJson = response.json()

        print(f"Followers: {noFollowers} \n")
        for follower in followersJson:
            print(f"- {follower["login"]}")
    else:
        print(f"Error Getting Follower Data. Error {response.status_code}, {response.json()["message"]}")

    response = gh.get(json["following_url"].replace("{/other_user}", ""), "", False)
    if response.status_code == 200:
        followingJson = response.json()

        print(f"\nFollowing: {noFollowing} \n")
        for following in followingJson:
            print(f"- {following["login"]}")
    else:
        print(f"Error Getting Following Data. Error {response.status_code}, {response.json()["message"]}")

def viewRepos(json: dict):
    params = {
        "affiliation": "owner"
    }

    response = gh.get("/user/repos", params=params)
    if response.status_code == 200:
        reposJson = response.json()

        # pprint.pprint(reposJson[0])

        for count, repo in enumerate(reposJson):
            print(f"{count+1}. {repo["name"]}")
            print(f"Description: {repo["description"]}")
            print(f"Visibility: {repo["visibility"]}")
            print(f"Owner: {repo["owner"]["login"]}")
            print(f"Link: {repo["html_url"]} \n")

        
    else:
        print(f"Error Getting Repos. Error {response.status_code}, {response.json()["message"]}")

def createRepo(username: str):
    url = f"/user/repos"
    
    repoName = str(input("Please enter the Repo Name: "))
    repoDesc = str(input("Please enter the Repo Description: "))
    repoPriv = str(input("Is the Repo Private? (True/False) ")).lower()

    repoPriv = True if repoPriv == "true" else False

    params = {
        "name": repoName,
        "description": repoDesc,
        "private": repoPriv
    }

    response = gh.post(url, params)

    if response.status_code == 201:
        print(f"Success. Repository Created at https://github.com/TotalDwarf03/{repoName}")
    else:
        print(f"Error Creating Repo. Error {response.status_code}, {response.json()["message"]}")

def deleteRepo():
    username = str(input("Enter the Repo Owner: "))
    repo = str(input("Enter the Repo Name: "))

    url = f"/repos/{username}/{repo}"

    response = gh.delete(url)

    print(response)


def editBio():
    oldBio = gh.get("/user", {}).json()["bio"]
    print(f"Old Bio: {oldBio}")
    newBio = input("Input the new BIO: ")
    params = {"bio":newBio}
    response = gh.patch(url="/user", params=params)
    if response.status_code == 200:
        print("Success")
    else:
        print(f"Error updating bio. Error {response.status_code}, {response.json()["message"]}")

def GetOrgRepos(pageNo: int = 1):
    # Get a list of Repos from an Org of the Auth'd user
    # Which hasn't been updated in x years

    # Get the No. of years
    xYears = int(input("Enter the number of years: "))

    # Get auth'd user's orgs
    response = gh.get("/orgs/ONSdigital/repos", {"page": pageNo})

    if response.status_code == 200:
        orgsRepos = response.json()

        print(response.links)
        
        for repo in orgsRepos:
            # Check if repo has been updated in last x years
            response = gh.get(repo["url"], {}, False)
            
            if response.status_code == 200:
                repoJson = response.json()
                lastUpdate = repoJson["updated_at"]
                lastUpdate = datetime.datetime.strptime(lastUpdate, "%Y-%m-%dT%H:%M:%SZ")
                lastUpdate = datetime.date(lastUpdate.year, lastUpdate.month, lastUpdate.day)

                currentDate = datetime.date.today()
                compDate = datetime.date(currentDate.year - xYears, currentDate.month, currentDate.day)

                if lastUpdate < compDate:
                    archiveFlag = "True"
                else:
                    archiveFlag = "False"
                
                print(str(repo["id"]) + " : " + repo["name"] + " : " + repo["url"] + " : " + lastUpdate.strftime("%B %Y") + " : " + archiveFlag)
            else:
                print(f"Error getting Repo Data. Error {response.status_code}, {response.json()["message"]}")
                break
            
    else:
        print(f"Error getting user's organisations. Error {response.status_code}, {response.json()["message"]}")


if __name__ == "__main__":
    if not os.path.exists(".env"):
        print("Github Access Token Required.")
        token = input("Please enter a Github Access Token for your Account: ")

        if token != "":
            with open(".env", "w") as f:
                f.write(f'TOKEN="{token}"')

    gh = APIHandler()
    userData = gh.get("/user", {})

    if userData.status_code == 200:
        json = userData.json()

        # Output confirmation
        print(f"Authenticated as: {json["name"]} ({json["login"]})")

        # Start CLI
        exitCode = False

        while not exitCode:
            selection = input(""" \n
Please Select an Option:
1. View Profile
2. View Followers/Following
3. View Repos
4. Create Repo
5. Delete Repo
6. Update Bio
7. Get Organisation Repos not updated in the last x years
                                  
Type -1 to Quit.
""")
            clearTerminal()
            match selection:
                case "1":
                    viewProfile(json)
                case "2":
                    viewFollows(json)
                case "3":
                    viewRepos(json)
                case "4":
                    createRepo(json["login"])
                case "5":
                    deleteRepo()
                case "6":
                    editBio()
                case "7":
                    GetOrgRepos()
                case "-1":
                    exitCode = True
                # Default
                case _:
                    print("Invalid Input")

                    
    else:
        print(f"Error Getting User Data. Error {userData.status_code}, {userData.json()["message"]}")