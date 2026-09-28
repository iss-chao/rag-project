from pydantic import BaseModel

class TaskEvent(BaseModel):
    kb_id: int
    task_id: int
    type: str
    status: str
    msg: str