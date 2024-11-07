import argparse
import os
import time
import shelve
from parse_config import parse_config_file
from alive_check import execute_alive_check
from backup import get_backup
from send_email import send_email

backup_dir = "./backup"
state_data = {}
initial_state_data = {}
state_file = "./state.db"

if __name__ == "__main__":
    VERSION = "1.0.0"
    # print("kineperfect supervisor : {}".format(VERSION))
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--backup_dir",
        default="./backup",
        nargs="?",
        help="name of the resulting zip file (default=none)",
    )
    args = parser.parse_args()
    backup_dir = args.backup_dir
    state_file = os.path.join(backup_dir, "state.db")
    config_file = os.path.join(backup_dir, "config.yaml")
    try:
        with shelve.open(state_file) as db:
            state_data = db["state"]
    except:
        print("no state data yet, that is fine")

    config = parse_config_file(config_file)
    current_epoch_time = int(time.time())

    for site in config["sites"]:
        site_context = config["sites"][site]
        if site not in state_data:
            state_data[site] = {}
            state_data[site]["last_alive_check_timestamp"] = 0
            state_data[site]["last_backup_timestamp"] = 0

        if (
            current_epoch_time
            >= state_data[site]["last_backup_timestamp"] + site_context["backup_every"]
        ):
            print("backup required")
            ok = get_backup(backup_dir, config["sites"][site], site, state_data[site])
            if not ok:
                send_email(
                    "backup failed",
                    f"backup failed {site}",
                    config,
                    config["sites"][site]["email"],
                )
            state_data[site]["last_backup_timestamp"] = current_epoch_time
        if (
            current_epoch_time
            >= state_data[site]["last_alive_check_timestamp"]
            + site_context["alive_check_every"]
        ):
            print("alive check required")
            ok = execute_alive_check(config["sites"][site])
            if not ok:
                print("alive check failed")
                send_email(
                    "alive check failed",
                    f"alive check failed {site}",
                    config,
                    config["sites"][site]["email"],
                )
            state_data[site]["last_alive_check_timestamp"] = current_epoch_time
    with shelve.open(state_file) as db:
        db["state"] = state_data
