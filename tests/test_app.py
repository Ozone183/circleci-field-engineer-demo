"""
Tests for the CircleCI Field Engineer Demo API.

These tests demonstrate:
- Unit testing with pytest
- Testing Flask endpoints
- Testing database integration
- Test coverage for CI/CD pipeline
"""
import pytest
from app.main import app
from app.database import db, User


@pytest.fixture
def client():
    """
    Create a test client for the Flask app.
    
    This fixture sets up a test database and provides a client
    for making requests to the API.
    """
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()


def test_index(client):
    """Test the root endpoint."""
    response = client.get('/')
    assert response.status_code == 200
    
    data = response.get_json()
    assert data['status'] == 'healthy'
    assert data['message'] == 'CircleCI Field Engineer Demo API'
    assert data['version'] == '1.0.0'


def test_health(client):
    """Test the health check endpoint."""
    response = client.get('/health')
    assert response.status_code == 200
    
    data = response.get_json()
    assert data['status'] == 'healthy'
    assert data['database'] == 'connected'


def test_get_users_empty(client):
    """Test getting users when database is empty."""
    response = client.get('/users')
    assert response.status_code == 200
    
    data = response.get_json()
    assert 'users' in data
    assert len(data['users']) == 0


def test_create_user(client):
    """Test creating a new user."""
    response = client.post('/users', json={
        'username': 'testuser',
        'email': 'test@example.com'
    })
    
    assert response.status_code == 201
    
    data = response.get_json()
    assert data['message'] == 'user created successfully'
    assert data['user']['username'] == 'testuser'
    assert data['user']['email'] == 'test@example.com'


def test_create_user_missing_fields(client):
    """Test creating a user with missing required fields."""
    response = client.post('/users', json={
        'username': 'testuser'
    })
    
    assert response.status_code == 400
    
    data = response.get_json()
    assert 'error' in data


def test_create_duplicate_username(client):
    """Test creating a user with duplicate username."""
    # Create first user
    client.post('/users', json={
        'username': 'testuser',
        'email': 'test1@example.com'
    })
    
    # Try to create second user with same username
    response = client.post('/users', json={
        'username': 'testuser',
        'email': 'test2@example.com'
    })
    
    assert response.status_code == 409
    
    data = response.get_json()
    assert 'error' in data
    assert 'username already exists' in data['error']


def test_create_duplicate_email(client):
    """Test creating a user with duplicate email."""
    # Create first user
    client.post('/users', json={
        'username': 'testuser1',
        'email': 'test@example.com'
    })
    
    # Try to create second user with same email
    response = client.post('/users', json={
        'username': 'testuser2',
        'email': 'test@example.com'
    })
    
    assert response.status_code == 409
    
    data = response.get_json()
    assert 'error' in data
    assert 'email already exists' in data['error']


def test_get_users_after_creation(client):
    """Test getting users after creating some."""
    # Create two users
    client.post('/users', json={
        'username': 'user1',
        'email': 'user1@example.com'
    })
    
    client.post('/users', json={
        'username': 'user2',
        'email': 'user2@example.com'
    })
    
    # Get all users
    response = client.get('/users')
    assert response.status_code == 200
    
    data = response.get_json()
    assert 'users' in data
    assert len(data['users']) == 2


def test_get_user_by_id(client):
    """Test getting a specific user by ID."""
    # Create a user
    create_response = client.post('/users', json={
        'username': 'testuser',
        'email': 'test@example.com'
    })
    
    user_id = create_response.get_json()['user']['id']
    
    # Get the user by ID
    response = client.get(f'/users/{user_id}')
    assert response.status_code == 200
    
    data = response.get_json()
    assert data['user']['username'] == 'testuser'
    assert data['user']['email'] == 'test@example.com'


def test_get_nonexistent_user(client):
    """Test getting a user that doesn't exist."""
    response = client.get('/users/999')
    assert response.status_code == 404
    
    data = response.get_json()
    assert 'error' in data
    assert 'user not found' in data['error']