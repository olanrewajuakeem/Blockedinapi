from web3 import Web3
from app.config import Config
from app.db import db
import json
import os
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug(f"Config.BASE_RPC_URL at module level: {Config.BASE_RPC_URL}")
if not Config.BASE_RPC_URL:
    logger.error("BASE_RPC_URL is None")
    raise Exception("BASE_RPC_URL is not set")

try:
    w3 = Web3(Web3.HTTPProvider(Config.BASE_RPC_URL))
    logger.debug(f"Attempting to connect to {Config.BASE_RPC_URL}")
    if not w3.is_connected():
        logger.error("Failed to connect to Base Sepolia")
        raise Exception("Failed to connect to Base Sepolia")
    logger.debug(f"Connected to Base Sepolia, block number: {w3.eth.block_number}")
except Exception as e:
    logger.error(f"Connection error: {str(e)}")
    raise

with open(os.path.join(os.path.dirname(__file__), '../../artifacts/@openzeppelin/contracts/token/ERC20/ERC20.sol/ERC20.json')) as f:
    usdc_data = json.load(f)
usdc_abi = usdc_data['abi']
usdc_address = "0x036CbD53842c5426634e7929541eC2318f3dCF7e"
usdc = w3.eth.contract(address=usdc_address, abi=usdc_abi)

with open(os.path.join(os.path.dirname(__file__), '../../artifacts/contracts/Escrow.sol/Escrow.json')) as f:
    contract_data = json.load(f)
contract_abi = contract_data['abi']
contract_address = Config.ESCROW_CONTRACT_ADDRESS
contract = w3.eth.contract(address=contract_address, abi=contract_abi)

def fund_escrow(gig_id, provider_address, amount, sender_private_key):
    logger.debug(f"Funding escrow for gig_id: {gig_id}, provider: {provider_address}, amount: {amount}")
    if not sender_private_key.startswith('0x'):
        sender_private_key = '0x' + sender_private_key
    try:
        account = w3.eth.account.from_key(sender_private_key)
        logger.debug(f"Account address: {account.address}")
    except Exception as e:
        logger.error(f"Invalid private key: {str(e)}")
        raise Exception("Invalid private key")
    balance = usdc.functions.balanceOf(account.address).call()
    logger.debug(f"Account USDC balance: {balance}")
    if balance < int(amount * 10**6):
        raise Exception(f"Insufficient USDC balance: {balance} < {int(amount * 10**6)}")
    try:
        nonce = w3.eth.get_transaction_count(account.address)
        gas_price = w3.eth.gas_price
        logger.debug(f"Current gas price: {gas_price}")
        approve_tx = usdc.functions.approve(contract_address, int(amount * 10**6)).build_transaction({
            'from': account.address,
            'gas': 60000,
            'gasPrice': gas_price,
            'nonce': nonce,
            'chainId': 84532
        })
        logger.debug(f"Approve transaction: {approve_tx}")
        signed_approve_tx = w3.eth.account.sign_transaction(approve_tx, sender_private_key)
        approve_tx_hash = w3.eth.send_raw_transaction(signed_approve_tx.raw_transaction)
        w3.eth.wait_for_transaction_receipt(approve_tx_hash)
        logger.debug(f"Approve tx_hash: {approve_tx_hash.hex()}")
        tx = contract.functions.fundEscrow(gig_id, provider_address, int(amount * 10**6)).build_transaction({
            'from': account.address,
            'gas': 150000,
            'gasPrice': gas_price,
            'nonce': nonce + 1,
            'chainId': 84532
        })
        logger.debug(f"FundEscrow transaction: {tx}")
        signed_tx = w3.eth.account.sign_transaction(tx, sender_private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        logger.debug(f"Escrow funded, tx_hash: {tx_hash.hex()}, status: {receipt['status']}")
        if receipt['status'] == 0:
            raise Exception("Transaction failed")
        return tx_hash.hex()
    except Exception as e:
        logger.error(f"Transaction error: {str(e)}")
        raise Exception(f"Transaction error: {str(e)}")

def approve_gig(gig_id, sender_private_key):
    logger.debug(f"Approving gig: {gig_id}")
    if not sender_private_key.startswith('0x'):
        sender_private_key = '0x' + sender_private_key
    try:
        account = w3.eth.account.from_key(sender_private_key)
        logger.debug(f"Account address: {account.address}")
    except Exception as e:
        logger.error(f"Invalid private key: {str(e)}")
        raise Exception("Invalid private key")
    try:
        gas_price = w3.eth.gas_price
        logger.debug(f"Current gas price: {gas_price}")
        tx = contract.functions.approveGig(gig_id).build_transaction({
            'from': account.address,
            'gas': 80000,
            'gasPrice': gas_price,
            'nonce': w3.eth.get_transaction_count(account.address),
            'chainId': 84532
        })
        logger.debug(f"ApproveGig transaction: {tx}")
        signed_tx = w3.eth.account.sign_transaction(tx, sender_private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        logger.debug(f"Gig approved, tx_hash: {tx_hash.hex()}, status: {receipt['status']}")
        if receipt['status'] == 0:
            raise Exception("Transaction failed")
        return tx_hash.hex()
    except Exception as e:
        logger.error(f"Transaction error: {str(e)}")
        raise Exception(f"Transaction error: {str(e)}")

def refund_escrow(gig_id, sender_private_key, hirer_address):
    logger.debug(f"Refunding escrow for gig_id: {gig_id}, hirer: {hirer_address}")
    if not sender_private_key.startswith('0x'):
        sender_private_key = '0x' + sender_private_key
    try:
        account = w3.eth.account.from_key(sender_private_key)
        logger.debug(f"Account address: {account.address}")
    except Exception as e:
        logger.error(f"Invalid private key: {str(e)}")
        raise Exception("Invalid private key")
    try:
        gas_price = w3.eth.gas_price
        logger.debug(f"Current gas price: {gas_price}")
        tx = contract.functions.refundFunds(gig_id, hirer_address).build_transaction({
            'from': account.address,
            'gas': 80000,
            'gasPrice': gas_price,
            'nonce': w3.eth.get_transaction_count(account.address),
            'chainId': 84532
        })
        logger.debug(f"RefundFunds transaction: {tx}")
        signed_tx = w3.eth.account.sign_transaction(tx, sender_private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        logger.debug(f"Escrow refunded, tx_hash: {tx_hash.hex()}, status: {receipt['status']}")
        if receipt['status'] == 0:
            raise Exception("Transaction failed")
        return tx_hash.hex()
    except Exception as e:
        logger.error(f"Transaction error: {str(e)}")
        raise Exception(f"Transaction error: {str(e)}")