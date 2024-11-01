from pydantic import BaseModel

class QuestionData(BaseModel):
    uid: str
    question: str
    sessionId: str
    
class QuestionDataServer(BaseModel):
    uid: str
    question: str
    created_at: str

class AnswerData(BaseModel):
    sessionId: str
    uid: str
    answer: str = None
    status_code: int
    clarifying_questions: list = None

class AnswerDataServer(BaseModel):
    uid: str
    answer: str
    created_at: str