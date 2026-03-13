from fastapi import FastAPI, Request, Form, UploadFile, File, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from email_service import send_email
import shutil
import os

import models
from database import engine, SessionLocal
from ai_model import predict_late

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")

UPLOAD_FOLDER = "uploads"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


# -----------------------------
# Database Session
# -----------------------------

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -----------------------------
# Create Default Users
# -----------------------------

db = SessionLocal()

teacher = db.query(models.User).filter(models.User.username == "admin").first()

if not teacher:
    teacher_user = models.User(
        username="admin",
        password="admin123",
        role="teacher"
    )
    db.add(teacher_user)

student = db.query(models.User).filter(models.User.username == "student").first()

if not student:
    student_user = models.User(
        username="student",
        password="1234",
        role="student"
    )
    db.add(student_user)

db.commit()
db.close()


# -----------------------------
# Login Page
# -----------------------------

@app.get("/")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


# -----------------------------
# Login
# -----------------------------

@app.post("/login")
def login(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):

    user = db.query(models.User).filter(models.User.username == username).first()

    if user and user.password == password:

        if user.role == "teacher":
            return RedirectResponse("/teacher", status_code=303)

        if user.role == "student":
            return RedirectResponse("/student", status_code=303)

    return {"message": "Invalid login"}


# -----------------------------
# Teacher Dashboard
# -----------------------------

@app.get("/teacher")
def teacher(request: Request):
    return templates.TemplateResponse("teacher.html", {"request": request})


# -----------------------------
# Create Assignment
# -----------------------------

@app.post("/create_assignment")
def create_assignment(
    title: str = Form(...),
    description: str = Form(...),
    deadline: str = Form(...),
    db: Session = Depends(get_db)
):

    assignment = models.Assignment(
        title=title,
        description=description,
        deadline=deadline
    )

    db.add(assignment)
    db.commit()

    # Email notification
    send_email(
        "student@gmail.com",
        "New Assignment Posted",
        f"""
New Assignment Created

Title: {title}
Description: {description}
Deadline: {deadline}

Login to submit your assignment.
"""
    )

    return RedirectResponse("/teacher", status_code=303)


# -----------------------------
# Student Dashboard
# -----------------------------

@app.get("/student")
def student(request: Request, db: Session = Depends(get_db)):

    assignments = db.query(models.Assignment).all()

    return templates.TemplateResponse(
        "student.html",
        {
            "request": request,
            "assignments": assignments
        }
    )


# -----------------------------
# Submit Assignment
# -----------------------------

@app.post("/submit")
def submit(
    student_name: str = Form(...),
    assignment_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)

    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    submission = models.Submission(
        student_name=student_name,
        assignment_id=assignment_id,
        file_path=filepath
    )

    db.add(submission)
    db.commit()

    send_email(
        "teacher@gmail.com",
        "Assignment Submitted",
        f"{student_name} has submitted assignment ID {assignment_id}"
    )

    return RedirectResponse("/student", status_code=303)


# -----------------------------
# Analytics Dashboard
# -----------------------------

@app.get("/analytics")
def analytics(request: Request, db: Session = Depends(get_db)):

    total_submissions = db.query(models.Submission).count()

    total_assignments = db.query(models.Assignment).count()

    pending = total_assignments - total_submissions

    prediction = predict_late(3)

    return templates.TemplateResponse(
        "analytics.html",
        {
            "request": request,
            "total": total_submissions,
            "pending": pending,
            "prediction": prediction
        }
    )


# -----------------------------
# Logout
# -----------------------------

@app.get("/logout")
def logout():
    return RedirectResponse("/", status_code=303)


# ============================================================
# TEACHER ADMIN CONTROL PANEL (NEW FEATURES)
# ============================================================

# Delete assignment
@app.get("/delete-assignment/{assignment_id}")
def delete_assignment(assignment_id: int, db: Session = Depends(get_db)):

    db.query(models.Assignment).filter(
        models.Assignment.id == assignment_id
    ).delete()

    db.commit()

    return RedirectResponse("/teacher", status_code=303)


# Edit assignment page
@app.get("/edit-assignment/{assignment_id}")
def edit_assignment_page(assignment_id: int, request: Request, db: Session = Depends(get_db)):

    assignment = db.query(models.Assignment).filter(
        models.Assignment.id == assignment_id
    ).first()

    return templates.TemplateResponse(
        "edit_assignment.html",
        {"request": request, "assignment": assignment}
    )


# Update assignment
@app.post("/update-assignment/{assignment_id}")
def update_assignment(
    assignment_id: int,
    title: str = Form(...),
    description: str = Form(...),
    deadline: str = Form(...),
    db: Session = Depends(get_db)
):

    assignment = db.query(models.Assignment).filter(
        models.Assignment.id == assignment_id
    ).first()

    assignment.title = title
    assignment.description = description
    assignment.deadline = deadline

    db.commit()

    return RedirectResponse("/teacher", status_code=303)


# View submissions
@app.get("/submissions/{assignment_id}")
def view_submissions(assignment_id: int, request: Request, db: Session = Depends(get_db)):

    submissions = db.query(models.Submission).filter(
        models.Submission.assignment_id == assignment_id
    ).all()

    return templates.TemplateResponse(
        "submissions.html",
        {
            "request": request,
            "submissions": submissions
        }
    )


# Download submitted file
from fastapi.responses import FileResponse

@app.get("/download/{submission_id}")
def download_file(submission_id: int, db: Session = Depends(get_db)):

    submission = db.query(models.Submission).filter(
        models.Submission.id == submission_id
    ).first()

    return FileResponse(submission.file_path)


# Grade submission
@app.post("/grade/{submission_id}")
def grade_submission(
    submission_id: int,
    grade: str = Form(...),
    db: Session = Depends(get_db)
):

    submission = db.query(models.Submission).filter(
        models.Submission.id == submission_id
    ).first()

    submission.grade = grade

    db.commit()

    return RedirectResponse("/teacher", status_code=303)