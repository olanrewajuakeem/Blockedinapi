import requests
from app.config import Config

def upload_to_pinata(file, gig_id):
    headers = {
        'pinata_api_key': Config.PINATA_API_KEY,
        'pinata_api_secret': Config.PINATA_API_SECRET
    }
    files = {'file': (f'gig-{gig_id}-{file.filename}', file)}
    response = requests.post('https://api.pinata.cloud/pinning/pinFileToIPFS', headers=headers, files=files)
    response.raise_for_status()
    return f"ipfs://{response.json()['IpfsHash']}"