"""Testes de unidade e API usados pelo pipeline."""

from app import app, calculate_shipping


def test_calculate_shipping():
    assert calculate_shipping(100.0, "5.50") == 105.50


def test_health_endpoint():
    response = app.test_client().get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_shipping_endpoint():
    response = app.test_client().post(
        "/shipping", json={"base_price": 100.0, "tax_rate": "5.50"}
    )
    assert response.status_code == 200
    assert response.get_json() == {"total": 105.50}
