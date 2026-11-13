from pathlib import Path
from fastapi import HTTPException
from PIL import Image
import cv2,uuid
IMG={'.jpg','.jpeg','.png','.webp'}; VID={'.mp4','.mov','.avi','.mkv','.webm'}
async def save_uploads(files,dest,max_bytes):
 dest.mkdir(parents=True,exist_ok=True); kinds=set()
 for f in files:
  name=Path(f.filename or '').name; ext=Path(name).suffix.lower()
  if ext not in IMG|VID: raise HTTPException(400,f'Unsupported file type: {name}')
  target=dest/(uuid.uuid4().hex+'_'+name); size=0
  with target.open('wb') as out:
   while chunk:=await f.read(1024*1024):
    size+=len(chunk)
    if size>max_bytes: target.unlink(missing_ok=True); raise HTTPException(413,f'{name} exceeds upload size limit')
    out.write(chunk)
  if ext in IMG:
   try:
    with Image.open(target) as im: im.verify()
   except Exception: target.unlink(missing_ok=True); raise HTTPException(400,f'Invalid image: {name}')
   kinds.add('images')
  else: kinds.add('video')
 if len(kinds)!=1: raise HTTPException(400,'Upload either one or more images OR one video, not a mixture')
 return kinds.pop()
def extract_video_frames(video,out,interval):
 cap=cv2.VideoCapture(str(video))
 if not cap.isOpened(): raise RuntimeError('Could not open uploaded video')
 fps=cap.get(cv2.CAP_PROP_FPS) or 25; step=max(1,int(fps*interval)); out.mkdir(parents=True,exist_ok=True); i=n=0
 while True:
  ok,frame=cap.read()
  if not ok: break
  if i%step==0:
   h,w=frame.shape[:2]; scale=min(1,2400/max(h,w))
   if scale<1: frame=cv2.resize(frame,(int(w*scale),int(h*scale)))
   cv2.imwrite(str(out/f'frame_{n:05d}.jpg'),frame); n+=1
  i+=1
 cap.release()
 if n<2: raise RuntimeError('Video produced fewer than two frames')
 return n
