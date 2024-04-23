import flask
from datetime import datetime, timedelta, date
import os
import json
from dateutil.relativedelta import relativedelta

import api_controller

archive_threshold_days = 30

app = flask.Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)

@app.before_request
def check_pat():
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
def find_repos():
    """
        Gets and stores any Github repositories, using api_controller.py, which fits the given parameters.
        
        ==========
        
        When posted to, the function will use the inputted values from the homepage to make
        a request to the Github API using api_controller.py and its APIHandler class.
        The request will return any repositories which fit the inputted parameters, in which
        this function will store ANY NEW repositories in JSON (repositories.json).

        If this function is not posted to, it will return a redirect to the homepage.

        If the function receives an error after using api_controller.py, it will return a render of
        error.html with an appropriate error message.

        If the function is successful with obtaining the information, it will return a redirect to
        /manage_repositories with an in-URL arguement (reposAdded) which is used to display how many
        repositories are added to JSON.
    """
    if flask.request.method == 'POST':
        try:
            # Create APIHandler instance
            gh = api_controller.api_handler(flask.session['pat'])
        
        except KeyError:
            return flask.render_template('error.html', pat='', error='Personal Access Token Undefined.')
        
        else:
            # Get form values
            org = flask.request.form['org']
            date = flask.request.form['date']
            repo_type = flask.request.form['repoType']

            new_repos = api_controller.get_organisation_repos(org, date, repo_type, gh)

            if type(new_repos) == str:
                # Error Message Returned                
                try:
                    return flask.render_template('error.html', pat=flask.session['pat'], error=new_repos)
                except KeyError:
                    return flask.render_template('error.html', pat='', error=new_repos)

            # Get current date for logging purposes
            current_date = datetime.today().strftime("%Y-%m-%d")

            repos_added = 0

            # Get repos from storage
            try:
                with open("repositories.json", "r") as f:
                    stored_repos = json.load(f) 
            except FileNotFoundError:
                # File doesn't exist therefore no repos stored
                stored_repos = []

            for repo in new_repos:
                if not any(d["name"] == repo["name"] for d in stored_repos):
                    contributor_list = api_controller.get_repo_contributors(gh, repo["contributorsUrl"])

                    stored_repos.append({
                        "name": repo["name"],
                        "type": repo["type"],
                        "contributors": contributor_list,
                        "apiUrl": repo["apiUrl"],
                        "lastCommit": repo["lastCommitDate"],
                        "dateAdded": current_date,
                        "exemptUntil": "1900-01-01"
                    })

                    repos_added += 1

            with open("repositories.json", "w") as f:
                f.write(json.dumps(stored_repos, indent=4))
                
            return flask.redirect(f'/manage_repositories?reposAdded={repos_added}')
    
    return flask.redirect('/')
    
@app.route('/manage_repositories')
def manage_repos():
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

    repos_added = flask.request.args.get("reposAdded")

    if repos_added == None:
        repos_added = -1
    else:
        repos_added = int(repos_added)

    # When loading repos, check each repo to see if its exempt date has passed
    for i in range(0, len(repos)):
        if repos[i]["exemptUntil"] != "1900-01-01" and datetime.strptime(repos[i]["exemptUntil"], "%Y-%m-%d") < datetime.today():
            repos[i]["exemptUntil"] = "1900-01-01"
            repos[i]["dateAdded"] = datetime.strftime(datetime.today(), "%Y-%m-%d")
    
    with open("repositories.json", "w") as f:
        f.write(json.dumps(repos, indent=4))

    return flask.render_template("manageRepositories.html", repos=repos, reposAdded=repos_added)

