from datetime import datetime, timezone, timedelta
from Database.model import Chat, CompleteChat
from Data.chat import QuestionData, AnswerData
from Database.database import get_db
class TransactionService:
    def to_question_entity(question:QuestionData):
        return Chat(utterance=question.question, uid = question.uid, isuser=True, type="q")
    
    def to_answer_entity(answer:AnswerData):
        if answer.clarifying_questions is not None:
            return Chat(utterance=str(answer.clarifying_questions), uid = answer.uid, isuser=False, type="s")
        elif answer.answer is not None:
            return Chat(utterance=str(answer.answer), uid = answer.uid, isuser=False, type="a")
        
    def to_answer_entity_qa(answer:AnswerData):
        if answer.clarifying_questions is not None:
            return Chat(utterance=str(answer.clarifying_questions), uid = answer.uid, isuser=False, type="c")
    
    # def to_question_data(question:Chat):
    #     return QuestionData(uid=question.uid, utterance=question.utterance, created_at=question.created_at)
    
    def save_chat(question:Chat):
        with get_db() as db:
            try:
                db.add(question)
                db.commit()
            except Exception as e:
                db.rollback()
                raise e

    def get_chat_by_uid(uid:str):
        with get_db() as db:
            try:
                return db.query(Chat).filter(Chat.uid == uid).order_by(Chat.created_at.desc()).all()
            except Exception as e:
                raise e
