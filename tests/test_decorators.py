import pytest
import time
from app import create_app
from app.db import init_db, get_db
from app.aop import _cache


@pytest.fixture
def app():
    app = create_app(
        {
            "TESTING": True,
            "DATABASE": "file:memdb_test?mode=memory&cache=shared",
        }
    )

    with app.app_context():
        init_db()
        # Seed any specific test data if needed
        db = get_db()
        # Ensure admin user exists for @secure test
        db.execute(
            "INSERT INTO user (username, password, role) VALUES (?, ?, ?)",
            ("testadmin", "pw", "admin"),
        )
        # Ensure feature flag exists for test
        db.execute(
            "INSERT INTO feature_flag (name, is_active) VALUES (?, ?)",
            ("test_feature", 1),
        )
        db.commit()

    yield app

    # Clean up cache after each test
    _cache.clear()


@pytest.fixture
def client(app):
    return app.test_client()


def login(client, username, password):
    # A simplified login for testing purposes
    with client.application.app_context():
        db = get_db()
        user = db.execute(
            "SELECT * FROM user WHERE username = ?", (username,)
        ).fetchone()
        with client.session_transaction() as session:
            session["user_id"] = user["id"]


# --- Tests for Decorators ---


def test_secure_decorator_success(client):
    """Test that @secure allows access with the correct role."""
    login(client, "testadmin", "pw")
    response = client.get("/auth/admin_only")
    assert response.status_code == 200
    assert b"Bienvenido, Administrador!" in response.data


def test_secure_decorator_forbidden(client):
    """Test that @secure forbids access with the wrong role."""
    # Create a non-admin user
    with client.application.app_context():
        db = get_db()
        db.execute(
            "INSERT INTO user (username, password, role) VALUES (?, ?, ?)",
            ("testuser", "pw", "user"),
        )
        db.commit()

    login(client, "testuser", "pw")
    response = client.get("/auth/admin_only")
    assert response.status_code == 403  # Forbidden


def test_secure_decorator_unauthorized(client):
    """Test that @secure denies access without login."""
    response = client.get("/auth/admin_only")
    assert response.status_code == 302  # Redirects to login


def test_cache_decorator(client):
    """Test @cache for hit, miss, and TTL expiration."""
    login(client, "testadmin", "pw")

    # 1. Cache Miss
    start_time = time.time()
    response1 = client.get("/products/")
    duration1 = time.time() - start_time
    assert response1.status_code == 200

    # 2. Cache Hit (should be much faster)
    start_time = time.time()
    response2 = client.get("/products/")
    duration2 = time.time() - start_time
    assert response2.status_code == 200
    assert response1.data == response2.data
    # A simple heuristic: hit should be significantly faster than miss
    assert duration2 < duration1 * 0.5

    # 3. Cache Expiration
    with client.application.app_context():
        # Manually expire the cache entry for testing
        key = "list_products:{}"
        _cache[key] = (_cache[key][0], time.time() - 70)  # Expire cache (TTL is 60)

    start_time = time.time()
    response3 = client.get("/products/")
    duration3 = time.time() - start_time
    assert response3.status_code == 200
    # Should behave like a miss again
    assert duration3 > duration2


def test_feature_flag_decorator_on(client):
    """Test that @feature_flag allows access when flag is ON."""
    login(client, "testadmin", "pw")
    with client.application.app_context():
        db = get_db()
        db.execute("UPDATE feature_flag SET is_active = 1 WHERE name = 'promo_editor'")
        db.commit()

    response = client.get("/promotions/")
    assert response.status_code == 200
    assert b"Crear Nueva Promoci" in response.data


def test_feature_flag_decorator_off(client):
    """Test that @feature_flag denies access when flag is OFF."""
    login(client, "testadmin", "pw")
    with client.application.app_context():
        db = get_db()
        db.execute("UPDATE feature_flag SET is_active = 0 WHERE name = 'promo_editor'")
        db.commit()

    response = client.get("/promotions/")
    assert response.status_code == 200
    assert (
        b"funcionalidad est" in response.data
    )  # Check for substring to avoid encoding issues


def test_validate_with_decorator_success(client):
    """Test @validate_with succeeds with correct data."""
    login(client, "testadmin", "pw")
    # Ensure the feature flag is on to access the POST endpoint
    with client.application.app_context():
        db = get_db()
        db.execute("UPDATE feature_flag SET is_active = 1 WHERE name = 'promo_editor'")
        db.commit()

    response = client.post(
        "/promotions/",
        data={
            "name": "Summer Sale",
            "discount_percent": 15.5,
            "start_date": "2024-06-01",
            "end_date": "2024-06-30",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"creada exitosamente" in response.data

    # Check if the data was actually inserted
    with client.application.app_context():
        db = get_db()
        promo = db.execute(
            "SELECT * FROM promotion WHERE name = 'Summer Sale'"
        ).fetchone()
        assert promo is not None
        assert promo["discount_percent"] == 15.5


def test_validate_with_decorator_failure(client):
    """Test @validate_with fails with incorrect data and flashes an error."""
    login(client, "testadmin", "pw")
    # Ensure the feature flag is on
    with client.application.app_context():
        db = get_db()
        db.execute("UPDATE feature_flag SET is_active = 1 WHERE name = 'promo_editor'")
        db.commit()

    response = client.post(
        "/promotions/",
        data={
            "name": "Invalid Sale",
            "discount_percent": 150,  # Invalid value > 100
            "start_date": "2024-01-01",
            "end_date": "2024-01-31",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Error de validaci" in response.data
    assert b"Input should be less than 100" in response.data
