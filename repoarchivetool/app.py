import flask
from datetime import datetime, timedelta, date
import os
import json
from dateutil.relativedelta import relativedelta

import apiScript

archive_threshold_days = 30

app = flask.Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)

@app.before_request
def checkPAT():
    """
        Before any request, check if Personal Access Token is defined.
        If it's not, return a render of accessToken.html
    """
    if "pat" not in flask.session and flask.request.endpoint != "login":
        return flask.render_template('accessToken.html')

@app.route('/', methods=['POST', 'GET'])
def index():
    """
        Returns a render of index.html.
    """

    return flask.render_template('findRepositories.html', date=(datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"))

@app.route('/login', methods=['POST', 'GET'])
def login():
    """
        Registers the user's inputted personal access token for Github Authentication.

        ==========

        When posted to, the function will set the session variable, pat, to the posted value.
        The session variable is intended to hold the user's personal access token for Github API authentication.

        Returns a redirect back to the homepage.
    """
    if flask.request.method == 'POST':
        flask.session['pat'] = flask.request.form['pat']

        # No need to test token here as tested when getting repos

    return flask.redirect('/')

@app.route('/logout')
def logout():
    """
        Removes the user's personal access token.
        
        ==========
        
        Unsets the session variable, pat, which holds the user's personal access token.

        Returns a redirect back to the homepage.
    """
    # remove the username from the session if it's there
    flask.session.pop('pat', None)
    return flask.redirect('/')

@app.route('/find_repositories', methods=['POST', 'GET'])
def findRepos():
    """
        Gets and stores any Github repositories, using apiScript.py, which fits the given parameters.
        
        ==========
        
        When posted to, the function will use the inputted values from the homepage to make
        a request to the Github API using apiScript.py and its APIHandler class.
        The request will return any repositories which fit the inputted parameters, in which
        this function will store ANY NEW repositories in JSON (repositories.json).

        If this function is not posted to, it will return a redirect to the homepage.

        If the function receives an error after using apiScript.py, it will return a render of
        error.html with an appropriate error message.

        If the function is successful with obtaining the information, it will return a redirect to
        /manage_repositories with an in-URL arguement (reposAdded) which is used to display how many
        repositories are added to JSON.
    """
    if flask.request.method == 'POST':
        try:
            # Create APIHandler instance
            gh = apiScript.APIHandler(flask.session['pat'])
        
        except KeyError:
            return flask.render_template('error.html', pat='', error='Personal Access Token Undefined.')
        
        else:
            # Get form values
            org = flask.request.form['org']
            date = flask.request.form['date']
            repoType = flask.request.form['repoType']

            newRepos = apiScript.GetOrgRepos(org, date, repoType, gh)

            if type(newRepos) == str:
                # Error Message Returned                
                try:
                    return flask.render_template('error.html', pat=flask.session['pat'], error=newRepos)
                except KeyError:
                    return flask.render_template('error.html', pat='', error=newRepos)

            # Get current date for logging purposes
            currentDate = datetime.today().strftime("%Y-%m-%d")

            reposAdded = 0

            # Get repos from storage
            try:
                with open("repositories.json", "r") as f:
                    storedRepos = json.load(f) 
            except FileNotFoundError:
                # File doesn't exist therefore no repos stored
                storedRepos = []

            for repo in newRepos:
                if not any(d["name"] == repo["name"] for d in storedRepos):
                    contributorList = apiScript.getRepoContributors(gh, repo["contributorsUrl"])

                    storedRepos.append({
                        "name": repo["name"],
                        "type": repo["type"],
                        "contributors": contributorList,
                        "apiUrl": repo["apiUrl"],
                        "lastCommit": repo["lastCommitDate"],
                        "dateAdded": currentDate,
                        "exemptUntil": "1900-01-01"
                    })

                    reposAdded += 1

            with open("repositories.json", "w") as f:
                f.write(json.dumps(storedRepos, indent=4))
                
            return flask.redirect(f'/manage_repositories?reposAdded={reposAdded}')
    
    return flask.redirect('/')
    
@app.route('/manage_repositories')
def manageRepos():
    """
        Returns a render of manageRepositories.html.

        ==========
        
        Loads a list of repositories from repositories.json to display within the render.

        This function can also be passed an arguement called reposAdded, which is used to
        display a success message when being redirected from findRepos().
    """

    # Get repos from storage
    try:
        with open("repositories.json", "r") as f:
            repos = json.load(f) 
            repos.sort(key=lambda x: x["name"])
    except FileNotFoundError:
        # File doesn't exist therefore no repos stored
        repos = []

    reposAdded = flask.request.args.get("reposAdded")

    if reposAdded == None:
        reposAdded = -1
    else:
        reposAdded = int(reposAdded)

    # When loading repos, check each repo to see if its exempt date has passed
    for i in range(0, len(repos)):
        if repos[i]["exemptUntil"] != "1900-01-01" and datetime.strptime(repos[i]["exemptUntil"], "%Y-%m-%d") < datetime.today():
            repos[i]["exemptUntil"] = "1900-01-01"
            repos[i]["dateAdded"] = datetime.strftime(datetime.today(), "%Y-%m-%d")
    
    with open("repositories.json", "w") as f:
        f.write(json.dumps(repos, indent=4))

    return flask.render_template("manageRepositories.html", repos=repos, reposAdded=reposAdded)

@app.route('/clear_repositories')
def clearRepos():
    """ 
        Removes all stored repositories by deleting repositories.json.
        
        Returns a redirect to manage_repositories.
    """
    os.remove("repositories.json")
    return flask.redirect('/manage_repositories')

@app.route('/set_exempt_date', methods=['POST', 'GET'])
def set_exempt_date():
    repo_name = flask.request.args.get("repoName")

    if repo_name == None:
        return flask.redirect("/manage_repositories")

    if flask.request.method == "POST":
        months_select_value = flask.request.form['date']

        if months_select_value == "-1":
            months_select_value = flask.request.form['months']
            
        exempt_until = datetime.today() + relativedelta(months=int(months_select_value))
        exempt_until = exempt_until.strftime("%Y-%m-%d")

        # Get repos from storage
        try:
            with open("repositories.json", "r") as f:
                repos = json.load(f) 
                repos.sort(key=lambda x: x["name"])
        except FileNotFoundError:
            # File doesn't exist therefore no repos stored
            repos = []

        for i in range(0, len(repos)):
            if repos[i]["name"] == repo_name:
                repos[i]["exemptUntil"] = exempt_until

        with open("repositories.json", "w") as f:
                f.write(json.dumps(repos, indent=4))
    
    else:
        return flask.render_template("setExemptDate.html", repoName=repo_name)
    
    return flask.redirect("/manage_repositories")

@app.route('/clear_exempt_date')
def clear_exempt_date():
    repo_name = flask.request.args.get("repoName")

    if repo_name != None:
        # Get repos from storage
        try:
            with open("repositories.json", "r") as f:
                repos = json.load(f) 
                repos.sort(key=lambda x: x["name"])
        except FileNotFoundError:
            # File doesn't exist therefore no repos stored
            repos = []

        for i in range(0, len(repos)):
            if repos[i]["name"] == repo_name:
                repos[i]["dateAdded"] = datetime.now().strftime("%Y-%m-%d")
                repos[i]["exemptUntil"] = "1900-01-01"

        with open("repositories.json", "w") as f:
                f.write(json.dumps(repos, indent=4))

    return flask.redirect("/manage_repositories")
    

@app.route('/archive_repositories', methods=['POST', 'GET'])
def archiveRepos():
    """
        Archives any repositories which are:
            - older than archive_threshold_days days within the system
            - have not been marked to be kept using the keep attribute in repositories.json
        
        ==========
        
        Creates an instance of the APIHandler class from apiScript.py.
        Loads any archive batches from archived.json into archiveList.
        Loads all stored repositories from repositories.json into repos.
        Adds any repositories older than archive_threshold_days days which do not have a keep attribute of True
        to the reposToRemove array.
        If there are repositories which need archiving, archive them using a patch request from the
        APIHandler class instance.
        Store the status of the archive attempt in archiveInstance["repos"].
        Add the new archiveInstance to archiveList and write it to archived.json.
        Remove any archived repositories from repos and write it to repositories.json.

        Returns a redirect to recentlyArchived.

        If the function fails to create an APIHandler instance, it will return a render of error.html
        with an appropriate error message.

    """
    try:
        gh = apiScript.APIHandler(flask.session['pat'])
    except KeyError:
        return flask.render_template('error.html', pat='', error='Personal Access Token Undefined.')

    # Get archive batches from storage
    try:
        with open("archived.json", "r") as f:
            archiveList = json.load(f)
    except FileNotFoundError:
        archiveList = []

    archiveInstance = {
        "batchID": len(archiveList)+1,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "repos": []
    }

    reposToRemove = []

    # Get repos from storage
    with open("repositories.json", "r") as f:
        repos = json.load(f)

    # For each repo, if keep is false and it was added to storage over archive_threshold_days days ago,
    # Archive them
    for i in range(0, len(repos)):
        if repos[i]["exemptUntil"] == "1900-01-01":
            if (datetime.now() - datetime.strptime(repos[i]["dateAdded"], "%Y-%m-%d")).days >= archive_threshold_days:
                response = gh.patch(repos[i]["apiUrl"], {"archived":True}, False)

                if response.status_code == 200:

                    archiveInstance["repos"].append({
                        "name": repos[i]["name"],
                        "apiurl": repos[i]["apiUrl"],
                        "status": "Success",
                        "message": "Repository Archived Successfully."
                    })

                    reposToRemove.append(i)

                else:
                    archiveInstance["repos"].append({
                        "name": repos[i]["name"],
                        "apiurl": repos[i]["apiUrl"],
                        "status": "Failed",
                        "message": f"Error {response.status_code}: {response.json()["message"]}"
                    })

    # If repos have been archived, log changes in storage 
    if len(archiveInstance["repos"]) > 0:
        
        archiveList.append(archiveInstance)

        with open("archived.json", "w") as f:
            f.write(json.dumps(archiveList, indent=4))

        popCount = 0
        for i in reposToRemove:
            repos.pop(i - popCount)
            popCount += 1

        with open("repositories.json", "w") as f:
            f.write(json.dumps(repos, indent=4))

    return flask.redirect('/recently_archived')

@app.route('/recently_archived')
def recentlyArchived():
    """
        Returns a render of recentlyArchived.html.

        ==========

        Loads a list of archive batches from archived.json to display within the render.

        This function can also be passed an arguement called batchID, which is used to 
        display a success message when redirected from undoBatch().
    """

    # Get archive batches from storage
    try:
        with open("archived.json", "r") as f:
            archiveList = json.load(f)
            archiveList.reverse()
    except FileNotFoundError:
        archiveList = []

    batchID = flask.request.args.get("batchID")

    if batchID == None:
        batchID = ""

    try:
        return flask.render_template('recentlyArchived.html', archiveList=archiveList, batchID=batchID)
    except KeyError:
        return flask.render_template('recentlyArchived.html', archiveList=archiveList, batchID=batchID)

@app.route('/undo_batch')
def undoBatch():
    """
        Unarchives a batch of archived repositories.

        ==========

        Creates an instance of the APIHandler class from apiScript.py.
        Gets the passed batchID arguement.
        Loads any archive batches from archived.json into archiveList.
        Gets the batch that needs undoing from archiveList using the given batchID.
        Unarchives all repositories within the batch using a patch request from the APIHandler class instance.
        Loads all stored repositories from repositories.json into storedRepos.
        If any now unarchived repositories are not already stored, fetch their information from Github using a get request
        from the APIHandler class instance and add it to storedRepos.
        Write storedRepos back to repositories.json.
        Remove any now archived repositories from the batch in archiveList and write it back to archived.json.

        Returns a redirect to recentlyArchived with a passed arguement, batchID, which is used to show a success message.

        If the function fails to create an APIHandler instance, it will return a render of error.html
        with an appropriate error message.

        If the function fails to unarchive a repository or get the repository's information from Github, it will return a render of error.html
        with an appropriate error message.
    """
    try:
        gh = apiScript.APIHandler(flask.session['pat'])
    except KeyError:
        return flask.render_template('error.html', pat='', error='Personal Access Token Undefined.')

    batchID = flask.request.args.get("batchID")

    if batchID != None:
        batchID = int(batchID)

        with open("archived.json", "r") as f:
            archiveList = json.load(f)

        batchToUndo = archiveList[batchID - 1]

        popCount = 0

        for i in range(0, len(batchToUndo["repos"])):
            # Unarchive the repo
            response = gh.patch(batchToUndo["repos"][i - popCount]["apiurl"], {"archived": False}, False)

            if response.status_code != 200:
                return flask.render_template('error.html', pat=flask.session['pat'], error=f"Error {response.status_code}: {response.json()["message"]} <br> Point of Failure: Unarchiving batch {batchID}, {batchToUndo["repos"][i - popCount]["name"]}")

            # Add the repo to repositories.json
            # Get repos from storage
            try:
                with open("repositories.json", "r") as f:
                    storedRepos = json.load(f) 
            except FileNotFoundError:
                # File doesn't exist therefore no repos stored
                storedRepos = []
            
            if not any(d["name"] == batchToUndo["repos"][i - popCount]["name"] for d in storedRepos):

                response = gh.get(batchToUndo["repos"][i - popCount]["apiurl"], {}, False)

                if response.status_code != 200:
                    return flask.render_template('error.html', pat=flask.session['pat'], error=f"Error {response.status_code}: {response.json()["message"]} <br> Point of Failure: Restoring batch {batchID}, {batchToUndo["repos"][i - popCount]["name"]} to stored repositories")

                repoJson = response.json()

                currentDate = datetime.now().strftime("%Y-%m-%d")

                lastUpdate = repoJson["pushed_at"]
                lastUpdate = datetime.strptime(lastUpdate, "%Y-%m-%dT%H:%M:%SZ")
                lastUpdate = date(lastUpdate.year, lastUpdate.month, lastUpdate.day)

                contributorList = apiScript.getRepoContributors(gh, repoJson["contributors_url"])

                storedRepos.append({
                    "name": repoJson["name"],
                    "type": repoJson["visibility"],
                    "contributors": contributorList,
                    "apiUrl": repoJson["url"],
                    "lastCommit": str(lastUpdate),
                    "dateAdded": currentDate,
                    "exemptUntil": "1900-01-01"
                })

            with open("repositories.json", "w") as f:
                f.write(json.dumps(storedRepos, indent=4))

            # Remove the repo from archived.json
            archiveList[batchID - 1]["repos"].pop(i - popCount)
            popCount += 1

            with open("archived.json", "w") as f:
                f.write(json.dumps(archiveList, indent=4))

        return flask.redirect(f"/recently_archived?batchID={batchID}")

    return flask.redirect("/")

@app.route('/confirm')
def confirmAction():
    message = flask.request.args.get("message")
    confirmUrl = flask.request.args.get("confirmUrl")
    cancelUrl = flask.request.args.get("cancelUrl")

    if message != None and confirmUrl != None and cancelUrl != None:
        return flask.render_template("confirmAction.html", message=message, confirmUrl=confirmUrl, cancelUrl=cancelUrl)

    return flask.redirect("/")

if __name__ == "__main__":
    app.run(debug=True)