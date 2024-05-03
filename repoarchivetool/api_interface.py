import requests
import datetime

# api_controller class to manage all API interactions
class api_controller():
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

    def get(self, url: str, params: dict, add_prefix: bool = True) -> requests.Response:
        """
            Performs a get request using the passed url.

            Args:
                url (str): The url endpoint of the request.
                params (dict): A Dictionary containing any Query Parameters.
                add_prefix (bool): A Boolean determining whether to add the "https://api.github.com" prefix
                to the beginning of the passed url.

            Returns:
                Response: The response from the API.
        """
        if add_prefix:
            url = "https://api.github.com" + url
        return requests.get(url=url, headers=self.headers, params=params)
    
    def patch(self, url, params, add_prefix: bool = True):
        """
            Performs a patch request using the passed url.

            Args:
                url (str): The url endpoint of the request.
                params (dict): A Dictionary containing any Query Parameters.
                add_prefix (bool): A Boolean determining whether to add the "https://api.github.com" prefix
                to the beginning of the passed url.

            Returns:
                Response: The response from the API.
        """
        if add_prefix:
            url = "https://api.github.com" + url
        return requests.patch(url=url, headers=self.headers, json=params)
    
    def post(self, url, params, add_prefix: bool = True):
        """
            Performs a post request using the passed url.

            Args:
                url (str): The url endpoint of the request.
                params (dict): A Dictionary containing any Query Parameters.
                add_prefix (bool): A Boolean determining whether to add the "https://api.github.com" prefix
                to the beginning of the passed url.

            Returns:
                Response: The response from the API.
        """
        if add_prefix:
            url = "https://api.github.com" + url
        return requests.post(url=url, headers=self.headers, json=params)
    
    def delete(self, url, add_prefix: bool = True):
        """
            Performs a delete request using the passed url.

            Args:
                url (str): The url endpoint of the request.
                params (dict): A Dictionary containing any Query Parameters.
                add_prefix (bool): A Boolean determining whether to add the "https://api.github.com" prefix
                to the beginning of the passed url.

            Returns:
                Response: The response from the API.
        """
        if add_prefix:
            url = "https://api.github.com" + url

        return requests.delete(url=url, headers=self.headers)


