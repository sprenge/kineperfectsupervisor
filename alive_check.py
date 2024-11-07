import requests


def execute_alive_check(config):
    url = f"https://{config['fqdn']}:{config['port']}/exercises_summary"
    try:
        r = requests.get(url, auth=(config["login"], config["password"]))
    except Exception as e:
        print(f"execute_alive_check failed {url} {e}")
    if r.status_code != 200:
        print(f"execute_alive_check failed {url} {r.status_code} {r.content}")
        return False
    return True
