- [Task Management API](#task-management-api)
  - [Features](#features)
  - [API Endpoints](#api-endpoints)
    - [POST `/tasks/`](#post-tasks)
    - [GET `/tasks/`](#get-tasks)
    - [PUT `/tasks/{task_id}`](#put-taskstask_id)
    - [DELETE `/tasks/{task_id}`](#delete-taskstask_id)
    - [GET `/tasks/suggestions/`](#get-taskssuggestions)
  - [Setup and Installation](#setup-and-installation)
    - [Prerequisites](#prerequisites)
    - [Steps](#steps)
  - [Technologies Used](#technologies-used)
  - [Future Development Ideas](#future-development-ideas)

# Task Management API

A FastAPI-based Task Management API designed to manage tasks, including creating, updating, deleting, and fetching tasks. The API also provides a recommendation feature to suggest similar tasks based on text similarity using TF-IDF and cosine similarity.

## Features

- **Task Creation**: Allows creating new tasks with a title, description, and due date.
- **Task Fetching**: Fetches tasks with optional filtering by status, sorting by various fields, and ordering.
- **Task Update**: Allows updating the title, description, or status of an existing task.
- **Task Deletion**: Deletes a task by its ID.
- **Task Suggestions**: Suggests tasks similar to a given task based on its title and description using cosine similarity and TF-IDF.
  
## API Endpoints

### POST `/tasks/`

Create a new task.

**Request Body**:

```json
{
  "title": "Task title",
  "description": "Task description",
  "due_date": "2025-03-01T00:00:00"
}
```

**Response**:

```json
{
  "id": 1,
  "title": "Task title",
  "description": "Task description",
  "created_at": "2025-03-01T00:00:00",
  "due_date": "2025-03-01T00:00:00",
  "status": "pending"
}
```

### GET `/tasks/`

Fetch tasks with optional filters.

**Query Parameters**:

- `status`: Filter tasks by status (optional).
- `sort_by`: Sort tasks by a specified field (created_at or due_date). Defaults to `created_at`.
- `order`: Sort order (`asc` or `desc`). Defaults to `asc`.

**Response**:

```json
[
  {
    "id": 1,
    "title": "Task title",
    "description": "Task description",
    "created_at": "2025-03-01T00:00:00",
    "due_date": "2025-03-01T00:00:00",
    "status": "pending"
  }
]
```

### PUT `/tasks/{task_id}`

Update an existing task by its ID.

**Request Body**:

```json
{
  "title": "Updated title",
  "description": "Updated description",
  "status": "in_progress"
}
```

**Response**:

```json
{
  "id": 1,
  "title": "Updated title",
  "description": "Updated description",
  "created_at": "2025-03-01T00:00:00",
  "due_date": "2025-03-01T00:00:00",
  "status": "in_progress"
}
```

### DELETE `/tasks/{task_id}`

Delete a task by its ID.

**Response**:

```json
{
  "message": "Task deleted"
}
```

### GET `/tasks/suggestions/`

Get task suggestions based on text similarity or task transition sequences.

**Query Parameters**:

- `target_title`: The title of the target task for similarity comparison.
- `target_description`: The description of the target task for similarity comparison.
- `top_n`: Number of similar tasks to return (default: 5).
- `status_filter`: Filter by task status (optional).

**Response**:

```json
{
  "message": [
    {
      "title": "Similar task 1",
      "description": "Description of similar task 1",
      "due_date": "2025-03-01T00:00:00"
    }
  ]
}
```

## Setup and Installation

### Prerequisites

Ensure that Docker and Docker Compose are installed and running on your machine. You can follow the official installation guides for both tools:

- [Docker Installation Guide](https://docs.docker.com/get-docker/)
- [Docker Compose Installation Guide](https://docs.docker.com/compose/install/)

### Steps

1. Clone the repository:

   ```bash
   git clone https://github.com/balkanyilajos/task-management
   ```

2. Run the API:

   ```bash
   cd task-management
   docker-compose up
   ```

3. Access the API at `http://localhost/`. I suggest using `http://localhost/docs` to try CRUD endpoints.

## Technologies Used

- **FastAPI**: Web framework for building APIs.
- **SQLAlchemy**: ORM used for database management.
- **SQLite**: Database used for storing tasks.
- **Pandas**: Data manipulation for the task suggestion feature.
- **scikit-learn**: For text similarity using TF-IDF and cosine similarity.

## Future Development Ideas

- Further optimization and fine-tuning of the statistical models used in smart suggestion process, ensuring better accuracy and performance.
- Consider weighing the user's input based on its position within the text they've already entered.
