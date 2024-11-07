import yaml
import copy


def parse_config_file(path):
    with open(path, "r") as file:
        config_dict = yaml.safe_load(file)

    the_config = copy.deepcopy(config_dict)
    if "sites" in config_dict:
        for site in config_dict["sites"]:
            mandatory_fields = ["fqdn", "port", "login", "password"]
            for mandatory_field in mandatory_fields:
                if mandatory_field not in config_dict["sites"][site]:
                    raise Exception(f"{mandatory_field} not provided in config")

            the_config["sites"][site]["db_copies"] = config_dict["sites"][site].get(
                "db_copies", 10
            )
            the_config["sites"][site]["alive_check_every"] = config_dict["sites"][
                site
            ].get("alive_check_every", 600)
            the_config["sites"][site]["backup_every"] = config_dict["sites"][site].get(
                "backup_every", 1
            )
            the_config["sites"][site]["limit_nbr_videos_per_backup"] = config_dict[
                "sites"
            ][site].get("limit_nbr_videos_per_backup", 5)
    else:
        config_dict["sites"] = {}

    return the_config
