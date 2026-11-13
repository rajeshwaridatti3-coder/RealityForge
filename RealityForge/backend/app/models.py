from sqlalchemy import Column,String,DateTime,Text,Float,ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime,timezone
from .db import Base
class Project(Base):
 __tablename__='projects'
 id=Column(String,primary_key=True); name=Column(String(160),nullable=False); status=Column(String(30),default='uploaded'); input_type=Column(String(20)); source_dir=Column(Text); output_dir=Column(Text); created_at=Column(DateTime,default=lambda:datetime.now(timezone.utc)); jobs=relationship('Job',back_populates='project',cascade='all, delete-orphan')
class Job(Base):
 __tablename__='jobs'
 id=Column(String,primary_key=True); project_id=Column(String,ForeignKey('projects.id')); status=Column(String(30),default='queued'); stage=Column(String(100),default='Queued'); progress=Column(Float,default=0); message=Column(Text,default=''); error=Column(Text,default=''); updated_at=Column(DateTime,default=lambda:datetime.now(timezone.utc)); project=relationship('Project',back_populates='jobs')
