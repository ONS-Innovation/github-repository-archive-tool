import flask
from datetime import datetime, timedelta
import os
import apiScript

app = flask.Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)

@app.route('/', methods=['POST', 'GET'])
def index():
    if flask.request.method == "POST":
        flask.session['pat'] = flask.request.form['pat']

    try:
        return flask.render_template('index.html', pat=flask.session['pat'], date=(datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"))
    except KeyError:
        return flask.render_template('index.html', pat='', date=(datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"))

@app.route('/login', methods=['POST', 'GET'])
def login():
    if flask.request.method == 'POST':
        flask.session['pat'] = flask.request.form['pat']

        # No need to test token here as tested when getting repos

        return flask.redirect('/')
    return flask.redirect('/')

@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    flask.session.pop('pat', None)
    return flask.redirect('/')

@app.route('/FindRepositories', methods=['POST', 'GET'])
def findRepos():
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

            repos = apiScript.GetOrgRepos(org, date, repoType, gh)

            if type(repos) == str:
                # Error Message Returned                
                try:
                    return flask.render_template('error.html', pat=flask.session['pat'], error=repos)
                except KeyError:
                    return flask.render_template('error.html', pat='', error=repos)

            # Get current date for logging purposes
            currentDate = datetime.today().strftime("%Y-%m-%d")

            reposAdded = 0

            try:
                with open("repositories.txt", "r+") as f:

                    storedRepos = f.read().split(";")
                    storedRepos.pop()

                    for i in range(0, len(storedRepos)):
                        storedRepos[i] = storedRepos[i].split(",")[0]

                    for repo in repos:
                        if repo['name'] not in storedRepos:
                            f.write(f"{repo['name']},{repo['apiUrl']},{repo['lastCommitDate']},{currentDate},0;")
                            reposAdded += 1
            
            except FileNotFoundError:
                with open("repositories.txt", "w") as f:
                    for repo in repos:
                        f.write(f"{repo['name']},{repo['apiUrl']},{repo['lastCommitDate']},{currentDate},0;")
                        reposAdded += 1
                
            return flask.redirect(f'/manageRepositories?reposAdded={reposAdded}')
            
            # Test to get repo owner email
            # need to make another api call to owner info and get it there
                
            # owner = gh.get("https://api.github.com/repos/ONS-Innovation/AI_Testing_App", {}, False).json()["owner"]["url"]
            # return gh.get(owner, {}, False).json()["email"]
    
    return flask.redirect('/')

@app.route('/manageRepositories')
def manageRepos():
    try:
        with open("repositories.txt", "r") as f:
            repos = f.read().split(";")
            repos.pop()

            for i in range(0, len(repos)):
                name, url, lastCommit, dateAdded, keep = repos[i].split(",")
                repos[i] = {
                    "name": name,
                    "dateAdded": dateAdded,
                    "lastCommit": lastCommit,
                    "keep": keep
                }
    except FileNotFoundError:
        repos = ""

    reposAdded = flask.request.args.get("reposAdded")

    if reposAdded == None:
        reposAdded = 0
    else:
        reposAdded = int(reposAdded)

    try:
        return flask.render_template('manageRepositories.html', pat=flask.session['pat'], repos=repos, reposAdded=reposAdded)
    except KeyError:
        return flask.render_template('manageRepositories.html', pat='', repos=repos, reposAdded=reposAdded)

@app.route('/clearRepositories')
def clearRepos():
    os.remove("repositories.txt")
    return flask.redirect('/manageRepositories')

@app.route('/changeKeepFlag')
def changeFlag():
    repoName = flask.request.args.get("repoName")

    if repoName == None:
        return flask.redirect('/manageRepositories')
    
    updatedRepos = []

    with open("repositories.txt", "r") as f:
        repos = f.read().split(';')
        repos.pop()

        for i in range(0, len(repos)):
            name, apiUrl, lastCommitDate, dateAdded, keep = repos[i].split(',')

            if repoName == name:
                if keep == "1":
                    updatedRepos.append(f"{name},{apiUrl},{lastCommitDate},{dateAdded},0;")
                else:
                    updatedRepos.append(f"{name},{apiUrl},{lastCommitDate},{dateAdded},1;")
            else:
                updatedRepos.append(f"{name},{apiUrl},{lastCommitDate},{dateAdded},{keep};")
    
    with open("repositories.txt", "w") as f:
        for repo in updatedRepos:
            f.write(repo)
        
    return flask.redirect('/manageRepositories')

@app.route('/archiveRepositories', methods=['POST', 'GET'])
def archiveRepos():
    try:
        gh = apiScript.APIHandler(flask.session['pat'])
    except KeyError:
        return flask.render_template('error.html', pat='', error='Personal Access Token Undefined.')

    # A list of dictionaries to keep track of what repos have been archived (w/ success status)
    archiveList = []

    with open("repositories.txt", "r") as f:
        repos = f.read().split(';')
        repos.pop()

        for i in range(0, len(repos)):
            name, apiUrl, lastCommitDate, dateAdded, keep = repos[i].split(',')

            if keep != 1:
                print((datetime.now() - datetime.strptime(dateAdded, "%Y-%m-%d")).days)

                if (datetime.now() - datetime.strptime(dateAdded, "%Y-%m-%d")).days >= 30:
                    response = gh.patch(apiUrl, {"archived":True}, False)

                    if response.status_code == 200:

                        archiveList.append({
                            "name": name,
                            "apiurl": apiUrl,
                            "status": "Success",
                            "message": "Repository Archived Successfully."
                        })

                    else:
                        archiveList.append({
                            "name": name,
                            "apiurl": apiUrl,
                            "status": "Failed",
                            "message": f"Error {response.status_code}: {response.json()["message"]}"
                        })

    return archiveList
    # return flask.redirect(f'/manageRepositories')

if __name__ == "__main__":
    app.run(debug=True)