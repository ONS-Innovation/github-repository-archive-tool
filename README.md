# Github API App
A simple python program which uses the Github API to do things.
The projects is made to gain more experience with the Github API and to start looking 
into the use of Poetry to better manage projects and dependencies.

This is a CLI project but might be updated to use Flask in the future (also to gain XP).

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
- Add a parameter for the Repo type:
    - All
    - Internal
    - Public
    - Private
- ~~Codebase Clean-up and Refactor~~ 
- Data Logging for analysis (very future)