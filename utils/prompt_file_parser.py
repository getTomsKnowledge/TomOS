# tomos/utils/prompt_file_parser.py
from __future__ import annotations
from typing import Dict, Iterable
import os
import json

# Dictionary mapping modes to their respective template folder paths:
pathDict = {"career": 'G:\\My Drive\\Desktop\\Studies\\Engineering\\AI\\TomOS\\prompts\\career\\',
"growth": 'G:\\My Drive\\Desktop\\Studies\\Engineering\\AI\\TomOS\\prompts\\growth\\',
"play": 'G:\\My Drive\\Desktop\\Studies\\Engineering\\AI\\TomOS\\prompts\\play\\',
# FIX ME!!!  Make into a relative path
"defaultPath": 'G:\\My Drive\\Desktop\\Studies\\Engineering\\AI\\TomOS\\prompts\\default\\helloworld.txt',
"defaultSchema": 'G:\\My Drive\\Desktop\\Studies\\Engineering\\AI\\TomOS\\schemas\\default_schema.txt'
}

def select_and_load_json_schema(selected_mode: str) -> dict:
    """
    Discover JSON schema files for a given role, prompt user to select one, and load it.
    Returns the loaded schema as a Python dict.
    """

    if (selected_mode == "career"):
        folder_path = pathDict["career"]
    elif (selected_mode == "growth"):
        folder_path = pathDict["growth"]
    elif (selected_mode == "play"):
        folder_path = pathDict["play"]
    else:
        folder_path = pathDict["defaultPath"]

    # Discover .json files in the schema folder
    json_files = [f for f in os.listdir(folder_path) if f.endswith('.json')]
    if not json_files:
        print(f"No JSON schema files found in {folder_path}")
        return None

    print(f"Available schemas for {selected_mode}:")
    for idx, fname in enumerate(json_files):
        print(f"{idx + 1}: {fname}")

    # Prompt user to select a file
    selection = input("Enter the number of the schema to use: ")
    try:
        selected_file = json_files[int(selection) - 1]
    except (ValueError, IndexError):
        print("Invalid selection.")
        return None

    # Read and return the JSON schema
    schema_path = os.path.join(folder_path, selected_file)
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)
    return schema

# Example usage:
# schema = select_and_load_json_schema("career", "G:\\My Drive\\Desktop\\Studies\\Engineering\\AI\\TomOS\\prompts\\career")
# Pass schema to OpenAI client: client.responses.create(..., response_format={"type": "json_object", "schema": schema})

# Utility functions to read prompt files and extract variables and prompts.
def get_filenames_from_folder(selected_mode):
    """
    Reads all file names from a specified folder and returns them in a list.

    Args:
        folder_path (str): The path to the folder.

    Returns:
        list: A list containing the names of all files in the specified folder.
              Returns an empty list if the folder does not exist or is empty.
    """
    if (selected_mode == "career"):
        folder_path = pathDict["career"]
    elif (selected_mode == "growth"):
        folder_path = pathDict["growth"]
    elif (selected_mode == "play"):
        folder_path = pathDict["play"]
    else:
        folder_path = pathDict["defaultPath"]

    filenames = []
    if os.path.exists(folder_path) and os.path.isdir(folder_path):
        for item in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item)
            if os.path.isfile(item_path):
                filenames.append(item)

    return filenames

# Set the template file path in the TomOS object:
def set_template_file(thisOS, templateName):
    absPath = ""
    if (thisOS.mode not in pathDict):
        absPath = pathDict["defaultPath"]
    else:
        absPath = pathDict[thisOS.mode]
    fullPath = absPath + templateName
    thisOS.templateFilepath = fullPath    
    return

