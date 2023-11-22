import sys
import json
import yaml
import requests
import logging
from pathlib import Path

# hack to import from top level of repo
sys.path.append(str(Path(__file__).parents[2].absolute()))

with open("config_template.yml") as f:
    config = yaml.safe_load(f)

# overwrite / extend default configuration settings
with open("config.yml") as f:
    config.update(yaml.safe_load(f))


def fetch_latest_diction(diction_json: Path | str) -> None:
    # TODO: Update this once there is a release version of the json file
    url = config["GIT_EXFOR_DICT_URL"] + \
        '/main/src/exfor_dictionary/latest.json'

    r = requests.get(url, allow_redirects=True,
                     verify=config["SSL_VERIFICATION"])

    if r.status_code == 404:
        logging.error(
            f"Could not retrieve new dictionary json from the IAEA-NDS at {url}: {r['message']}")
        sys.exit()

    open(diction_json, "wb").write(r.content)
    logging.info(f"dictionary json downloaded")


def get_available_diction_ids(diction_file: Path | str) -> list:
    with open(diction_file, 'r') as f:
        dictions = json.load(f)
        return list(dictions["definitions"].keys())


def extract_survey_list(diction_json: Path | str, diction_id: int, prefix="dictions") -> str:

    prefix = Path(prefix)
    prefix.mkdir(exist_ok=True)

    with open(diction_json) as f:
        dictions = json.load(f)

    diction = dictions["dictionaries"].get(diction_id, {"codes": {}})
    diction_name = dictions["definitions"][diction_id]["description"]
    output_filename = prefix / \
        f"diction_{diction_name.lower().replace(' ', '_')}.md"

    logging.info(f"Extracting description list of {diction_name}")

    descriptions = []

    for code_name, code_dict in diction["codes"].items():

        # Skip non active entries as these can have duplicate descriptions
        if code_dict["active"] == False:
            continue

        description = code_dict["description"]

        # sanity check
        if description in descriptions:
            logging.warning(
                f"Detected duplicate entry '{description}' in '{diction_name}' diction.")
            continue

        descriptions.append(description)

    item_prefix = "        - "
    descriptions_formatted = "\n".join([item_prefix + d for d in descriptions])

    with open(output_filename, 'w') as f:
        f.writelines(descriptions_formatted)
    logging.info(f"Extracted {diction_name} diction as list.")

    return output_filename


def extract_all_survey_lists(diction_json):
    ids = get_available_diction_ids(diction_json)
    return [extract_survey_list(diction_json, id) for id in ids]


def update():
    dict_filename = "latest_dict.json"
    fetch_latest_diction(dict_filename)
    extract_all_survey_lists(dict_filename)


if __name__ == "__main__":
    print(update())
