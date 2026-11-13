from fastapi import FastAPI,UploadFile,File,Form,Depends,HTTPException,BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pathlib import Path,PurePosixPath
import uuid,json,shutil
from .core.config import settings
from .db import Base,engine,get_db
from .models import Project,Job
from .schemas import ProjectOut,JobOut
from .services.upload import save_uploads
from .services.pipeline import process_project
from .services.colmap import find_colmap
Base.metadata.create_all(bind=engine)
app=FastAPI(title='RealityForge API',version='1.0.0',description='AI-powered image/video to semantic 3D reconstruction')
app.add_middleware(CORSMiddleware,allow_origins=settings.origins,allow_credentials=True,allow_methods=['*'],allow_headers=['*'])
@app.get('/health')
def health(): return {'status':'ok','colmap_available':bool(find_colmap(settings.colmap_bin)),'ai_enabled':settings.enable_ai}
@app.get('/api/projects',response_model=list[ProjectOut])
def projects(db:Session=Depends(get_db)): return db.query(Project).order_by(Project.created_at.desc()).all()
@app.post('/api/projects',response_model=ProjectOut)
async def create(name:str=Form(...),files:list[UploadFile]=File(...),db:Session=Depends(get_db)):
 name=name.strip()[:160]
 if not name: raise HTTPException(400,'Project name required')
 pid=str(uuid.uuid4()); base=settings.data_path/'projects'/pid; src=base/'uploads'; out=base/'outputs'
 kind=await save_uploads(files,src,settings.max_upload_mb*1024*1024); out.mkdir(parents=True,exist_ok=True)
 p=Project(id=pid,name=name,status='uploaded',input_type=kind,source_dir=str(src),output_dir=str(out)); db.add(p); db.commit(); db.refresh(p); return p
@app.get('/api/projects/{pid}',response_model=ProjectOut)
def project(pid:str,db:Session=Depends(get_db)):
 p=db.query(Project).filter_by(id=pid).first()
 if not p: raise HTTPException(404,'Project not found')
 return p
@app.post('/api/projects/{pid}/process',response_model=JobOut)
def process(pid:str,bg:BackgroundTasks,prompt:str=Form('chair . table . sofa . person . door . window'),db:Session=Depends(get_db)):
 p=db.query(Project).filter_by(id=pid).first()
 if not p: raise HTTPException(404,'Project not found')
 active=db.query(Job).filter(Job.project_id==pid,Job.status.in_(['queued','running'])).first()
 if active: raise HTTPException(409,'A job is already running')
 j=Job(id=str(uuid.uuid4()),project_id=pid,status='queued',stage='Queued',progress=0,message='Waiting to start'); p.status='processing'; db.add(j); db.commit(); db.refresh(j); bg.add_task(process_project,pid,j.id,prompt); return j
@app.get('/api/jobs/{jid}',response_model=JobOut)
def job(jid:str,db:Session=Depends(get_db)):
 j=db.query(Job).filter_by(id=jid).first()
 if not j: raise HTTPException(404,'Job not found')
 return j
@app.get('/api/projects/{pid}/summary')
def summary(pid:str,db:Session=Depends(get_db)):
 p=db.query(Project).filter_by(id=pid).first()
 if not p: raise HTTPException(404,'Project not found')
 f=Path(p.output_dir)/'summary.json'
 if not f.exists(): return {'ready':False}
 data=json.loads(f.read_text()); det=Path(p.output_dir)/'detections.json'; data['detections']=json.loads(det.read_text()) if det.exists() else []; return {'ready':True,**data}
@app.get('/api/projects/{pid}/assets/{asset:path}')
def asset(pid:str,asset:str,db:Session=Depends(get_db)):
 p=db.query(Project).filter_by(id=pid).first()
 if not p: raise HTTPException(404,'Project not found')
 base=Path(p.output_dir).resolve(); target=(base/PurePosixPath(asset)).resolve()
 if base not in target.parents or not target.is_file(): raise HTTPException(404,'Asset not found')
 return FileResponse(target)
@app.delete('/api/projects/{pid}')
def delete(pid:str,db:Session=Depends(get_db)):
 p=db.query(Project).filter_by(id=pid).first()
 if not p: raise HTTPException(404,'Project not found')
 shutil.rmtree(Path(p.source_dir).parent,ignore_errors=True); db.delete(p); db.commit(); return {'deleted':True}
