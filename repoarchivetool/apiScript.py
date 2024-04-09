import requests
import datetime

# APIHandler class to manage all API interactions
class APIHandler():
    """
        A class used to interact with the Github API.

        The class can perform get, patch, post and delete requests using the
        get(), patch(), post() and delete() functions respectively.
    """
    def __init__(self, token) -> None:
        """
            Creates the header attribute containing the Personal Access token to make auth'd API requests.
        """
        self.headers = {"Authorization": "token " + token}

    def get(self, url: str, params: dict, addPrefix: bool = True) -> requests.Response:
        """
            Performs a get request using the passed url.

            Args:
                url (str): The url endpoint of the request.
                params (dict): A Dictionary containing any Query Parameters.
                addPrefix (bool): A Boolean determining whether to add the "https://api.github.com" prefix
                to the beginning of the passed url.

            Returns:
                Response: The response from the API.
        """
        if addPrefix:
            url = "https://api.github.com" + url
        return requests.get(url=url, headers=self.headers, params=params)
    
    def patch(self, url, params, addPrefix: bool = True):
        """
            Performs a patch request using the passed url.

            Args:
                url (str): The url endpoint of the request.
                params (dict): A Dictionary containing any Query Parameters.
                addPrefix (bool): A Boolean determining whether to add the "https://api.github.com" prefix
                to the beginning of the passed url.

            Returns:
                Response: The response from the API.
        """
        if addPrefix:
            url = "https://api.github.com" + url
        return requests.patch(url=url, headers=self.headers, json=params)
    
    def post(self, url, params, addPrefix: bool = True):
        """
            Performs a post request using the passed url.

            Args:
                url (str): The url endpoint of the request.
                params (dict): A Dictionary containing any Query Parameters.
                addPrefix (bool): A Boolean determining whether to add the "https://api.github.com" prefix
                to the beginning of the passed url.

            Returns:
                Response: The response from the API.
        """
        if addPrefix:
            url = "https://api.github.com" + url
        return requests.post(url=url, headers=self.headers, json=params)
    
    def delete(self, url, addPrefix: bool = True):
        """
            Performs a delete request using the passed url.

            Args:
                url (str): The url endpoint of the request.
                params (dict): A Dictionary containing any Query Parameters.
                addPrefix (bool): A Boolean determining whether to add the "https://api.github.com" prefix
                to the beginning of the passed url.

            Returns:
                Response: The response from the API.
        """
        if addPrefix:
            url = "https://api.github.com" + url

        return requests.delete(url=url, headers=self.headers)


