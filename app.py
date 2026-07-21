import traceback
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import mysql.connector

app = FastAPI(title="Smart Course Enrollment Platform", version="2.0.0")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Shalu@2004",
        database="course_enrollment",
        autocommit=True,
    )


def init_db():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL UNIQUE,
                description TEXT,
                image VARCHAR(100),
                color VARCHAR(30),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS courses (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(150) NOT NULL,
                category_id INT NOT NULL,
                instructor VARCHAR(100),
                duration VARCHAR(50),
                level VARCHAR(50),
                description TEXT,
                seats INT DEFAULT 50,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (category_id) REFERENCES categories(id)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS enrollments (
                id INT AUTO_INCREMENT PRIMARY KEY,
                student_name VARCHAR(100) NOT NULL,
                student_email VARCHAR(100) NOT NULL,
                course_name VARCHAR(150) NOT NULL,
                category_name VARCHAR(100),
                phone VARCHAR(30),
                status VARCHAR(30) DEFAULT 'Pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Migrate old enrollments table if columns are missing
        cursor.execute("SHOW COLUMNS FROM enrollments LIKE 'category_name'")
        if cursor.fetchone() is None:
            cursor.execute("ALTER TABLE enrollments ADD COLUMN category_name VARCHAR(100) NULL AFTER course_name")
        cursor.execute("SHOW COLUMNS FROM enrollments LIKE 'phone'")
        if cursor.fetchone() is None:
            cursor.execute("ALTER TABLE enrollments ADD COLUMN phone VARCHAR(30) NULL AFTER category_name")
        cursor.execute("SHOW COLUMNS FROM enrollments LIKE 'status'")
        if cursor.fetchone() is None:
            cursor.execute("ALTER TABLE enrollments ADD COLUMN status VARCHAR(30) DEFAULT 'Pending' AFTER phone")

        cursor.execute("SELECT COUNT(*) FROM categories")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO categories (name, description, image, color) VALUES
                ('Computer Science', 'Modern programming, engineering, and AI-focused learning paths.', '💻', '#4f46e5'),
                ('Business & Leadership', 'Strategy, management, and entrepreneurial growth for ambitious teams.', '📈', '#0f766e'),
                ('Design & Creative', 'Visual storytelling, product design, and creative thinking workshops.', '🎨', '#db2777'),
                ('Data Science', 'Analytics, machine learning, and decision-making for data-driven careers.', '📊', '#ea580c'),
                ('Languages & Communication', 'Professional communication and language confidence for global careers.', '🗣️', '#7c3aed')
            """)

        cursor.execute("SELECT COUNT(*) FROM courses")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO courses (title, category_id, instructor, duration, level, description, seats) VALUES
                ('Full-Stack Web Development', 1, 'Asha Khan', '8 Weeks', 'Beginner', 'Build modern web apps with HTML, CSS, JavaScript, and Python.', 30),
                ('AI & Machine Learning Essentials', 1, 'Ravi Sharma', '10 Weeks', 'Intermediate', 'Learn practical machine learning workflows and real-world projects.', 25),
                ('Leadership for Growth Teams', 2, 'Mina Patel', '6 Weeks', 'Intermediate', 'Master leadership habits that scale teams and ideas.', 20),
                ('UI/UX Design System Mastery', 3, 'Noor Ali', '7 Weeks', 'Beginner', 'Create polished interfaces that feel intuitive and premium.', 22),
                ('Data Visualization with Power BI', 4, 'Daniel Brooks', '5 Weeks', 'Beginner', 'Turn raw data into meaningful insights and stunning dashboards.', 18),
                ('Business English Communication', 5, 'Sofia Martin', '4 Weeks', 'Beginner', 'Improve confidence in presentations, networking, and interviews.', 24)
            """)

        cursor.close()
        conn.close()
    except mysql.connector.Error as exc:
        print(f"Database initialization skipped: {exc}")


init_db()


class EnrollmentPayload(BaseModel):
    student_name: str
    student_email: str
    course_name: str
    category_name: str
    phone: str | None = None


def fetch_all(query: str, params=()):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, params)
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result


