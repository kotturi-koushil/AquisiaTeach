from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    jsonify,
)

import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", os.urandom(24))
app.config["UPLOAD_FOLDER"] = "uploads"




def get_db_connection():
    """Create and return a new database connection"""
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        database=os.getenv("DB_NAME"),
        port=int(os.getenv("DB_PORT", 3306)),
    )


def initialize_database():
    """Initialize database tables if they don't exist"""
    conn = None
    curr = None
    try:
        conn = get_db_connection()
        curr = conn.cursor(dictionary=True)

        curr.execute(
            """
            CREATE TABLE IF NOT EXISTS questions(
                day INT,
                question TEXT,
                option_a VARCHAR(255),
                option_b VARCHAR(255),
                option_c VARCHAR(255),
                option_d VARCHAR(255),
                correct_option INT,
                subject VARCHAR(255),
                topic text,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        curr.execute(
            """
            CREATE TABLE IF NOT EXISTS syllabus (
                day INT PRIMARY KEY,
                topic TEXT NOT NULL,
                description TEXT
            )
            """
        )

        curr.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                phone VARCHAR(15) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                category VARCHAR(50) NOT NULL,
                district VARCHAR(50) NOT NULL,
                password VARCHAR(200) NOT NULL,
                subscription bool,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )
        curr.execute(
            """
        CREATE TABLE IF NOT EXISTS quiz_results (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_email VARCHAR(255) NOT NULL,
            day INT NOT NULL,
            total_score INT NOT NULL,
            total_questions INT NOT NULL,
            completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            attempts INT,
            district VARCHAR(255),
            FOREIGN KEY (user_email) REFERENCES users(email),
            UNIQUE KEY user_day_unique (user_email, day)
        )
        """
        )

        # Create subject_results table exactly as specified
        curr.execute(
            """
        CREATE TABLE IF NOT EXISTS subject_results (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_email VARCHAR(255) NOT NULL,
            day INT NOT NULL,
            subject VARCHAR(255) NOT NULL,
            correct_answers INT NOT NULL,
            total_questions INT NOT NULL,
            percentage INT NOT NULL,
            completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_email) REFERENCES users(email),
            UNIQUE KEY user_day_subject_unique (user_email, day, subject)
        )
        """
        )
        conn.commit()

    except Exception as e:
        print(f"Database initialization error: {str(e)}")
    finally:
        if curr:
            curr.close()
        if conn:
            conn.close()


# Initialize database tables
initialize_database()




@app.route("/add-question", methods=["GET", "POST"])
def addQuestions():
    if request.method == "POST":
        day = request.form.get("day1", "").strip()
        question = request.form.get("question_text", "").strip()
        optionA = request.form.get("option_a", "").strip()
        optionB = request.form.get("option_b", "").strip()
        optionC = request.form.get("option_c", "").strip()
        optionD = request.form.get("option_d", "").strip()
        correct_option = request.form.get("correct_option", "").strip()
        subject = request.form.get("subject", "").strip()
        topic = request.form.get("topic", "").strip()

        if not all(
            [
                day,
                question,
                optionA,
                optionB,
                optionC,
                optionD,
                correct_option,
                subject,
                topic,
            ]
        ):
            flash("All fields are required", "error")
            return redirect(url_for("addQuestions"))

        conn = None
        curr = None
        try:
            conn = get_db_connection()
            curr = conn.cursor()

            curr.execute(
                """INSERT INTO questions 
                (day, question, option_a, option_b, option_c, option_d, correct_option, subject,topic)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s,%s)""",
                (
                    day,
                    question,
                    optionA,
                    optionB,
                    optionC,
                    optionD,
                    correct_option,
                    subject,
                    topic,
                ),
            )
            conn.commit()

            flash("Question added successfully", "success")
            return redirect(url_for("addQuestions"))

        except Exception as e:
            flash(f"Error adding question: {str(e)}", "error")
            return redirect(url_for("addQuestions"))
        finally:
            if curr:
                curr.close()
            if conn:
                conn.close()

    return render_template("final_question_adding.html")


@app.route("/add-question-sample", methods=["GET", "POST"])
def addQuestions1():
    if request.method == "POST":
        day = request.form.get("day1", "").strip()
        question = request.form.get("question_text", "").strip()
        optionA = request.form.get("option_a", "").strip()
        optionB = request.form.get("option_b", "").strip()
        optionC = request.form.get("option_c", "").strip()
        optionD = request.form.get("option_d", "").strip()
        correct_option = request.form.get("correct_option", "").strip()
        subject = request.form.get("subject", "").strip()

        if not all(
            [day, question, optionA, optionB, optionC, optionD, correct_option, subject]
        ):
            flash("All fields are required", "error")
            return redirect(url_for("addQuestions"))

        conn = None
        curr = None
        try:
            conn = get_db_connection()
            curr = conn.cursor()

            curr.execute(
                """INSERT INTO sample
                (day, question, option_a, option_b, option_c, option_d, correct_option, subject)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                (
                    day,
                    question,
                    optionA,
                    optionB,
                    optionC,
                    optionD,
                    correct_option,
                    subject,
                ),
            )
            conn.commit()

            flash("Question added successfully", "success")
            return redirect(url_for("addQuestions1"))

        except Exception as e:
            flash(f"Error adding question: {str(e)}", "error")
            return redirect(url_for("addQuestions1"))
        finally:
            if curr:
                curr.close()
            if conn:
                conn.close()

    return render_template("sample_test.html")

@app.route("/add-schedule", methods=["GET", "POST"])
def addSchedule():
    if request.method == "POST":
        day = request.form.get("day1", "").strip()
        topic = request.form.get("Topic_text", "").strip()
        desc = request.form.get("Description", "").strip()

        if not all(
            [day,topic,desc]
        ):
            flash("All fields are required", "error")
            return redirect(url_for("addSchedule"))

        conn = None
        curr = None
        try:
            conn = get_db_connection()
            curr = conn.cursor()

            curr.execute(
                """Insert into  syllabus  values (%s,%s,%s)""",
                (
                    day,topic,desc
                ),
            )
            conn.commit()

            flash("Schedule added successfully", "success")
            return redirect(url_for("addSchedule"))

        except Exception as e:
            flash(f"Error adding Schedule: {str(e)}", "error")
            return redirect(url_for("addSchedule"))
        finally:
            if curr:
                curr.close()
            if conn:
                conn.close()

    return render_template("schedule.html")

@app.route("/")
def index():
    return render_template("index.html")



if __name__ == "__main__":
    app.run()