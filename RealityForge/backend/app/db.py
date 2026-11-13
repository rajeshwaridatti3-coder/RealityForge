from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base,sessionmaker
from pathlib import Path
from .core.config import settings
url=settings.database_url
if url.startswith('sqlite:///'):
 p=Path(url.replace('sqlite:///','',1)); p=p if p.is_absolute() else (Path(__file__).resolve().parents[2]/p).resolve(); p.parent.mkdir(parents=True,exist_ok=True); url='sqlite:///'+p.as_posix()
engine=create_engine(url,connect_args={'check_same_thread':False} if url.startswith('sqlite') else {})
SessionLocal=sessionmaker(bind=engine,autoflush=False,autocommit=False); Base=declarative_base()
def get_db():
 db=SessionLocal()
 try: yield db
 finally: db.close()