# Read key:value pairs from template file between start_tag and stop_tag (exclusive):
def read_kv_block(
    thisOS,
    start_tag: str = "_start_reading_context_variables",
    stop_tag: str = "_stop_reading_context_variables",
    *,
    comment_prefixes: Iterable[str] = ("#", "//", ";"),
    strip_quotes: bool = True,
    on_duplicate: str = "error",    # "error" | "first_wins" | "last_wins"
    allow_empty_values: bool = True
) -> Dict[str, str]:
    """
    Read key:value pairs from `path` between lines containing `start_tag` and `stop_tag` (exclusive).

    Rules:
      - Lines are 'key: value' (split on the FIRST colon).
      - Leading/trailing whitespace is ignored.
      - Blank lines are ignored.
      - Lines starting with a comment prefix are ignored.
      - If strip_quotes is True, surrounding single/double quotes on values are removed.
      - Duplicate keys policy via `on_duplicate`: 'error' | 'first_wins' | 'last_wins'.
      - If allow_empty_values is True, 'key:' (no value) yields empty string.

    Raises:
      - FileNotFoundError if `path` is missing.
      - ValueError for missing markers, malformed lines, or duplicate keys (per policy).
    """
    if (thisOS.templateFilepath == -1):
        thisOS.templateFilepath = pathDict["defaultPath"]

    with open(thisOS.templateFilepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # locate markers
    start_idx = next((i for i, ln in enumerate(lines) if start_tag in ln), None)
    if start_idx is None:
        raise ValueError(f"Start marker '{start_tag}' not found in {thisOS.templateFilepath}")
    stop_idx = next((i for i, ln in enumerate(lines[start_idx + 1 :], start_idx + 1) if stop_tag in ln), None)
    if stop_idx is None:
        raise ValueError(f"Stop marker '{stop_tag}' not found in {thisOS.templateFilepath}")
    if stop_idx <= start_idx:
        raise ValueError(f"Stop marker appears before start marker in {thisOS.templateFilepath}")

    result: Dict[str, str] = {}
    block = lines[start_idx + 1 : stop_idx]

    for lineno, raw in enumerate(block, start=start_idx + 2):
        line = raw.strip()
        if not line:
            continue
        if any(line.startswith(pfx) for pfx in comment_prefixes):
            continue

        colon = line.find(":")
        if colon == -1:
            raise ValueError(
                f"{thisOS.templateFilepath}:{lineno}: Expected 'key: value' (found no ':') -> {raw.rstrip()}"
            )

        key = line[:colon].strip()
        val = line[colon + 1 :].strip()

        if not key:
            raise ValueError(f"{thisOS.templateFilepath}:{lineno}: Empty key is not allowed.")

        if not val and not allow_empty_values:
            raise ValueError(f"{thisOS.templateFilepath}:{lineno}: Missing value for key '{key}'.")

        # optional quote stripping
        if strip_quotes and len(val) >= 2:
            if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                val = val[1:-1]

        if key in result:
            if on_duplicate == "error":
                raise ValueError(f"{thisOS.templateFilepath}:{lineno}: Duplicate key '{key}'.")
            elif on_duplicate == "first_wins":
                continue  # keep the original
            elif on_duplicate == "last_wins":
                pass      # overwrite below
            else:
                raise ValueError(f"Invalid on_duplicate policy: {on_duplicate}")

        result[key] = val

    return result

# Read prompt string from template file between start_tag and stop_tag (exclusive):
def read_prompt(
    thisOS,
    start_tag: str = "_prompt_start",
    stop_tag: str = "_prompt_stop",
    *,
    comment_prefixes: Iterable[str] = ("#", "//", ";"),
    allow_empty_values: bool = True
) -> str:
    """
    Read prompt string from text file marked with internal `start_tag` and `stop_tag` (exclusive).

    Rules:
      - Lines starting with a comment prefix are ignored.
      - If strip_quotes is True, surrounding single/double quotes on values are removed.
      - If allow_empty_values is True, 'key:' (no value) yields empty string.

    Raises:
      - FileNotFoundError if `path` is missing.
      - ValueError for missing markers, malformed lines.
    """

    if (thisOS.templateFilepath == -1):
        thisOS.templateFilepath = pathDict["defaultPath"]

    with open(thisOS.templateFilepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # locate markers
    start_idx = next((i for i, ln in enumerate(lines) if start_tag in ln), None)
    if start_idx is None:
        raise ValueError(f"Start marker '{start_tag}' not found in {thisOS.templateFilepath}")
    stop_idx = next((i for i, ln in enumerate(lines[start_idx + 1 :], start_idx + 1) if stop_tag in ln), None)
    if stop_idx is None:
        raise ValueError(f"Stop marker '{stop_tag}' not found in {thisOS.templateFilepath}")
    if stop_idx <= start_idx:
        raise ValueError(f"Stop marker appears before start marker in {thisOS.templateFilepath}")

    result: str = ""
    block = lines[start_idx + 1 : stop_idx]

    for lineno, raw in enumerate(block, start=start_idx + 2):
        line = raw.strip()
        if not line:
            continue
        if any(line.startswith(pfx) for pfx in comment_prefixes):
            continue
        result = result + '\n' + line

    return result