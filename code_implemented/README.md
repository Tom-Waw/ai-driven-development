# FastAPI CRUD Application

This is a simple FastAPI application that provides CRUD (Create, Read, Update, Delete) operations for a User entity.

## Requirements

- Python 3.10+
- FastAPI
- Uvicorn

## Installation

1. Clone the repository:

```bash
$ git clone <repository_url>
$ cd <repository_name>
```

2. Install the dependencies:

```bash
$ pip install -r requirements.txt
```

## Running the Application

To start the FastAPI application, run the following command:

```bash
$ python app/main.py
```

The application will be available at `http://127.0.0.1:8000`.

## API Endpoints

- **POST /users**: Create a new user with name and age and return the user ID.
- **GET /users/{user_id}**: Retrieve the details of a user based on the user ID.
- **PUT /users/{user_id}**: Update the information of a user (name and/or age) based on the user ID.
- **DELETE /users/{user_id}**: Delete a user based on the user ID.

## Running Tests

To run the tests, use the following command:

```bash
$ pytest
```
