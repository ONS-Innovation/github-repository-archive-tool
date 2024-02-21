import dotenv
import os
import requests

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

repoDelList = ['TEST', 'TEST2', 'TEST3', 'test34', 'test111', 'adhjadkl-adkl-adskl-', 'asdasdadadadadadadadads', 'asd', 'test5555', 'test22', 'adadsadadsadsadsads', 'asdf', 'adsadsads', 'adsadsadsadadadads']

gh = APIHandler()

for item in repoDelList:
    url = f"/repos/TotalDwarf03/{item}"
    response = gh.delete(url)

    print(f"{item}: {response}")