@app.route('/clear_repositories')
def clear_repos():
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
def archive_repos():
    """
        Archives any repositories which are:
            - older than archive_threshold_days days within the system
            - have not been marked to be kept using the keep attribute in repositories.json
        
        ==========
        
        Creates an instance of the APIHandler class from api_controller.py.
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
        gh = api_controller.api_handler(flask.session['pat'])
    except KeyError:
        return flask.render_template('error.html', pat='', error='Personal Access Token Undefined.')

    # Get archive batches from storage
    try:
        with open("archived.json", "r") as f:
            archive_list = json.load(f)
    except FileNotFoundError:
        archive_list = []

    archive_instance = {
        "batchID": len(archive_list)+1,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "repos": []
    }

    repos_to_remove = []

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

                    archive_instance["repos"].append({
                        "name": repos[i]["name"],
                        "apiurl": repos[i]["apiUrl"],
                        "status": "Success",
                        "message": "Repository Archived Successfully."
                    })

                    repos_to_remove.append(i)

                else:
                    archive_instance["repos"].append({
                        "name": repos[i]["name"],
                        "apiurl": repos[i]["apiUrl"],
                        "status": "Failed",
                        "message": f"Error {response.status_code}: {response.json()["message"]}"
                    })

    # If repos have been archived, log changes in storage 
    if len(archive_instance["repos"]) > 0:
        
        archive_list.append(archive_instance)

        with open("archived.json", "w") as f:
            f.write(json.dumps(archive_list, indent=4))

        pop_count = 0
        for i in repos_to_remove:
            repos.pop(i - pop_count)
            pop_count += 1

        with open("repositories.json", "w") as f:
            f.write(json.dumps(repos, indent=4))

    return flask.redirect('/recently_archived')

@app.route('/recently_archived')
def recently_archived():
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
            archive_list = json.load(f)
            archive_list.reverse()
    except FileNotFoundError:
        archive_list = []

    batch_id = flask.request.args.get("batchID")

    if batch_id == None:
        batch_id = ""

    try:
        return flask.render_template('recentlyArchived.html', archiveList=archive_list, batchID=batch_id)
    except KeyError:
        return flask.render_template('recentlyArchived.html', archiveList=archive_list, batchID=batch_id)

@app.route('/undo_batch')
def undo_batch():
    """
        Unarchives a batch of archived repositories.

        ==========

        Creates an instance of the APIHandler class from api_controller.py.
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
        gh = api_controller.api_handler(flask.session['pat'])
    except KeyError:
        return flask.render_template('error.html', pat='', error='Personal Access Token Undefined.')

    batch_id = flask.request.args.get("batchID")

    if batch_id != None:
        batch_id = int(batch_id)

        with open("archived.json", "r") as f:
            archive_list = json.load(f)

        batch_to_undo = archive_list[batch_id - 1]

        pop_count = 0

        for i in range(0, len(batch_to_undo["repos"])):
            # Unarchive the repo
            response = gh.patch(batch_to_undo["repos"][i - pop_count]["apiurl"], {"archived": False}, False)

            if response.status_code != 200:
                return flask.render_template('error.html', pat=flask.session['pat'], error=f"Error {response.status_code}: {response.json()["message"]} <br> Point of Failure: Unarchiving batch {batch_id}, {batch_to_undo["repos"][i - pop_count]["name"]}")

            # Add the repo to repositories.json
            # Get repos from storage
            try:
                with open("repositories.json", "r") as f:
                    stored_repos = json.load(f) 
            except FileNotFoundError:
                # File doesn't exist therefore no repos stored
                stored_repos = []
            
            if not any(d["name"] == batch_to_undo["repos"][i - popCount]["name"] for d in stored_repos):

                response = gh.get(batch_to_undo["repos"][i - pop_count]["apiurl"], {}, False)

                if response.status_code != 200:
                    return flask.render_template('error.html', pat=flask.session['pat'], error=f"Error {response.status_code}: {response.json()["message"]} <br> Point of Failure: Restoring batch {batch_id}, {batch_to_undo["repos"][i - pop_count]["name"]} to stored repositories")

                repo_json = response.json()

                current_date = datetime.now().strftime("%Y-%m-%d")

                last_update = repo_json["pushed_at"]
                last_update = datetime.strptime(last_update, "%Y-%m-%dT%H:%M:%SZ")
                last_update = date(last_update.year, last_update.month, last_update.day)

                contributor_list = api_controller.get_repo_contributors(gh, repo_json["contributors_url"])

                stored_repos.append({
                    "name": repo_json["name"],
                    "type": repo_json["visibility"],
                    "contributors": contributor_list,
                    "apiUrl": repo_json["url"],
                    "lastCommit": str(last_update),
                    "dateAdded": current_date,
                    "exemptUntil": "1900-01-01"
                })

            with open("repositories.json", "w") as f:
                f.write(json.dumps(stored_repos, indent=4))

            # Remove the repo from archived.json
            archive_list[batch_id - 1]["repos"].pop(i - pop_count)
            popCount += 1

            with open("archived.json", "w") as f:
                f.write(json.dumps(archive_list, indent=4))

        return flask.redirect(f"/recently_archived?batchID={batch_id}")

    return flask.redirect("/")

@app.route('/confirm')
def confirm_action():
    message = flask.request.args.get("message")
    confirm_url = flask.request.args.get("confirmUrl")
    cancel_url = flask.request.args.get("cancelUrl")

    if message != None and confirm_url != None and cancel_url != None:
        return flask.render_template("confirmAction.html", message=message, confirmUrl=confirm_url, cancelUrl=cancel_url)

    return flask.redirect("/")

if __name__ == "__main__":
    app.run(debug=True)