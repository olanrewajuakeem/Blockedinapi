from flask import current_app
from flask_restx import Namespace, Resource, fields
from web3 import Web3
from app.models import Escrow, Fee, GigInstance, Dispute, User
from app.db import db
from datetime import datetime

escrow_ns = Namespace('escrow', description='Escrow operations')

fund_model = escrow_ns.model('FundEscrow', {
    'gig_id': fields.String(required=True),
    'provider_address': fields.String(required=True),
    'amount_usdc': fields.Float(required=True),
    'signed_tx': fields.String(required=True)
})

approve_model = escrow_ns.model('ApproveGig', {
    'gig_id': fields.String(required=True),
    'signed_tx': fields.String(required=True)
})

refund_model = escrow_ns.model('RefundEscrow', {
    'gig_id': fields.String(required=True),
    'signed_tx': fields.String(required=True)
})

@escrow_ns.route('/fund')
class FundEscrow(Resource):
    @escrow_ns.expect(fund_model)
    def post(self):
        data = escrow_ns.payload
        gig_id = data.get('gig_id')
        provider_address = data.get('provider_address')
        amount = data.get('amount_usdc')
        signed_tx = data.get('signed_tx')

        if not all([gig_id, provider_address, amount, signed_tx]):
            return {"error": "Missing required fields"}, 400

        w3 = Web3(Web3.HTTPProvider(current_app.config['BASE_RPC_URL']))
        if not w3.is_address(provider_address):
            return {"error": "Invalid provider address"}, 400
        user = User.query.filter_by(wallet_address=provider_address).first()
        if not user or not user.is_provider:
            return {"error": "Provider address must belong to a provider"}, 400

        try:
            tx_hash = w3.eth.send_raw_transaction(signed_tx)
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
            if receipt.status != 1:
                return {"error": "Transaction failed"}, 400
        except Exception as e:
            return {"error": f"Transaction failed: {str(e)}"}, 400

        try:
            escrow = Escrow(
                gig_id=gig_id,
                provider_address=provider_address,
                amount=amount,
                tx_hash=tx_hash.hex()
            )
            fee = Fee.create_fee(gig_id=gig_id, amount=amount * 0.1)
            instance = GigInstance.create_gig_instance(
                gig_id=gig_id,
                hirer_wallet=provider_address,
                escrow_address=current_app.config['ESCROW_CONTRACT_ADDRESS']
            )
            db.session.add(escrow)
            db.session.commit()
            return {
                "tx_hash": tx_hash.hex(),
                "fee_id": fee['id'],
                "instance_id": instance['id']
            }, 200
        except Exception as e:
            db.session.rollback()
            return {"error": f"Database error: {str(e)}"}, 400

@escrow_ns.route('/approve')
class ApproveGig(Resource):
    @escrow_ns.expect(approve_model)
    def post(self):
        data = escrow_ns.payload
        gig_id = data.get('gig_id')
        signed_tx = data.get('signed_tx')

        if not all([gig_id, signed_tx]):
            return {"error": "Missing required fields"}, 400

        w3 = Web3(Web3.HTTPProvider(current_app.config['BASE_RPC_URL']))
        try:
            tx_hash = w3.eth.send_raw_transaction(signed_tx)
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
            if receipt.status != 1:
                return {"error": "Transaction failed"}, 400
        except Exception as e:
            return {"error": f"Transaction failed: {str(e)}"}, 400

        try:
            escrow = Escrow.query.filter_by(gig_id=gig_id).first()
            if not escrow:
                return {"error": "Escrow not found"}, 404
            escrow.status = 'approved'
            escrow.tx_hash = tx_hash.hex()
            db.session.commit()
            return {"tx_hash": tx_hash.hex()}, 200
        except Exception as e:
            return {"error": f"Database error: {str(e)}"}, 400

@escrow_ns.route('/refund')
class RefundEscrow(Resource):
    @escrow_ns.expect(refund_model)
    def post(self):
        data = escrow_ns.payload
        gig_id = data.get('gig_id')
        signed_tx = data.get('signed_tx')

        if not all([gig_id, signed_tx]):
            return {"error": "Missing required fields"}, 400

        dispute = Dispute.query.filter_by(gig_id=gig_id).first()
        if not dispute or dispute.status != 'resolved' or dispute.outcome != 'hirer':
            return {"error": "No resolved dispute favoring hirer found"}, 400

        hirer = User.query.filter_by(uid=dispute.initiator_uid).first()
        if not hirer:
            return {"error": "Hirer not found"}, 404

        w3 = Web3(Web3.HTTPProvider(current_app.config['BASE_RPC_URL']))
        try:
            tx_hash = w3.eth.send_raw_transaction(signed_tx)
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
            if receipt.status != 1:
                return {"error": "Transaction failed"}, 400
        except Exception as e:
            return {"error": f"Transaction failed: {str(e)}"}, 400

        try:
            escrow = Escrow.query.filter_by(gig_id=gig_id).first()
            if not escrow:
                return {"error": "Escrow not found"}, 404
            escrow.status = 'refunded'
            escrow.tx_hash = tx_hash.hex()
            db.session.commit()
            return {"tx_hash": tx_hash.hex()}, 200
        except Exception as e:
            return {"error": f"Database error: {str(e)}"}, 400