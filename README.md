# BookRecommenderSystem
BookRecommenderSystem
# Project Readme

This project is a FastAPI-based API server that provides endpoints for managing users, book-related operations, and generating personalized recommendations.

## Table of Contents
- [Project Overview](#project-overview)
- [Installation](#installation)
- [Usage](#usage)
- [Endpoints](#endpoints)
- [Contributing](#contributing)
- [License](#license)

## Project Overview
The application consists of three main modules:
- **Users**: Manages user data and authentication.
- **Books**: Handles CRUD operations related to books.
- **Recommendations**: Provides personalized book recommendations based on user preferences.

### Technology Stack
- **FastAPI**: High-performance web framework for building APIs with Python.
- **Python**: Programming language used throughout the project.
- **Postgres**: Database for metadata and other relational data storage.
- **MongoDB**: Database for book pdfs storage.

## Installation
To set up the project locally, follow these steps:

```bash
git clone https://github.com/yourusername/project.git
cd project
pip install -r requirements.txt
```

## Usage
Start the development server using Uvicorn:

```bash
uvicorn app.main:app --reload
```

Access the API documentation at http://localhost:8000/docs.

## Endpoints
The following routes are available in the API:

| Route              | Description               |
|--------------------|---------------------------|
| `/books`           | Book management           |
| `/users`           | User management           |
| `/recommendations` | Recommendation generation |
| `/ratings`         | Ratings                   |
| `/statistics`      | Statistics                |

Each endpoint has its own detailed documentation within the Swagger UI accessible via the above link.

## Contributing
We welcome contributions! Please open an issue or submit a pull request if you have any improvements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.