def get_stats():
    categories = fetch_all("SELECT * FROM categories")
    courses = fetch_all("SELECT * FROM courses")
    enrollments = fetch_all("SELECT * FROM enrollments ORDER BY id DESC LIMIT 8")
    return {
        "categories": len(categories),
        "courses": len(courses),
        "enrollments": len(enrollments),
    }


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(request, "index.html", {
        "request": request,
        "categories": fetch_all("SELECT * FROM categories ORDER BY id"),
        "stats": get_stats(),
    })


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(request, "login.html", {"request": request, "error": None})


@app.post("/login", response_class=HTMLResponse)
async def login_submit(request: Request):
    form_data = await request.form()
    username = str(form_data.get("username", "")).strip()
    password = str(form_data.get("password", "")).strip()

    if not username or not password:
        return templates.TemplateResponse(request, "login.html", {"request": request, "error": "Please enter both username and password."})
    if len(password) < 4:
        return templates.TemplateResponse(request, "login.html", {"request": request, "error": "Password should be at least 4 characters long."})
    return RedirectResponse(url="/dashboard", status_code=303)


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse(request, "dashboard.html", {
        "request": request,
        "stats": get_stats(),
        "categories": fetch_all("SELECT * FROM categories ORDER BY id"),
        "courses": fetch_all("SELECT * FROM courses ORDER BY id"),
        "enrollments": fetch_all("SELECT * FROM enrollments ORDER BY id DESC LIMIT 8"),
    })


@app.get("/categories", response_class=HTMLResponse)
async def categories_page(request: Request):
    return templates.TemplateResponse(request, "categories.html", {
        "request": request,
        "categories": fetch_all("SELECT * FROM categories ORDER BY id"),
    })


@app.get("/courses", response_class=HTMLResponse)
async def courses_page(request: Request):
    selected_category = request.query_params.get("category")
    query = """
        SELECT c.*, cat.name AS category_name
        FROM courses c
        JOIN categories cat ON c.category_id = cat.id
    """
    params = ()
    if selected_category:
        query += " WHERE cat.name = %s"
        params = (selected_category,)
    query += " ORDER BY c.id"
    return templates.TemplateResponse(request, "courses.html", {
        "request": request,
        "courses": fetch_all(query, params),
        "categories": fetch_all("SELECT * FROM categories ORDER BY id"),
        "selected_category": selected_category,
    })


@app.get("/enroll", response_class=HTMLResponse)
async def enroll_page(request: Request):
    return templates.TemplateResponse(request, "enroll.html", {
        "request": request,
        "categories": fetch_all("SELECT * FROM categories ORDER BY id"),
        "courses": fetch_all("SELECT * FROM courses ORDER BY id"),
    })


@app.post("/enroll", response_class=HTMLResponse)
async def enroll_student(request: Request):
    try:
        form_data = await request.form()
        student_name = str(form_data.get("student_name", "")).strip()
        student_email = str(form_data.get("student_email", "")).strip()
        course_name = str(form_data.get("course_name", "")).strip()
        category_name = str(form_data.get("category_name", "")).strip()
        phone = str(form_data.get("phone", "") or "")

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO enrollments (student_name, student_email, course_name, category_name, phone)
            VALUES (%s, %s, %s, %s, %s)
        """, (student_name, student_email, course_name, category_name, phone))
        conn.commit()
        cursor.close()
        conn.close()
        return templates.TemplateResponse(request, "enroll.html", {
            "request": request,
            "categories": fetch_all("SELECT * FROM categories ORDER BY id"),
            "courses": fetch_all("SELECT * FROM courses ORDER BY id"),
            "success": "Enrollment submitted successfully. We will contact you shortly.",
        })
    except Exception as exc:
        traceback.print_exc()
        error_text = str(exc) or "Unexpected server error."
        return templates.TemplateResponse(request, "enroll.html", {
            "request": request,
            "categories": fetch_all("SELECT * FROM categories ORDER BY id"),
            "courses": fetch_all("SELECT * FROM courses ORDER BY id"),
            "error": error_text,
        })


@app.get("/contact", response_class=HTMLResponse)
async def contact_page(request: Request):
    return templates.TemplateResponse(request, "contact.html", {"request": request})