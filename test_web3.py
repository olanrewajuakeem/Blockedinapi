from web3 import Web3
import os

BASE_RPC_URL = 'https://base-sepolia.g.alchemy.com/v2/DUE-KloSh-vpMsfffjSm3'
w3 = Web3(Web3.HTTPProvider(BASE_RPC_URL))
print(f"Connected: {w3.is_connected()}")
if w3.is_connected():
    print(f"Block number: {w3.eth.block_number}")
else:
    print("Connection failed")
