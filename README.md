# Bakery Chatbot

A simple chatbot for a bakery that uses OpenAI's API to handle customer queries.

## Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and fill in your OpenAI API key:
   ```bash
   cp .env.example .env
   ```
5. Set up PostgreSQL database and update DATABASE_URL in `.env` if needed

## Running the Application

Start the server:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Endpoints

- GET `/`: Welcome message
- POST `/chat`: Send a message to the chatbot
  - Request body: `{"message": "your message here"}`

## Database

The application uses PostgreSQL as its database. Make sure PostgreSQL is installed and running on your system. 