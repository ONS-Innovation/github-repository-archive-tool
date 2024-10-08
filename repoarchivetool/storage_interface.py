import json
import os

import boto3
from botocore.exceptions import ClientError


def get_s3_client():
    """Returns an S3 Client.

    ==========

    Returns:
        S3 Client
    """
    session = boto3.Session()
    s3 = session.client("s3")

    return s3


def has_file_changed(bucket: str, key: str, filename: str) -> bool:
    """Checks if a file in an S3 Bucket has changed.

    ==========

    Args:
        bucket (str): The name of the bucket
        key (str): The key of the file
        filename (str): The name of the file to compare

    Returns:
        bool
    """
    s3 = get_s3_client()

    try:
        obj = s3.get_object(Bucket=bucket, Key=key)
    except ClientError as e:  # noqa F841
        # ClientError is raised when the key does not exist in the bucket
        # Therefore we need to return True to indicate that the file should be created
        return True
    else:
        s3_last_modified = int(obj["LastModified"].strftime("%s")) // 10
        s3_content_length = obj["ContentLength"]

        try:
            local_last_modified = os.path.getmtime(filename) // 10
            local_content_length = os.path.getsize(filename)
        except FileNotFoundError:
            # FileNotFoundError is raised when the file does not exist locally
            # Therefore, return True to indicate that the file should be created
            return True

        return s3_last_modified != local_last_modified or s3_content_length != local_content_length


def get_bucket_content(bucket: str, filename: str) -> bool | ClientError:
    """Downloads a given file from an S3 Bucket.

    ==========

    Args:
        filename (str): The name of the file to download
        bucket (str): The name of the bucket

    Returns:
        Bool or ClientError
    """
    s3 = get_s3_client()

    try:
        s3.download_file(bucket, f"repo-archive/{filename}", filename)
    except ClientError as e:
        return e
    return True


def update_bucket_content(bucket: str, filename: str, local_filename: str = "") -> bool | ClientError:
    """Uploads a given file to an S3 Bucket.

    ==========

    Args:
        filename (str): The name of the file to upload
        bucket (str): The name of the bucket
        local_filename (str): The name of the file to upload. If not provided, it will use and empty string

    Returns:
        Bool or ClientError
    """
    if local_filename == "":
        local_filename = filename

    s3 = get_s3_client()

    try:
        response = s3.upload_file(local_filename, bucket, f"repo-archive/{filename}")  # noqa F841
    except ClientError as e:
        return e
    return True


def write_file(bucket: str, filename: str, content: list):
    """Writes to a given file in JSON.

    ==========

    Args:
        filename (str): the name of the file to write to
        content (list): the data to be written as a list of dictionaries to mimic JSON
        bucket (str): the name of the bucket to upload the file to

    returns:
        None
    """
    with open(filename, "w") as f:
        f.write(json.dumps(content, indent=4))

    update_bucket_content(bucket, filename)


def read_file(filename: str, sort_field: str | None = None, reverse: bool = False) -> list:
    """Reads a given file.

    ==========

    Args:
        filename (str): the name of the file to be read
        sort_field (str): the field the output should be sorted on. If None is passed, it will not be sorted.
        reverse (bool): whether the output should be reversed or not.

    Returns:
        list
    """
    try:
        with open(filename) as f:
            contents = json.load(f)

            if sort_field != None:  # noqa E711
                contents.sort(key=lambda x: x[sort_field])

            if reverse:
                contents.reverse()

    except FileNotFoundError:
        contents = []

    return contents
