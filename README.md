# ATOL Biological Metadata Tracking System

A FastAPI backend for tracking biological metadata integrated with PostgreSQL.

## Overview

This system manages metadata for core biological entities:
- Organism
- Sample
- Experiment
- Assembly
- BPA Initiative
- Bioproject
- Read
- Genome Note

The system follows a design pattern with three tables per core entity:
- Main table (current state)
- Submitted table (staged for submission)
- Fetched table (immutable history)

## Features

- JWT-based authentication with role-based access control
- RESTful API endpoints for all core biological entities
- PostgreSQL database with UUID primary keys and JSONB fields
- Docker and Docker Compose deployment

## Tech Stack

- FastAPI
- SQLAlchemy ORM
- Pydantic for data validation
- PostgreSQL
- JWT authentication (python-jose)
- Password hashing (passlib)
- Docker & Docker Compose

## Project Structure

```
app/
├── api/
│   └── v1/
│       ├── endpoints/
│       │   ├── assemblies.py
│       │   ├── auth.py
│       │   ├── bioprojects.py
│       │   ├── bpa_initiatives.py
│       │   ├── experiments.py
│       │   ├── genome_notes.py
│       │   ├── organisms.py
│       │   ├── reads.py
│       │   ├── samples.py
│       │   └── users.py
│       └── api.py
├── core/
│   ├── dependencies.py
│   ├── security.py
│   └── settings.py
├── db/
│   └── session.py
├── models/
│   ├── assembly.py
│   ├── bioproject.py
│   ├── bpa_initiative.py
│   ├── experiment.py
│   ├── genome_note.py
│   ├── organism.py
│   ├── read.py
│   ├── sample.py
│   └── user.py
├── schemas/
│   ├── assembly.py
│   ├── bioproject.py
│   ├── bpa_initiative.py
│   ├── experiment.py
│   ├── genome_note.py
│   ├── organism.py
│   ├── read.py
│   ├── sample.py
│   └── user.py
└── main.py
```

## Getting Started

### Prerequisites

- Docker and Docker Compose

### Running the Application

1. Clone the repository
2. Set up your environment variables or use the defaults in docker-compose.yml
3. Run the application:

```bash
docker-compose up -d
```

4. Access the API documentation at http://localhost:8000/docs

### Authentication

The API uses JWT tokens for authentication. To authenticate:

1. Create a user or use a default admin user
2. Get a token from `/auth/login` endpoint
3. Use the token in the Authorization header: `Bearer {token}`

## API Documentation

Once the application is running, you can access the interactive API documentation:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Role-Based Access Control

The system implements role-based access control with the following roles:

- **user**: Basic read access to data
- **curator**: Can create and update biological entities
- **admin**: Full access to all endpoints
- **superuser**: Special role with delete permissions

## Development

### Setting Up a Development Environment

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/atol_db
export SECRET_KEY=your_secret_key
```

4. Run the application:
```bash
uvicorn app.main:app --reload
```

## License

This project is licensed under the MIT License.
