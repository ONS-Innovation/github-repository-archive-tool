import jwt
import time
import requests

def get_access_token(org: str) -> tuple | str:
    # Generate JSON Web Token
    client_id = "Iv23lifHcR6yRDTxa7nk"
    issue_time = time.time()
    expiration_time = issue_time + 600

    with open(".pem", "rb") as pem:
        signing_key = jwt.jwk_from_pem(pem.read())

    payload = {
        # Issued at time
        "iat": int(issue_time),
        # Expiration time
        "exp": int(expiration_time),
        # Github App CLient ID
        "iss": client_id
    }

    jwt_instance = jwt.JWT()
    encoded_jwt = jwt_instance.encode(payload, signing_key, alg="RS256")

    # Get Installation ID

    header = {"Authorization": f"Bearer {encoded_jwt}"}

    response = requests.get(url=f"https://api.github.com/orgs/{org}/installation", headers=header)

    if response.status_code == 200:
        installation_json = response.json()
        installation_id = installation_json["id"]

        # Get Access Token
        response = requests.post(url=f"https://api.github.com/app/installations/{installation_id}/access_tokens", headers=header)
        access_token = response.json()
        return (access_token["token"], access_token["expires_at"])
    else:
        return "The pem file used does not support that organisation."
    
# token, expiration = get_access_token("ONS-Innovation")

# # header = {"Authorization": f"Bearer {token}"}
# header = {"Authorization": f"Bearer "}


# response = requests.get(url=f"https://api.github.com/orgs/ONS-Innovation/repos", headers=header, params={ "type": "internal" })
# print(response)
# import pprint

# for repo in response.json():
#     print(repo["visibility"])