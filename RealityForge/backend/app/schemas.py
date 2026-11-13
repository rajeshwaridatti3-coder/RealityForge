from pydantic import BaseModel
from datetime import datetime
class ProjectOut(BaseModel):
 id:str; name:str; status:str; input_type:str; created_at:datetime
 class Config: from_attributes=True
class JobOut(BaseModel):
 id:str; project_id:str; status:str; stage:str; progress:float; message:str; error:str; updated_at:datetime
 class Config: from_attributes=True
