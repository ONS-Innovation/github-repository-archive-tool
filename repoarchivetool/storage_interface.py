import json

def write_file(filename: str, content: list):
    with open(filename, "w") as f:
        f.write(json.dumps(content, indent=4))

def read_file(filename: str, sort_field: str | None = None, reverse: bool = False) -> list:
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