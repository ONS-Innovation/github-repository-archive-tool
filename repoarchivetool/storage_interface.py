import json
import boto3
from botocore.exceptions import ClientError

def get_bucket_content(filename: str) -> bool | ClientError:
    """
        Downloads a given file from an S3 Bucket

        ==========

        Args:
            filename (str): The name of the file to download

        Returns:
            Bool or ClientError
    """

    # session = boto3.Session(profile_name="<profile_name>")
    session = boto3.Session()
    s3 = session.client("s3")

    try:
        s3.download_file("github-audit-tool", f"repo-archive/{filename}", filename)
    except ClientError as e:
        return e
    return True

def update_bucket_content(filename: str) -> bool | ClientError:
    """
        Uploads a given file to an S3 Bucket

        ==========

        Args:
            filename (str): The name of the file to upload

        Returns:
            Bool or ClientError
    """

    # session = boto3.Session(profile_name="<profile_name>")
    session = boto3.Session()
    s3 = session.client("s3")

    try:
        response = s3.upload_file(filename, "github-audit-tool", f"repo-archive/{filename}")
    except ClientError as e:
        return e
    return True

def write_file(filename: str, content: list):
    """
        Writes to a given file in JSON

        ==========

        Args:
            filename (str): the name of the file to write to
            content (list): the data to be written as a list of dictionaries to mimic JSON

        returns:
            None
    """
    with open(filename, "w") as f:
        f.write(json.dumps(content, indent=4))

    update_bucket_content(filename)

def read_file(filename: str, sort_field: str | None = None, reverse: bool = False) -> list:
    """
        Reads a given file

        ==========

        Args:
            filename (str): the name of the file to be read
            sort_field (str): the field the output should be sorted on. If None is passed, it will not be sorted.
            reverse (bool): whether the output should be reversed or not.

        Returns:
            list
    """
    try:
        with open(filename, "r") as f:
            contents = json.load(f)

            if sort_field != None:
                contents.sort(key=lambda x: x[sort_field])

            if reverse:
                contents.reverse()

    except FileNotFoundError:
        contents = []

    return contents