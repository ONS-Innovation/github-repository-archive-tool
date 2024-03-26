# Github API App
A Python application to archive outdated organisation repositories.

## Setup
1. Install Poetry using `pip install poetry`.
2. Navigate into the project's folder and create a virtual environement using `python3 -m venv <environment_name>`.
3. Activate the environment using `source <environment_name>/bin/activate`.
4. Run `Poetry install` to install all the required dependencies.
5. Run the project using `poetry run python3 githubapiapp/__init__.py`.

## First Execution
When you first run the script, it will ask for an access token to authenticate with the Github API.
![CLI Asking for PAT token](/assets/readme/PAT1.png)

This must be generated on Github.

1. Go to Settings > Developer Settings > Personal Access Tokens > Fine-grained Tokens.
2. Next, Click **Generate new token**
![New Fine-grained token UI](/assets/readme/PAT2.png)

3. Create a new token by filling in the fields appropriately. **Make sure to select the organisation as the Resource Owner.**
![Resource Owner Field](/assets/readme/PAT3.png)
4. Give the token access to **All Repositories** and, under Repository Permissions, **Administration (Read and Write)** and **Metadata (Read-only)** access.
![Repository Access](/assets/readme/PAT4.png)
![Administration Permission](/assets/readme/PAT5.png)
![Metadata Permission](/assets/readme/PAT6.png)

5. Generate the token and make a note of it.
6. An owner of the Organisation will then need to approve the token before use.
7. Input the token into the CLI.

The script is now ready for use.

## Future Developments
1. Flask UI
2. Adapt CLI script to use UI
3. Email Notification to Repo Owner
4. Some way to prevent archive if needed
5. Archive Repo 30 days from notif
6. Update README with Flask instructions (once setup)
