# Backend Service

This is the backend service for the resident management system. It provides FastAPI-based endpoints for Face Recognition System.

## Prerequisites

- Python 3.10
- pip (Python package manager)
- SQLite3

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Capstonebara/backend.git
cd backend
```

2. Install PyTorch (Choose one based on your system):

For CPU-only version:
```bash
pip install torch==2.2.2 torchvision==0.17.2 --index-url https://download.pytorch.org/whl/cpu
```

For CUDA-enabled version:
```bash
pip install torch==2.2.2 torchvision==0.17.2
```

3. Install other dependencies:
```bash
pip install -r requirements.txt
```

## Environment Setup

1. Create a `.env` file in the root directory:
```bash
cp .env.example .env
```

2. Update the `.env` file with your configuration:
- Set up authentication credentials
- Configure JWT settings
- Set up mail settings (if needed)

## Project Structure

```
backend/
├── config/         # Configuration files
├── database/       # Database models and connection
├── middleware/     # Middleware components
├── models/         # ML models
├── routes/         # API routes
├── services/       # Business logic
├── tests/          # Test files
└── utils/          # Utility functions
```

## Running the Application

1. Start the server:
```bash
python server.py
```

The server will start on `http://0.0.0.0:5500`

## API Documentation

Once the server is running, you can access:
- Swagger UI: `http://localhost:5500/docs`

## Features

- User authentication with JWT
- Resident management (CRUD operations)
- Face recognition and embedding generation
- Admin dashboard functionalities
- File upload and processing

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.