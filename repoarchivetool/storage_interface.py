import json

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