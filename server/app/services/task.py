from sqlmodel import select, Session
from app.schemas.app import User, Task, Email


def get_tasks_by_user(user: User, session: Session) -> list[Task]:
    all_tasks = session.exec(
        select(Task)
            .join(Email, Task.email_id == Email.email_id)
            .where(Email.user_id == user.user_id)
    ).all()
    return all_tasks