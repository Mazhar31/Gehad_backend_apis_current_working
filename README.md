# OneQlek Backend API

A comprehensive FastAPI backend for the OneQlek project management and client dashboard system.

## Features

- **Authentication & Authorization**: JWT-based auth with role-based access control
- **Two-Factor Authentication**: Google Authenticator support for admins and users
- **Project Management**: Complete CRUD operations for projects, clients, and users
- **Invoice Management**: Manual and automatic subscription invoice generation
- **File Upload**: Image and ZIP file handling with optimization
- **Dashboard Deployment**: ZIP file deployment to projects or subdomains
- **API Documentation**: Auto-generated OpenAPI/Swagger documentation

## Tech Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy**: SQL toolkit and ORM
- **PostgreSQL**: Primary database
- **Alembic**: Database migration tool
- **JWT**: JSON Web Tokens for authentication
- **PyOTP**: Two-factor authentication
- **Pillow**: Image processing
- **Pytest**: Testing framework

## Installation

1. **Clone the repository**
```bash
cd oneqlek_backend
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your database credentials and settings
```

5. **Set up PostgreSQL database**
```bash
# Create database
createdb oneqlek_db

# Update DATABASE_URL in .env file
DATABASE_URL=postgresql://username:password@localhost:5432/oneqlek_db
```

6. **Run database migrations**
```bash
alembic upgrade head
```

7. **Start the server**
```bash
python -m app.main
# Or using uvicorn directly:
uvicorn app.main:app --reload
```

## API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Project Structure

```
oneqlek_backend/
├── app/
│   ├── api/
│   │   ├── auth/          # Authentication routes
│   │   └── v1/            # API v1 routes
│   ├── core/              # Core configuration
│   ├── models/            # SQLAlchemy models
│   ├── schemas/           # Pydantic schemas
│   ├── services/          # Business logic
│   ├── utils/             # Utilities and dependencies
│   └── tests/             # Test files
├── alembic/               # Database migrations
├── uploads/               # File uploads directory
└── static/                # Static files
```

## API Endpoints

### Authentication
- `POST /api/auth/admin/login` - Admin login
- `POST /api/auth/user/login` - User login
- `POST /api/auth/admin/setup-2fa` - Setup 2FA for admin
- `POST /api/auth/admin/enable-2fa` - Enable 2FA for admin
- `GET /api/auth/me` - Get current user info

### Admin Dashboard
- `GET /api/admin/dashboard/stats` - Dashboard statistics
- `GET /api/admin/dashboard/recent-projects` - Recent projects

### Client Management
- `GET /api/admin/clients` - List clients
- `POST /api/admin/clients` - Create client
- `PUT /api/admin/clients/{id}` - Update client
- `DELETE /api/admin/clients/{id}` - Delete client

### Project Management
- `GET /api/admin/projects` - List projects
- `POST /api/admin/projects` - Create project
- `PUT /api/admin/projects/{id}` - Update project
- `DELETE /api/admin/projects/{id}` - Delete project

### User Access
- `GET /api/admin/projects/user/my-projects` - Get user's projects

## Environment Variables

```env
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/oneqlek_db

# JWT Configuration
SECRET_KEY=your-super-secret-jwt-key-change-this-in-production-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=150

# Application Configuration
PROJECT_NAME=OneQlek Backend API
ENVIRONMENT=development
DEBUG=True

# File Upload Configuration
MAX_FILE_SIZE=10485760  # 10MB
UPLOAD_DIR=uploads
STATIC_DIR=static

# CORS Configuration
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

## Testing

Run tests using pytest:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest app/tests/test_auth.py
```

## Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## File Uploads

The API supports file uploads for:
- User avatars
- Client logos
- Project images
- Portfolio images
- Dashboard ZIP files

Files are automatically optimized and stored in the `uploads/` directory.

## Two-Factor Authentication

The system supports Google Authenticator-style TOTP (Time-based One-Time Password):

1. Admin/User sets up 2FA by scanning QR code
2. Verifies setup with authenticator app
3. Enables 2FA for their account
4. Future logins require 2FA token

## Security Features

- Password hashing with bcrypt
- JWT token authentication
- Role-based access control
- Input validation and sanitization
- File upload security
- CORS configuration
- Rate limiting (can be added)

## Development

1. **Code Style**: Follow PEP 8 guidelines
2. **Testing**: Write tests for new features
3. **Documentation**: Update API documentation
4. **Migrations**: Create migrations for model changes

## Production Deployment

1. Set `ENVIRONMENT=production` in .env
2. Use strong `SECRET_KEY`
3. Configure production database
4. Set up reverse proxy (nginx)
5. Use process manager (systemd, supervisor)
6. Enable HTTPS
7. Set up monitoring and logging

## Contributing

1. Fork the repository
2. Create feature branch
3. Write tests for new features
4. Ensure all tests pass
5. Submit pull request

## License

This project is proprietary software for OneQlek.