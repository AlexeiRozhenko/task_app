# Full-stack app

This is a full-stack FastAPI application that allows you to manage your tasks. It features a backend API, a PostgreSQL database, and is served with Nginx in a Dockerized environment for easy deployment.

Key Features:

- User registration with password validation and authentication
- Access and refresh tokens for secure and scalable user management
- Ability to log out and switch users seamlessly
- Backend deployed with Uvicorn

## Tech Stack

- **Backend**: FastAPI
- **Frontend**: HTML, JavaScript
- **Database**: PostgreSQL
- **Reverse Proxy**: Nginx
- **Containerization**: Docker, Docker Compose

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/AlexeiRozhenko/task-tracker.git
cd pet-app
```

### 2. Create .env file

Add your PostgreSQL credentials in a .env file:

SECRET_KEY=key_for_hash

ALGORITHM=hash_algorithm

POSTGRES_USER=your_username

POSTGRES_PASSWORD=your_password

POSTGRES_DB=your_db_name

DATABASE_URL=your_db_url

### 3. Start the application

Run the following command to build and start the application using Docker Compose:

```bash
docker-compose up --build -d
```

Your app will be accessible at http://localhost

### 4. Stop the application

To stop and remove the containers:

```bash
docker-compose down
```
