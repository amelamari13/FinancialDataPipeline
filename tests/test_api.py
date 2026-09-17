import pytest

from api import app as api_app


@pytest.fixture
def client():
    api_app.app.config['TESTING'] = True
    with api_app.app.test_client() as test_client:
        yield test_client


@pytest.fixture(autouse=True)
def sample_stock_data(monkeypatch):
    """Replace the module-level stock_data with a small, known dataset for each test."""
    data = [
        {'Date': '2024-01-01', 'Symbol': 'AAPL', 'Open': 170.0, 'Close': 172.0},
        {'Date': '2024-01-02', 'Symbol': 'AAPL', 'Open': 172.0, 'Close': 171.0},
        {'Date': '2024-01-01', 'Symbol': 'GOOGL', 'Open': 140.0, 'Close': 141.5},
    ]
    monkeypatch.setattr(api_app, 'stock_data', data)
    return data


def test_get_all_prices_returns_200_and_full_list(client, sample_stock_data):
    response = client.get('/prices')

    assert response.status_code == 200
    assert response.get_json() == sample_stock_data


def test_get_prices_for_known_symbol_returns_200(client):
    response = client.get('/prices/AAPL')

    assert response.status_code == 200

    data = response.get_json()
    assert len(data) == 2
    assert all(entry['Symbol'] == 'AAPL' for entry in data)


def test_get_prices_for_known_symbol_is_case_insensitive(client):
    response = client.get('/prices/aapl')

    assert response.status_code == 200
    assert len(response.get_json()) == 2


def test_get_prices_for_unknown_symbol_returns_404(client):
    response = client.get('/prices/UNKNOWN')

    assert response.status_code == 404
    assert 'message' in response.get_json()


def test_get_prices_for_empty_symbol_returns_400(client):
    response = client.get('/prices/ ')

    assert response.status_code == 400


def test_get_all_prices_returns_503_when_no_data(client, monkeypatch):
    monkeypatch.setattr(api_app, 'stock_data', [])

    response = client.get('/prices')

    assert response.status_code == 503
