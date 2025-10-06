import pytest
from app import create_app
from app.db import db
from app.config import Config

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        with app.app_context():
            db.users.drop()  # Clear users before each test
        yield client

@pytest.fixture(autouse=True)
def setup_users():
    db.users.insert_many([
        {
            'uid': 'hirer1',
            'email': 'hirer1@example.com',
            'wallet_address': '0x73A9f11e52DDAA3717Fb79C5BF2f007e7397e1C2'
        },
        {
            'uid': 'provider1',
            'email': 'provider1@example.com',
            'wallet_address': '0xCa3edFaA083B17D49d2981143c2d6e0cFf40E7b9'
        }
    ])

def test_deliverables(client):
    response = client.post('/api/gigs', headers={'Authorization': 'Bearer provider1'}, json={
        'provider_uid': 'provider1',
        'title': 'Web Development',
        'price': 10,
        'duration_hours': 3
    })
    assert response.status_code == 200

    response = client.post('/api/escrow/fund', headers={'Authorization': 'Bearer hirer1'}, json={
        'gig_id': 'gig12',
        'provider_address': '0xCa3edFaA083B17D49d2981143c2d6e0cFf40E7b9',
        'amount_usdc': 30,
        'private_key': Config.TEST_USER_PRIVATE_KEY
    })
    assert response.status_code == 200
    assert 'tx_hash' in response.json

    response = client.post('/api/escrow/approve', headers={'Authorization': 'Bearer hirer1'}, json={
        'gig_id': 'gig12',
        'private_key': Config.PRIVATE_KEY
    })
    assert response.status_code == 200
    assert 'tx_hash' in response.json