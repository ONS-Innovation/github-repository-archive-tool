# Github API App
A Python application to archive outdated organisation repositories.

## Setup
1. Install Poetry using `pip install poetry`.
2. Navigate into the project's folder and create a virtual environement using `python3 -m venv <environment_name>`.
3. Activate the environment using `source <environment_name>/bin/activate`.
4. Run `Poetry install` to install all the required dependencies.
5. Navigate into the repoarchivetool directory.
6. Run the project using `poetry run python3 app.py`.

## Getting a Personal Access Token (PAT)
Before you can use the application, you will need a Personal Access Token (PAT).

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

You can now input this into the app and use it.

## Data Storage
This application stores repository data within a text file (repositories.txt).

Each repository has 5 main parts which are separated by commas. Each repository entry is separated by semi-colons.

The example below represents 2 repositories within repositories.txt

![Data Storage Format](/assets/readme/DataStorage.png)

## Future Developments
- ~~Some sort of loading screen whilst it finds the repos~~
- Store Repos for archive and display them (In Progress)
    - ~~Need to add functionality to keep flag~~
    - ~~Make it so that new records are added instead of overwriting table~~
    - Need a success page once repos are stored
    - Need to separate find repos and manage repos into separate pages instead of using dynamic pills from BS5
    - Add table searching and filters (JS)
- Email Notification to Repo Owner
- Some way to prevent archive if needed (checkbox/button in display)
- Archive Repo 30 days from notif (will trigger on button press)
