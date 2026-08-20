import pytest
from conftest import register, token, auth


@pytest.mark.xfail(reason="registration trusts is_admin from the request body", strict=True)
def test_cannot_self_register_as_admin(client):
    r = register(client, "mallory", "pw", is_admin=True)
    assert r.status_code == 200
    assert r.json()["is_admin"] is False


@pytest.mark.xfail(reason="password_hash is serialized in the user response", strict=True)
def test_password_hash_not_exposed(client):
    r = register(client, "alice", "pw")
    assert "password_hash" not in r.json()


@pytest.mark.xfail(reason="account read has no ownership check", strict=True)
def test_cannot_read_other_users_account(client):
    register(client, "alice", "pw")
    register(client, "bob", "pw")
    alice_tok = token(client, "alice", "pw")
    bob_tok = token(client, "bob", "pw")

    bob_acc = client.post("/accounts", json={"name": "Bob", "balance": 999.0},
                          headers=auth(bob_tok)).json()

    r = client.get(f"/accounts/{bob_acc['id']}", headers=auth(alice_tok))
    assert r.status_code in (403, 404)


@pytest.mark.xfail(reason="transfer does not verify the source account owner", strict=True)
def test_cannot_transfer_from_others_account(client):
    register(client, "alice", "pw")
    register(client, "bob", "pw")
    alice_tok = token(client, "alice", "pw")
    bob_tok = token(client, "bob", "pw")

    bob_acc = client.post("/accounts", json={"name": "Bob", "balance": 500.0},
                          headers=auth(bob_tok)).json()
    alice_acc = client.post("/accounts", json={"name": "Alice", "balance": 0.0},
                            headers=auth(alice_tok)).json()

    r = client.post("/transfer", json={
        "from_account_id": bob_acc["id"], "to_account_id": alice_acc["id"], "amount": 500.0,
    }, headers=auth(alice_tok))
    assert r.status_code in (403, 404)


@pytest.mark.xfail(reason="transfer accepts negative amounts and overdrafts", strict=True)
def test_transfer_rejects_negative_and_overdraft(client):
    register(client, "alice", "pw")
    tok = token(client, "alice", "pw")
    a = client.post("/accounts", json={"name": "A", "balance": 100.0}, headers=auth(tok)).json()
    b = client.post("/accounts", json={"name": "B", "balance": 0.0}, headers=auth(tok)).json()

    assert client.post("/transfer", json={
        "from_account_id": a["id"], "to_account_id": b["id"], "amount": -50.0,
    }, headers=auth(tok)).status_code == 400

    assert client.post("/transfer", json={
        "from_account_id": a["id"], "to_account_id": b["id"], "amount": 1000.0,
    }, headers=auth(tok)).status_code == 400


@pytest.mark.xfail(reason="search input is interpolated into raw SQL", strict=True)
def test_search_is_not_sql_injectable(client):
    register(client, "alice", "pw")
    tok = token(client, "alice", "pw")
    a = client.post("/accounts", json={"name": "A", "balance": 100.0}, headers=auth(tok)).json()
    b = client.post("/accounts", json={"name": "B", "balance": 0.0}, headers=auth(tok)).json()
    client.post("/transfer", json={
        "from_account_id": a["id"], "to_account_id": b["id"], "amount": 10.0,
    }, headers=auth(tok))

    r = client.get("/transactions/search", params={"q": "' OR '1'='1"}, headers=auth(tok))
    assert r.status_code == 200
    assert r.json() == []


@pytest.mark.xfail(reason="admin listing has no authentication or role check", strict=True)
def test_admin_endpoint_requires_admin(client):
    r = client.get("/admin/users")
    assert r.status_code == 401

    register(client, "alice", "pw")
    alice_tok = token(client, "alice", "pw")
    r = client.get("/admin/users", headers=auth(alice_tok))
    assert r.status_code == 403


@pytest.mark.xfail(reason="balances are floats and drift off the cent", strict=True)
def test_money_has_no_float_drift(client):
    register(client, "alice", "pw")
    tok = token(client, "alice", "pw")
    a = client.post("/accounts", json={"name": "A", "balance": 0.0}, headers=auth(tok)).json()
    b = client.post("/accounts", json={"name": "B", "balance": 0.0}, headers=auth(tok)).json()

    client.post("/transfer", json={"from_account_id": b["id"], "to_account_id": a["id"], "amount": 1.0}, headers=auth(tok))
    for _ in range(3):
        client.post("/transfer", json={"from_account_id": a["id"], "to_account_id": b["id"], "amount": 0.1}, headers=auth(tok))

    bal = client.get(f"/accounts/{b['id']}", headers=auth(tok)).json()["balance"]
    assert repr(bal) == "-0.7"
