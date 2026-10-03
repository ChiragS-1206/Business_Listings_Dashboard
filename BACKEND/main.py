from fastapi import FastAPI
import mysql.connector
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ connection function (IMPORTANT)
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="business_db",
        autocommit=True,
        connection_timeout=10
    )


@app.get("/")
def home():
    return {"message": "API Running 🚀"}


# ✅ CITY
@app.get("/city-count")
def city_count():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT TRIM(city) as city, COUNT(*) as count 
        FROM listing_master 
        GROUP BY city
    """)

    result = cursor.fetchall()

    cursor.close()
    conn.close()

    return result


# ✅ CATEGORY
@app.get("/category-count")
def category_count():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT category, COUNT(*) as count 
        FROM listing_master 
        GROUP BY category
    """)

    result = cursor.fetchall()

    cursor.close()
    conn.close()

    return result


# ✅ SOURCE
@app.get("/source-count")
def source_count():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT source, COUNT(*) as count 
        FROM listing_master 
        GROUP BY source
    """)

    result = cursor.fetchall()

    cursor.close()
    conn.close()

    return result