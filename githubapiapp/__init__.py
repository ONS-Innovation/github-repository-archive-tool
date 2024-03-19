import requests
import dotenv
import os
import datetime
from tqdm import tqdm


def clearTerminal():
    os.system('cls' if os.name == 'nt' else 'clear')

# APIHandler class to manage all API interactions
class APIHandler():
    def __init__(self) -> None:
        """
            Creates the header attribute containing the Personal Access token to make auth'd API requests.
        """
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


def GetOrgRepos():
    """ 
        Gets a list of repos which haven't been pushed to since a given date.
        These are currently written to archive.txt but will be automatically archived in the future
    """

    
    def archiveFlag(repoUrl: str, compDate):
        """
            Calculates whether a given repo should be archived or not.

            Returns True or Falase
        """

        archiveFlag = False
        repoResponse = gh.get(repoUrl, {}, False)
                
        if repoResponse.status_code == 200:
            repoJson = repoResponse.json()
            lastUpdate = repoJson["pushed_at"]
            lastUpdate = datetime.datetime.strptime(lastUpdate, "%Y-%m-%dT%H:%M:%SZ")
            lastUpdate = datetime.date(lastUpdate.year, lastUpdate.month, lastUpdate.day)

            archiveFlag = True if lastUpdate < compDate else False
        
        else:
            print(f"Error getting user's organisations. Error {repoResponse.status_code}, {repoResponse.json()["message"]}")

        return archiveFlag

    # Get Org name
    org = input("Enter the Organisation Name: ")

    # If this used UI, it would have validation
    xDate = input("Enter the date you want to archive around (dd-mm-yyyy): ")
    day, month, year = xDate.split("-")
    xDate = datetime.date(int(year), int(month), int(day))

    # Test API Call
    response = gh.get(f"/orgs/{org}/repos", {"sort": "pushed", "per_page": 2, "page": 1})

    if response.status_code == 200:
        # - Finds where the inputted date is in the list of repos (this position will be held in midpoint)
        # - After the midpoint is found, everything to the right of it can be archived as it is older than the inputted date

        # Get Number of Pages 
        lastPage = int(response.links["last"]["url"].split("=")[-1])
        print(f"{lastPage} pages. {lastPage*2} Repositories Found.")


        upperPointer = lastPage
        midpoint = 0
        lowerPointer = 1
        midpointFound = False

        compDate = xDate

        print("Calculating Midpoint... Please wait...")

        while not midpointFound:
            if upperPointer - lowerPointer != 1:

                midpoint = lowerPointer + round((upperPointer - lowerPointer) / 2)

                response = gh.get(f"/orgs/{org}/repos", {"sort": "pushed", "per_page": 2, "page": midpoint})
                repos = response.json()

                minRepoFlag = archiveFlag(repos[0]["url"], compDate)
                maxRepoFlag = archiveFlag(repos[-1]["url"], compDate)

                # print("\n")
                # print("min: " + str(minRepoFlag))
                # print("max: " + str(maxRepoFlag))
                # print("lower: " + str(lowerPointer))
                # print("mp: " + str(midpoint))
                # print("upper: " + str(upperPointer))

                if not minRepoFlag and maxRepoFlag:
                    midpointFound = True
                elif minRepoFlag and maxRepoFlag:
                    upperPointer = midpoint
                else:
                    lowerPointer = midpoint
            
            else:
                # If upper - lower = 1, pointers are next to eachother
                # If the previous min and max flags are True, it needs to archive from the lower pointer
                # If the previous min and max flags are False, it needs to archive from the upper bound

                if minRepoFlag and maxRepoFlag:
                    midpoint = lowerPointer
                else:
                    midpoint = upperPointer
                midpointFound = True
        
        # Now midpoint is found, iterate through each repo between midpoint page and last page
        # only need to check dates for midpoint page
        # everything after midpoint can be archived
                
        print(f"Midpoint found (Page {midpoint}). Writing archivable repos to archive.txt...")

        # For now just store them in a text file
        reposToArchive = []

        # For each repo between the midpoint and last page
        for i in tqdm(range(midpoint, lastPage+1), "Getting Repository Data"):
            # Get the page
            response = gh.get(f"/orgs/{org}/repos", {"sort": "pushed", "per_page": 2, "page": i})

            if response.status_code == 200:
                pageRepos = response.json()

                # For each repo in the page
                for repo in pageRepos:
                    # Get that repo
                    repoResponse = gh.get(repo["url"], {}, False)
                    
                    if repoResponse.status_code == 200:
                        repoJson = repoResponse.json()

                        # If not on the midpoint page, archive
                        if i != midpoint:
                            archiveFlag = "True"

                        # If on the midpoint page, need to check repo date
                        else:
                            lastUpdate = repoJson["pushed_at"]
                            lastUpdate = datetime.datetime.strptime(lastUpdate, "%Y-%m-%dT%H:%M:%SZ")
                            lastUpdate = datetime.date(lastUpdate.year, lastUpdate.month, lastUpdate.day)
                            
                            archiveFlag = True if lastUpdate < compDate else False
                        
                        # If needs archiving and hasn't already been archived, add it to the archive list
                        if not repo["archived"] and archiveFlag:
                            # print(str(repo["id"]) + " : " + repo["name"] + " : " + repo["url"] + " : " + repo["visibility"] + " : " + str(repo["archived"]) + " : " + lastUpdate.strftime("%B %Y") + " : " + archiveFlag)
                            reposToArchive.append(repo["html_url"])
                    else:
                        print(f"Error getting Repo Data. Error {response.status_code}, {response.json()["message"]}")
                        break
            else: 
                print(f"Error getting organisation Repos. Error {response.status_code}, {response.json()["message"]}")
        
        # Write all repos in the archive list to Archive.txt (Will change to archive script later)
        with open("archive.txt", "w") as f:
            for url in tqdm(reposToArchive, "Writing Repositories to archive.txt"):
                f.write(url + "\n")
        print("Write Complete.")
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

        GetOrgRepos()
    else:
        print(f"Error Getting User Data. Error {userData.status_code}, {userData.json()["message"]}")