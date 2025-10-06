from flask import Flask, request, abort
from flask_restx import Api
from app.config import Config
from app.db import db, init_db
from flask_migrate import Migrate
from app.models import User, Gig, Escrow, Fee, Dispute, Review, GigInstance
import jwt
import requests
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    # logger.debug(f"Config.BASE_RPC_URL before loading: {Config.BASE_RPC_URL}")
    app.config.from_object(Config)
    # logger.debug(f"app.config['BASE_RPC_URL'] after loading: {app.config.get('BASE_RPC_URL')}")
    # logger.debug(f"Config.BASE_RPC_URL after loading: {Config.BASE_RPC_URL}")

    init_db(app)
    migrate = Migrate(app, db)

    with app.app_context():
        db.create_all()

    api = Api(
        app,
        version='1.0',
        title='BlockedIN API',
        description='API for BlockedIN decentralized gig marketplace (Base Sepolia Testnet)',
        prefix='/api'
    )

    from app.routes.escrow import escrow_ns
    from app.routes.users import users_ns
    from app.routes.gigs import gigs_ns
    from app.routes.reviews import reviews_ns
    from app.routes.disputes import disputes_ns
    from app.routes.deliverables import deliverables_ns

    api.add_namespace(escrow_ns, path='/escrow')
    api.add_namespace(users_ns, path='/users')
    api.add_namespace(gigs_ns, path='/gigs')
    api.add_namespace(reviews_ns, path='/reviews')
    api.add_namespace(disputes_ns, path='/disputes')
    api.add_namespace(deliverables_ns, path='/deliverables')


    return app