def GetOrgRepos(org: str, date: str, repoType: str, gh: APIHandler) -> str | list:
    """ 
        Gets all repositories which fit the given parameters.

        ==========

        Makes a test call to the API.
        If successful, get the total number of repository pages (2 repositories per page)
        Convert the given string, date, to a date object.
        Calculate the midpoint of the repositories, which denotes where the given archive
        date is.
        Any repositories to the left of the midpoint page are newer than the given date,
        and cannot be archived.
        Any repositories to the right of the midpoint page are newer than the given date,
        and can be archived.
        For each repository between the midpoint and last page of repositories,
        add the repository to reposToArchive but only if it hasn't already been archived.
        Return reposToArchive.

        Args:
            org (str): The name of the organisation whose repositories are to be returned.
            date (str): The date which repositories that have been committed prior to will be archived.
            repoType (str): The type of repository to be returned (public, private, internal or all).
            gh (APIHandler): An instance of the APIHandler class to interact with the Github API.

        Returns:
            str: An error message.
            or
            list: A list of dictionaries containing information about the repositories collected from 
            the Github API.
    """

    
    def archiveFlag(repoUrl: str, compDate: date) -> bool | str:
        """
            Calculates whether a given repo should be archived or not.

            ==========

            Gets the given repository's information using the given repoUrl.
            Gets the repository's pushed_at date and converts it from a string to a date object (now called lastUpdate).
            Compares lastUpdate to compDate.
            If lastUpdate is before compDate return True, otherwise False.

            Args:
                repoUrl (str): The API URL of the repository.
                compDate (date): The date which repositories that have been committed prior to should be archived.

            Returns:
                str: An error message.
                or
                bool: Whether the repository should be archived or not.
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
            return f"Error {repoResponse.status_code}: {repoResponse.json()["message"]} <br> Point of Failure: Getting Archive Flag."

        return archiveFlag


    # Test API Call
    response = gh.get(f"/orgs/{org}/repos", {"sort": "pushed", "type": repoType, "per_page": 2, "page": 1})

    if response.status_code == 200:
        # - Finds where the inputted date is in the list of repos (this position will be held in midpoint)
        # - After the midpoint is found, everything to the right of it can be archived as it is older than the inputted date

        # Get Number of Pages 
        try:
            lastPage = int(response.links["last"]["url"].split("=")[-1])
        except KeyError:
            # If Key Error, Last doesn't exist therefore 1 page
            lastPage = 1

        upperPointer = lastPage
        midpoint = 1
        lowerPointer = 1
        midpointFound = False

        year, month, day = date.split("-")
        xDate = datetime.date(int(year), int(month), int(day))
        compDate = xDate

        while not midpointFound:
            if upperPointer - lowerPointer != 1 and upperPointer - lowerPointer != 0:

                midpoint = lowerPointer + round((upperPointer - lowerPointer) / 2)

                response = gh.get(f"/orgs/{org}/repos", {"sort": "pushed", "type": repoType, "per_page": 2, "page": midpoint})
                repos = response.json()

                minRepoFlag = archiveFlag(repos[0]["url"], compDate)
                maxRepoFlag = archiveFlag(repos[-1]["url"], compDate)

                # If min or max flags are of type string, an error has occured
                if type(minRepoFlag) == str:
                    return minRepoFlag
                
                if type(maxRepoFlag) == str:
                    return maxRepoFlag

            
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

                # Check if min and max flags exist, if they don't, only 2 pages.
                # Need to then calculate midpoint
                try:
                    print(minRepoFlag)
                except UnboundLocalError:
                    response = gh.get(f"/orgs/{org}/repos", {"sort": "pushed", "type": repoType, "per_page": 2, "page": midpoint})
                    repos = response.json()

                    minRepoFlag = archiveFlag(repos[0]["url"], compDate)
                    maxRepoFlag = archiveFlag(repos[-1]["url"], compDate)

                if minRepoFlag and maxRepoFlag:
                    midpoint = lowerPointer
                if not minRepoFlag and not maxRepoFlag:
                    midpoint = upperPointer

                midpointFound = True
        
        # Now midpoint is found, iterate through each repo between midpoint page and last page
        # only need to check dates for midpoint page
        # everything after midpoint can be archived
                
        # List to hold Repos
        reposToArchive = []

        # For each repo between the midpoint and last page
        for i in range(midpoint, lastPage+1):
            # Get the page
            response = gh.get(f"/orgs/{org}/repos", {"sort": "pushed", "type": repoType, "per_page": 2, "page": i})

            if response.status_code == 200:
                pageRepos = response.json()

                # For each repo in the page
                for repo in pageRepos:
                    # Get that repo
                    repoResponse = gh.get(repo["url"], {}, False)
                    
                    if repoResponse.status_code == 200:
                        repoJson = repoResponse.json()

                        lastUpdate = repoJson["pushed_at"]
                        lastUpdate = datetime.datetime.strptime(lastUpdate, "%Y-%m-%dT%H:%M:%SZ")
                        lastUpdate = datetime.date(lastUpdate.year, lastUpdate.month, lastUpdate.day)

                        # If not on the midpoint page, archive
                        if i != midpoint:
                            archiveFlag = "True"

                        # If on the midpoint page, need to check repo date
                        else:                           
                            archiveFlag = True if lastUpdate < compDate else False
                        
                        # If needs archiving and hasn't already been archived, add it to the archive list
                        if not repo["archived"] and archiveFlag:
                            reposToArchive.append({
                                "name": repo["name"],
                                "type": repo["visibility"],
                                "apiUrl": repo["url"],
                                "lastCommitDate": str(lastUpdate),
                                "contributorsUrl": repo["contributors_url"]
                            })
                    else:
                        return f"Error {response.status_code}: {response.json()["message"]} <br> Point of Failure: Getting Individual Repositories."
            else: 
                return f"Error {response.status_code}: {response.json()["message"]} <br> Point of Failure: Getting Page of Repositories."
        
        return reposToArchive
    else:
        return f"Error {response.status_code}: {response.json()["message"]} <br> Point of Failure: Test API Call."
    

def getRepoContributors(gh: APIHandler, contributorsUrl: str) -> str | list:
    """
        Gets the list of contributors for a given repository.

        ==========

        Args:
            gh (APIHandler): An instance of the APIHandler class.
            contributorsUrl (str): The Github API endpoint URL for the repository's contributors.

        Returns:
            str: An error message.
            or
            list: A list of dictionaries containing information about the contributors to the given 
            repository collected from the Github API.
    """

    # Get contributors information
    response = gh.get(contributorsUrl, {}, False)

    if response.status_code not in (200, 204):
        return f"Error {response.status_code}: {response.json()["message"]}"

    contributorList = []

    if response.status_code == 200:
        contributors = response.json()
        
        for contributor in contributors:
            contributorList.append({
                "avatar": contributor["avatar_url"],
                "login": contributor["login"],
                "url": contributor["html_url"],
                "contributions": contributor["contributions"]

                # Maybe add their email to contact them?
            })

    return contributorList