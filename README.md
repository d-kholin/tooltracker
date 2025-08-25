# Tool Tracker

Web application to manage an inventory of tools and track loans. Data is stored in a SQLite database (`tooltracker.db`).
The backend runs with Flask and the dashboard is now built with a lightweight React front end styled with [Bootstrap](https://getbootstrap.com/). It can be executed via Docker.

## Features

- Add, edit, delete, and list tools
- Upload optional images for each tool
- Record tool value
- Lend tools to people and record return date
- Report showing how many tools each person currently has

## Running

Install dependencies and run the development server:

```bash
pip install -r requirements.txt
python app.py
```

The app will be available at [http://localhost:5000](http://localhost:5000).

### Docker

Build and run using Docker:

```bash
docker build -t tooltracker .
docker run -p 5000:5000 -v $(pwd)/data:/app tooltracker
```

Mount a volume to persist the SQLite database.
