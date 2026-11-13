from pathlib import Path
from datetime import datetime,timezone
import json,shutil,traceback
from ..db import SessionLocal
from ..models import Project,Job
from ..core.config import settings
from .upload import extract_video_frames
from .colmap import reconstruct,find_colmap,run
from .ai_pipeline import run_ai,AIUnavailable
from .semantic import colorize

def update(db,j,**kw):
 for k,v in kw.items(): setattr(j,k,v)
 j.updated_at=datetime.now(timezone.utc); db.commit()
def process_project(pid,jid,prompt):
 db=SessionLocal()
 try:
  p=db.query(Project).filter_by(id=pid).first(); j=db.query(Job).filter_by(id=jid).first()
  if not p or not j:return
  out=Path(p.output_dir); images=out/'images'; images.mkdir(parents=True,exist_ok=True); src=Path(p.source_dir)
  if p.input_type=='video': extract_video_frames(next(src.iterdir()),images,settings.video_frame_interval_sec)
  else:
   for f in src.iterdir():
    if f.suffix.lower() in {'.jpg','.jpeg','.png','.webp'}: shutil.copy2(f,images/f.name)
  if len(list(images.iterdir()))<2: raise RuntimeError('At least two usable images/frames are required.')
  update(db,j,status='running',stage='COLMAP reconstruction',progress=15,message='Extracting features, matching images and mapping sparse geometry')
  rec=reconstruct(images,out,settings.colmap_bin,settings.dense_reconstruction)
  txt=out/'sparse_text'; txt.mkdir(exist_ok=True); run([find_colmap(settings.colmap_bin),'model_converter','--input_path',rec['model_dir'],'--output_path',str(txt),'--output_type','TXT'])
  ai={'available':False,'reason':'ENABLE_AI is false'}; detections=[]
  update(db,j,stage='Grounding DINO + SAM',progress=65,message='Running optional pretrained detection and segmentation models')
  if settings.enable_ai:
   try: detections=run_ai(images,out,prompt,settings.grounding_dino_model,settings.sam_model,settings.ai_device); ai={'available':True,'detection_count':sum('box' in d for d in detections)}
   except AIUnavailable as e: ai={'available':False,'reason':str(e)}
  update(db,j,stage='2D-to-3D semantic projection',progress=88,message='Voting segmentation labels onto COLMAP 3D points')
  semantic=colorize(txt,out,detections) if detections else {'available':False,'reason':'No AI detections to project'}
  summary={'reconstruction':rec,'ai':ai,'semantic':semantic,'image_count':len(list(images.iterdir()))}
  (out/'summary.json').write_text(json.dumps(summary,indent=2,default=str)); p.status='completed'; update(db,j,status='completed',stage='Completed',progress=100,message='Processing completed; inspect generated scene artifacts')
 except Exception as e:
  j=db.query(Job).filter_by(id=jid).first(); p=db.query(Project).filter_by(id=pid).first()
  if p:p.status='failed'
  if j:update(db,j,status='failed',stage='Failed',message=str(e),error=traceback.format_exc()[-7000:])
 finally: db.close()
