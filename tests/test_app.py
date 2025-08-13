# tests/test_app.py
import os
import pytest

# IMPORTANTE: establecer DATABASE_URI antes de crear la app
# para que Flask-SQLAlchemy no intente conectar a Postgres.
os.environ["DATABASE_URI"] = "sqlite:///:memory:"

from app import create_app, db
from app.models import Data

@pytest.fixture
def app():
    # Creamos la app (ya leerá DATABASE_URI desde os.environ)
    app = create_app("development")
    app.config['TESTING'] = True

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_insert_and_get(client):
    # Insertamos
    resp = client.post("/data", json={"name": "Test User"})
    assert resp.status_code == 200 or resp.status_code == 201

    # Obtenemos lista
    resp2 = client.get("/data")
    assert resp2.status_code == 200
    data = resp2.get_json()
    assert any(d["name"] == "Test User" for d in data)

def test_unique_constraint(client):
    client.post("/data", json={"name": "Dup User"})
    resp = client.post("/data", json={"name": "Dup User"})
    assert resp.status_code == 409
