# Task-Management-API
MEDIVUE BACKEND ASSESSMENT
Task Management API

This project is a simple Task Management API built using FastAPI and PostgreSQL. It supports creating tasks, updating them, deleting them, and retrieving them with filtering and pagination. The application is fully containerized using Docker.

Setup

The easiest way to run the application is with Docker:

docker-compose up --build

Once running, the all APIs will be shown at:

http://localhost:8000/docs

PostgreSQL runs inside Docker and connects automatically to the API service.

API Overview

The API provides endpoints to create tasks, retrieve tasks with filters, retrieve a single task by ID, partially update tasks, and delete tasks. Filtering is supported by completed status, priority level, and tags. Pagination is handled using limit and offset query parameters.

Design Decisions

Tags are implemented using a many to many join table (task_tags). This keeps the database normalised and portable across databases. I used a relational join table because it scales better and also allows proper indexing for filtering queries.

Soft delete is implemented using an is_deleted flag instead of permanently removing records. This prevents accidental data loss and it is how deletion is handled in production grade systems. The trade-off is that all queries must filter out deleted records and also enforce a deletion policy later on.

Indexes are added to commonly filtered fields such as priority, completed, due_date, and is_deleted, as well as the tag name field. This improves performance when filtering tasks.

Validation and Error Handling

Validation is handled using Pydantic models. The API ensures that the title is not empty and does not exceed 200 characters, priority is between 1 and 5, and due_date is not in the past.

Validation errors follow a structured format:

{
  "error": "Validation Failed",
  "details": {
    "priority": "Must be between 1 and 5"
  }
}

This ensures consistent and predictable error responses.

Testing

Basic tests are written using pytest and FastAPI’s TestClient. The tests cover successful task creation, validation failures, filtering logic, partial updates, and soft delete behavior.

Tests can be run with:

pytest