def get_organisation_repos(org: str, date: str, repo_type: str, gh: api_controller) -> str | list:
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
            repo_type (str): The type of repository to be returned (public, private, internal or all).
            gh (api_controller): An instance of the APIHandler class to interact with the Github API.

        Returns:
            str: An error message.
            or
            list: A list of dictionaries containing information about the repositories collected from 
            the Github API.
    """

    
    def archive_flag(repo_url: str, comp_date: date) -> bool | str:
        """
            Calculates whether a given repo should be archived or not.

            ==========

            Gets the given repository's information using the given repoUrl.
            Gets the repository's pushed_at date and converts it from a string to a date object (now called lastUpdate).
            Compares lastUpdate to compDate.
            If lastUpdate is before compDate return True, otherwise False.

            Args:
                repo_url (str): The API URL of the repository.
                comp_date (date): The date which repositories that have been committed prior to should be archived.

            Returns:
                str: An error message.
                or
                bool: Whether the repository should be archived or not.
        """

        archive_flag = False
        repo_response = gh.get(repo_url, {}, False)
                
        if repo_response.status_code == 200:
            repo_json = repo_response.json()
            last_update = repo_json["pushed_at"]
            last_update = datetime.datetime.strptime(last_update, "%Y-%m-%dT%H:%M:%SZ")
            last_update = datetime.date(last_update.year, last_update.month, last_update.day)

            archive_flag = True if last_update < comp_date else False
        
        else:
            return f"Error {repo_response.status_code}: {repo_response.json()["message"]} <br> Point of Failure: Getting Archive Flag."

        return archive_flag


    # Test API Call
    response = gh.get(f"/orgs/{org}/repos", {"sort": "pushed", "type": repo_type, "per_page": 2, "page": 1})

    if response.status_code == 200:
        # - Finds where the inputted date is in the list of repos (this position will be held in midpoint)
        # - After the midpoint is found, everything to the right of it can be archived as it is older than the inputted date

        # Get Number of Pages 
        try:
            last_page = int(response.links["last"]["url"].split("=")[-1])
        except KeyError:
            # If Key Error, Last doesn't exist therefore 1 page
            lastPage = 1

        upper_pointer = last_page
        midpoint = 1
        lower_pointer = 1
        midpoint_found = False

        year, month, day = date.split("-")
        x_date = datetime.date(int(year), int(month), int(day))
        comp_date = x_date

        while not midpoint_found:
            if upper_pointer - lower_pointer != 1 and upper_pointer - lower_pointer != 0:

                midpoint = lower_pointer + round((upper_pointer - lower_pointer) / 2)

                response = gh.get(f"/orgs/{org}/repos", {"sort": "pushed", "type": repo_type, "per_page": 2, "page": midpoint})
                repos = response.json()

                min_repo_flag = archive_flag(repos[0]["url"], comp_date)
                max_repo_flag = archive_flag(repos[-1]["url"], comp_date)

                # If min or max flags are of type string, an error has occured
                if type(min_repo_flag) == str:
                    return min_repo_flag
                
                if type(max_repo_flag) == str:
                    return max_repo_flag

            
                if not min_repo_flag and max_repo_flag:
                    midpoint_found = True
                elif min_repo_flag and max_repo_flag:
                    upper_pointer = midpoint
                else:
                    lower_pointer = midpoint
            
            else:
                # If upper - lower = 1, pointers are next to eachother
                # If the previous min and max flags are True, it needs to archive from the lower pointer
                # If the previous min and max flags are False, it needs to archive from the upper bound

                # Check if min and max flags exist, if they don't, only 2 pages.
                # Need to then calculate midpoint
                try:
                    print(min_repo_flag)
                except UnboundLocalError:
                    response = gh.get(f"/orgs/{org}/repos", {"sort": "pushed", "type": repo_type, "per_page": 2, "page": midpoint})
                    repos = response.json()

                    min_repo_flag = archive_flag(repos[0]["url"], comp_date)
                    max_repo_flag = archive_flag(repos[-1]["url"], comp_date)

                if min_repo_flag and max_repo_flag:
                    midpoint = lower_pointer
                if not min_repo_flag and not max_repo_flag:
                    midpoint = upper_pointer

                midpoint_found = True
        
        # Now midpoint is found, iterate through each repo between midpoint page and last page
        # only need to check dates for midpoint page
        # everything after midpoint can be archived
                
        # List to hold Repos
        repos_to_archive = []

        # For each repo between the midpoint and last page
        for i in range(midpoint, last_page+1):
            # Get the page
            response = gh.get(f"/orgs/{org}/repos", {"sort": "pushed", "type": repo_type, "per_page": 2, "page": i})

            if response.status_code == 200:
                page_repos = response.json()

                # For each repo in the page
                for repo in page_repos:
                    # Get that repo
                    repo_response = gh.get(repo["url"], {}, False)
                    
                    if repo_response.status_code == 200:
                        repo_json = repo_response.json()

                        last_update = repo_json["pushed_at"]
                        last_update = datetime.datetime.strptime(last_update, "%Y-%m-%dT%H:%M:%SZ")
                        last_update = datetime.date(last_update.year, last_update.month, last_update.day)

                        # If not on the midpoint page, archive
                        if i != midpoint:
                            archive_flag = "True"

                        # If on the midpoint page, need to check repo date
                        else:                           
                            archive_flag = True if last_update < comp_date else False
                        
                        # If needs archiving and hasn't already been archived, add it to the archive list
                        if not repo["archived"] and archive_flag:
                            repos_to_archive.append({
                                "name": repo["name"],
                                "type": repo["visibility"],
                                "apiUrl": repo["url"],
                                "lastCommitDate": str(last_update),
                                "contributorsUrl": repo["contributors_url"],
                                "htmlUrl": repo["html_url"]
                            })
                    else:
                        return f"Error {response.status_code}: {response.json()["message"]} <br> Point of Failure: Getting Individual Repositories."
            else: 
                return f"Error {response.status_code}: {response.json()["message"]} <br> Point of Failure: Getting Page of Repositories."
        
        return repos_to_archive
    else:
        return f"Error {response.status_code}: {response.json()["message"]} <br> Point of Failure: Test API Call."
    

def get_repo_contributors(gh: api_controller, contributors_url: str) -> str | list:
    """
        Gets the list of contributors for a given repository.

        ==========

        Args:
            gh (api_controller): An instance of the APIHandler class.
            contributors_url (str): The Github API endpoint URL for the repository's contributors.

        Returns:
            str: An error message.
            or
            list: A list of dictionaries containing information about the contributors to the given 
            repository collected from the Github API.
    """

    # Get contributors information
    response = gh.get(contributors_url, {}, False)

    if response.status_code not in (200, 204):
        return f"Error {response.status_code}: {response.json()["message"]}"

    contributor_list = []

    if response.status_code == 200:
        contributors = response.json()
        
        for contributor in contributors:
            contributor_list.append({
                "avatar": contributor["avatar_url"],
                "login": contributor["login"],
                "url": contributor["html_url"],
                "contributions": contributor["contributions"]
            })

    return contributor_list