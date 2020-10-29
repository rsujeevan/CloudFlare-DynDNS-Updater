import logging
import requests


IPIFY_URL = "https://api.ipify.org?format=text"


def external_ip() -> str:
    logging.debug(f"Finding the external ip. URL={IPIFY_URL}")
    response = requests.get(url=IPIFY_URL)
    response.raise_for_status()
    ip = response.text.strip()
    logging.info(f"External IP is {ip}")
    return ip
