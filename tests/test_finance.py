"""Happy-path functional tests — these describe how the API should behave.

They pass today. Use them as the safety net while you fix the security bugs:
your fixes must not break these.
"""
from conftest import register, token, auth


def test_register_and_login(client):
    r = register(client, "alice", "pw")
    assert r.status_code == 200
    tok = token(client, "alice", "pw")
    assert tok


def test_create_and_read_own_account(client):
    register(client, "alice", "pw")
    tok = token(client, "alice", "pw")
    r = client.post("/accounts", json={"name": "Checking", "balance": 100.0}, headers=auth(tok))
    assert r.status_code == 200
    acc_id = r.json()["id"]

    r = client.get(f"/accounts/{acc_id}", headers=auth(tok))
    assert r.status_code == 200
    assert r.json()["balance"] == 100.0


def test_transfer_moves_money(client):
    register(client, "alice", "pw")
    tok = token(client, "alice", "pw")
    a = client.post("/accounts", json={"name": "A", "balance": 100.0}, headers=auth(tok)).json()
    b = client.post("/accounts", json={"name": "B", "balance": 0.0}, headers=auth(tok)).json()

    r = client.post("/transfer", json={
        "from_account_id": a["id"], "to_account_id": b["id"], "amount": 40.0,
    }, headers=auth(tok))
    assert r.status_code == 200

    assert client.get(f"/accounts/{a['id']}", headers=auth(tok)).json()["balance"] == 60.0
    assert client.get(f"/accounts/{b['id']}", headers=auth(tok)).json()["balance"] == 40.0


def test_protected_route_requires_token(client):
    r = client.post("/accounts", json={"name": "X", "balance": 0.0})
    assert r.status_code == 401
