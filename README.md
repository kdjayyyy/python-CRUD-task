# Assessment API

A FastAPI-based RESTful API for managing employee records stored in MongoDB. This project demonstrates CRUD operations with JWT authentication for protected endpoints.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [API Endpoints](#api-endpoints)
- [Testing](#testing)
- [Dependencies](#dependencies)
- [License](#license)

## Features

- **CRUD Operations**: Create, Read, Update, Delete employee records.
- **JWT Authentication**: Secure endpoints using JWT tokens.
- **MongoDB Integration**: Store data in a MongoDB database using the Motor driver.
- **Form Data Handling**: Uses `python-multipart` for handling form requests (for token generation).

## Prerequisites

- Python 3.12
- MongoDB server running locally or accessible remotely

## Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/kdjayyyy/python-CRUD-task.git
   cd python-CRUD-task
   ```

2. **Set up a virtual environment** (if not already created):

   On Windows:

   ```bash
   python -m venv myenv
   myenv\Scripts\activate
   ```

   On Unix-based systems:

   ```bash
   python3 -m venv myenv
   source myenv/bin/activate
   ```

3. **Install the dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

## Configuration

Create a `.env` file in the project root (if it doesn't exist) with the following content:

```ini
MONGO_URI=mongodb://localhost:27017
MONGO_DB_NAME=assessment_db

JWT_SECRET_KEY=<your_secret_key_here>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Demo admin credentials
ADMIN_USERNAME=admin
# Use hashed password for security:
ADMIN_PASSWORD_HASH=<your_hash_password>
```

Modify the values as needed for your environment.

## Running the Application

Start the FastAPI application using Uvicorn:

```bash
uvicorn app.main:app --reload
```

The API will be available at [http://127.0.0.1:8000](http://127.0.0.1:8000).

## API Endpoints

### Public Endpoints

- **GET /**: Health check endpoint. Returns the API status.
- **GET /employees**: List employees, optionally filtered by department. Supports pagination and sorting by joining date.
- **GET /employees/search**: Search employees by skill.
- **GET /employees/{employee_id}**: Retrieve details of a specific employee.
- **GET /employees/avg-salary**: Get average salary for each department.

### Protected Endpoints (Require JWT Authentication)

- **POST /employees/token**: Obtain an access token by providing admin credentials. Use form data (`username` and `password`).
- **POST /employees**: Create a new employee. Requires the `Authorization: Bearer <token>` header.
- **PUT /employees/{employee_id}**: Update an existing employee. Requires JWT authentication.
- **DELETE /employees/{employee_id}**: Delete an employee record. Requires JWT authentication.

## Testing

You can use tools like `curl`, [Postman](https://www.postman.com/), or [HTTPie](https://httpie.io/) to test the API endpoints. Below are a few examples using `curl`:

### Obtain a JWT Token

```bash
curl -X POST -F "username=admin" -F "password=password123" http://127.0.0.1:8000/employees/token
```

### Create an Employee (Protected)

```bash
curl -X POST \
  -H "Authorization: Bearer <your_access_token>" \
  -H "Content-Type: application/json" \
  -d '{"employee_id": "E123", "name": "John Doe", "department": "IT", "salary": 60000, "joining_date": "2023-01-15", "skills": ["Python", "FastAPI"]}' \
  http://127.0.0.1:8000/employees
```

### Other Endpoints

Refer to the API Endpoints section above for additional endpoints.

### Running Unit Tests

If tests are provided, you can run them with:

```bash
pytest
```

## Dependencies

The project relies on the following Python packages:

- FastAPI
- Uvicorn
- Motor (for MongoDB)
- Pydantic & Pydantic-Settings
- Python-JOSE (for JWT handling)
- bcrypt (for password hashing)
- python-multipart (for form data handling)
- pytest & pytest-asyncio (for testing)

See `requirements.txt` for the full list.

