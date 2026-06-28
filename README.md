# MyWorth API (Backend)

This is the backend API for the MyWorth personal finance application. It is built with **Python**, **FastAPI**, **SQLAlchemy** (with SQLite), and secured via **Argon2** and **JWT Auth**.

## Prerequisites
* Python 3.11+
* Docker (optional, for containerized testing/deployment)

---

## 1. Local Setup

**1. Create a Virtual Environment** (Recommended)
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

**2. Install Dependencies**
```bash
pip install -r requirements.txt
```

**3. Create the Environment File**
Create a `.env` file in the root directory (next to `requirements.txt`) and add the following:
```env
SECRET_KEY="your-super-secret-development-key-change-this"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=10080
```

---

## 2. Database Initialization & Seeding

Before running the server, you need to initialize the SQLite database and populate it with the mock test data.

Run the seed script from the root directory:
```bash
python scripts/seed_data.py
```
*You should see a success message, and a `myworth.db` file will appear in your folder. This creates a test user with the email `test@example.com` and password `password123`.*

---

## 3. Running the Server

Start the FastAPI server with live-reloading enabled:
```bash
uvicorn app.main:app --reload
```
The API is now running at: `http://localhost:8000`

---

## 4. Testing the API (Swagger UI)

FastAPI automatically generates an interactive testing interface. 

1. Open your browser and go to: **[http://localhost:8000/docs](http://localhost:8000/docs)**
2. Scroll down to the `POST /login` endpoint and click **Try it out**.
3. Enter the test credentials:
   * **email:** `test@example.com`
   * **password:** `password123`
4. Click **Execute**. In the server response, copy the `access_token` string.
5. Scroll to the very top of the page and click the green **Authorize** button.
6. Paste your token into the box and click **Authorize**, then close the modal.
7. You are now authenticated! Scroll down to `GET /summary/now`, click **Try it out**, and hit **Execute** to see the live financial math calculated by the server.

---

## 5. Docker Setup (Optional)

To ensure the app runs consistently across any environment, you can build and run it using Docker.

**1. Build the Docker Image:**
```bash
docker build -t myworth-backend .
```

**2. Run the Container:**
```bash
docker run -d -p 8000:8000 --name myworth-api myworth-backend
```
*(The API will again be available at `http://localhost:8000/docs`)*

**3. Stop the Container:**
```bash
docker stop myworth-api
```

---

## Project Structure

```text
backend/
├── .env                  # Secrets and config (Not tracked in Git)
├── requirements.txt      # Python dependencies
├── Dockerfile            # Docker deployment instructions
├── myworth.db            # SQLite Database (Created after seeding)
├── scripts/
│   └── seed_data.py      # Script to create tables and mock data
└── app/
    ├── main.py           # Application entry point
    ├── config.py         # Loads .env variables
    ├── database.py       # SQLAlchemy setup
    ├── models.py         # Database schemas (Tables)
    ├── schemas.py        # Pydantic schemas (JSON validation)
    ├── auth.py           # JWT & Argon2 security logic
    └── routers/          # API endpoints split by domain
        ├── users.py
        ├── settings.py
        ├── months.py
        ├── balances.py
        └── summary.py
```