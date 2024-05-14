# Github API App
A Python application to archive outdated organisation repositories.

## Setup
1. Install Poetry using `pip install poetry`.
2. Navigate into the project's folder and create a virtual environement using `python3 -m venv <environment_name>`.
3. Activate the environment using `source <environment_name>/bin/activate`.
4. Run `Poetry install` to install all the required dependencies.
5. Insert the .pem file for the Github App into /repoarchivetool (see below).
6. Navigate into the repoarchivetool directory.
7. Run the project using `poetry run python3 app.py`.

## Getting a .pem file for the Github App
A .pem file is used to allow the project to make authorised Github API requests through the means of Github App authentication.
The project uses authentication as a Github App installation ([documentation](https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/authenticating-as-a-github-app-installation)).

In order to get a .pem file, a Github App must be created an installed into the organisation of which the app will be managing.
This app should have **Read and Write Administration** permission and **read-only Metadata** permission.

Once created and installed, you need to generate a Private Key for that Github App. This will download a .pem file to your pc.
This file needs to be called .pem ([documentation](https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/managing-private-keys-for-github-apps)). If it isn't named .pem, please rename it.

If you do not have access to organisation settings, you need to request a .pem file for the app.

## Future Developments
- Email Notification to Repo Owner at time of storage
- Add front end filter for repo type