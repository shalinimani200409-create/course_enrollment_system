CREATE DATABASE IF NOT EXISTS course_enrollment;
USE course_enrollment;

CREATE TABLE IF NOT EXISTS categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    image VARCHAR(100),
    color VARCHAR(30),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

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
);

CREATE TABLE IF NOT EXISTS enrollments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_name VARCHAR(100) NOT NULL,
    student_email VARCHAR(100) NOT NULL,
    course_name VARCHAR(150) NOT NULL,
    category_name VARCHAR(100),
    phone VARCHAR(30),
    status VARCHAR(30) DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO categories (name, description, image, color) VALUES
('Computer Science', 'Modern programming, engineering, and AI-focused learning paths.', '💻', '#4f46e5'),
('Business & Leadership', 'Strategy, management, and entrepreneurial growth for ambitious teams.', '📈', '#0f766e'),
('Design & Creative', 'Visual storytelling, product design, and creative thinking workshops.', '🎨', '#db2777'),
('Data Science', 'Analytics, machine learning, and decision-making for data-driven careers.', '📊', '#ea580c'),
('Languages & Communication', 'Professional communication and language confidence for global careers.', '🗣️', '#7c3aed');

INSERT INTO courses (title, category_id, instructor, duration, level, description, seats) VALUES
('Full-Stack Web Development', 1, 'Asha Khan', '8 Weeks', 'Beginner', 'Build modern web apps with HTML, CSS, JavaScript, and Python.', 30),
('AI & Machine Learning Essentials', 1, 'Ravi Sharma', '10 Weeks', 'Intermediate', 'Learn practical machine learning workflows and real-world projects.', 25),
('Leadership for Growth Teams', 2, 'Mina Patel', '6 Weeks', 'Intermediate', 'Master leadership habits that scale teams and ideas.', 20),
('UI/UX Design System Mastery', 3, 'Noor Ali', '7 Weeks', 'Beginner', 'Create polished interfaces that feel intuitive and premium.', 22),
('Data Visualization with Power BI', 4, 'Daniel Brooks', '5 Weeks', 'Beginner', 'Turn raw data into meaningful insights and stunning dashboards.', 18),
('Business English Communication', 5, 'Sofia Martin', '4 Weeks', 'Beginner', 'Improve confidence in presentations, networking, and interviews.', 24);