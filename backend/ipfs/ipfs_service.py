import requests
import os
from dotenv import load_dotenv

load_dotenv()

PINATA_API_KEY = os.getenv("PINATA_API_KEY")
PINATA_SECRET_API_KEY = os.getenv("PINATA_SECRET_API_KEY")

PINATA_URL = "https://api.pinata.cloud/pinning/pinJSONToIPFS"


def upload_json_to_ipfs(data: dict):
    headers = {
        "pinata_api_key": PINATA_API_KEY,
        "pinata_secret_api_key": PINATA_SECRET_API_KEY,
        "Content-Type": "application/json",
    }

    response = requests.post(PINATA_URL, json=data, headers=headers)

    if response.status_code != 200:
        raise Exception("IPFS upload failed: " + response.text)

    ipfs_hash = response.json()["IpfsHash"]

    return ipfs_hash
