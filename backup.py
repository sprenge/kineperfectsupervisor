import os
import re
import json
import shutil
import zipfile
import requests


def download_media(base_path, url):
    # Extract the filename from the URL
    filename = os.path.join(base_path, url.split("/")[-1])

    # Send a GET request to the URL
    try:
        response = requests.get(url, stream=True)
    except:
        return False

    # Check if the request was successful
    if response.status_code == 200:
        # Save the content to a file in binary mode
        with open(filename, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        return filename
    else:
        print("Failed to retrieve the file. Status code:", response.status_code)
        return False


def get_backup(backup_dir, config, site, state_data):
    url = f"https://{config['fqdn']}:{config['port']}/get-csrf-token/"
    r = requests.get(url)
    csrf_token = r.json()["csrfToken"]
    headers = {
        "X-CSRFToken": csrf_token,
        "Content-Type": "application/json",  # or any other content type required
    }
    url = f"https://{config['fqdn']}:{config['port']}/backup_db/"
    r = requests.get(url, headers=headers, auth=(config["login"], config["password"]))

    if r.status_code != 200:
        return False
    db_json = r.json()

    base_dir = os.path.join(backup_dir, site)
    os.makedirs(base_dir, exist_ok=True)
    files = [
        f for f in os.listdir(base_dir) if os.path.isfile(os.path.join(base_dir, f))
    ]
    files.sort()
    seq_nbr = 1
    if len(files) > 0:
        match = re.match("db(\d+).zip", files[-1])
        if match:
            seq_nbr = int(match.group(1)) + 1
    if len(files) >= config["db_copies"]:
        os.remove(os.path.join(base_dir, files[0]))
    zip_filename = os.path.join(base_dir, f"db{seq_nbr:06}.zip")

    # Write the data to a zip file
    with zipfile.ZipFile(zip_filename, "w") as zipf:
        # Save it to a file inside the zip
        zipf.writestr("data.json", db_json)

    db_lines = json.loads(db_json)
    nbr_media_retrieved = 0
    for db_line in db_lines:
        if (
            db_line["model"] == "backend.video"
            and nbr_media_retrieved < config["limit_nbr_videos_per_backup"]
        ):
            pk = db_line["pk"]
            get_the_media = True
            if pk in state_data:
                if "size_disk" in state_data[pk]:
                    if db_line["fields"]["size_disk"] == state_data[pk]["size_disk"]:
                        print(f"no need to retrieve {pk}")
                        get_the_media = False
            if get_the_media:
                print(f"retrieve video {pk}")
                download_media(base_dir, db_line["fields"]["video_url"])
                if db_line["fields"]["snapshot"]:
                    download_media(base_dir, db_line["fields"]["snapshot"])
                if pk not in state_data:
                    state_data[pk] = {}
                nbr_media_retrieved += 1
                state_data[pk]["size_disk"] = db_line["fields"]["size_disk"]
    return True
