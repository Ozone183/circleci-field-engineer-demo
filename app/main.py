"""
Flask API for CircleCI Field Engineer demonstration.

This API demonstrates:
- RESTful endpoints
- Database integration (Postgres)
- Testing with pytest
- Docker containerization
- CI/CD with CircleCI
"""
import os
from flask import Flask, jsonify, request
from app.database import db, User

# Create Flask app
app = Flask(__name__)

# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL',
    'postgresql://postgres:password@localhost:5432/circleci_demo'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)


@app.route('/')
def index():
    """
    Root endpoint - health check.
    
    Returns:
        JSON response with API status and version
    """
    return jsonify({
        'status': 'healthy',
        'message': 'CircleCI Field Engineer Demo API',
        'version': '1.0.0'
    })


@app.route('/health')
def health():
    """
    Health check endpoint.
    
    Verifies database connection and API status.
    
    Returns:
        JSON response with health status
    """
    try:
        # Check database connection
        db.session.execute(db.text('SELECT 1'))
        return jsonify({
            'status': 'healthy',
            'database': 'connected'
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'database': 'disconnected',
            'error': str(e)
        }), 500


@app.route('/users', methods=['GET', 'POST'])
def users():
    """
    Users endpoint.
    
    GET: List all users
    POST: Create a new user
    
    Returns:
        JSON response with user data
    """
    if request.method == 'GET':
        # Get all users
        all_users = User.query.all()
        return jsonify({
            'users': [user.to_dict() for user in all_users]
        })
    
    elif request.method == 'POST':
        # Create new user
        data = request.get_json()
        
        # Validate input
        if not data or 'username' not in data or 'email' not in data:
            return jsonify({
                'error': 'username and email are required'
            }), 400
        
        # Check if user already exists
        if User.query.filter_by(username=data['username']).first():
            return jsonify({
                'error': 'username already exists'
            }), 409
        
        if User.query.filter_by(email=data['email']).first():
            return jsonify({
                'error': 'email already exists'
            }), 409
        
        # Create user
        new_user = User(
            username=data['username'],
            email=data['email']
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({
            'message': 'user created successfully',
            'user': new_user.to_dict()
        }), 201


@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """
    Get a specific user by ID.
    
    Args:
        user_id: User ID
    
    Returns:
        JSON response with user data
    """
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({
            'error': 'user not found'
        }), 404
    
    return jsonify({
        'user': user.to_dict()
    })


# Create tables on startup (for development)
#with app.app_context():
#    db.create_all()


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)