from pydantic import BaseModel

class AssignmentCreate(BaseModel):
    title: str
    description: str
    deadline: str

class SubmissionCreate(BaseModel):
    student_name: str
    assignment_id: int