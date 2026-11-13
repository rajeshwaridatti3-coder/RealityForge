from pathlib import Path
from PIL import Image
import numpy as np,json

def read_model(folder):
 lines=(folder/'images.txt').read_text(errors='ignore').splitlines(); imgs=[]; i=0
 while i<len(lines):
  s=lines[i].strip(); i+=1
  if not s or s.startswith('#'): continue
  p=s.split()
  if len(p)<10: continue
  imgs.append({'q':list(map(float,p[1:5])),'t':list(map(float,p[5:8])),'cam':int(p[8]),'name':' '.join(p[9:])})
  if i<len(lines): i+=1
 cams={}
 for s in (folder/'cameras.txt').read_text(errors='ignore').splitlines():
  p=s.split()
  if len(p)>=5 and not p[0].startswith('#'): cams[int(p[0])]={'model':p[1],'params':list(map(float,p[4:]))}
 pts=[]
 for s in (folder/'points3D.txt').read_text(errors='ignore').splitlines():
  p=s.split()
  if len(p)>=8 and not p[0].startswith('#'): pts.append((int(p[0]),np.array(list(map(float,p[1:4]))),list(map(int,p[4:7]))))
 return imgs,cams,pts

def quat(q):
 w,x,y,z=q
 return np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])
def colorize(model,out,dets):
 try: imgs,cams,pts=read_model(model)
 except Exception as e: return {'available':False,'reason':str(e)}
 grouped={}
 for d in dets:
  if d.get('mask') and d.get('label'): grouped.setdefault(d['image'],[]).append(d)
 votes={}
 for im in imgs:
  cam=cams.get(im['cam']); name=Path(im['name']).name
  if not cam or name not in grouped: continue
  masks=[]
  for d in grouped[name]:
   f=out/d['mask']
   if f.exists(): masks.append((d['label'],np.asarray(Image.open(f).convert('L'))>0))
  if not masks: continue
  R=quat(im['q']); t=np.array(im['t']); pars=cam['params']; modelname=cam['model']
  if modelname in ('SIMPLE_PINHOLE','SIMPLE_RADIAL','RADIAL'): fx=fy=pars[0]; cx,cy=pars[1:3]
  else: fx,fy,cx,cy=pars[:4]
  for pid,xyz,rgb in pts:
   c=R@xyz+t
   if c[2]<=0: continue
   u=int(round(fx*c[0]/c[2]+cx)); v=int(round(fy*c[1]/c[2]+cy))
   for label,mask in masks:
    if 0<=v<mask.shape[0] and 0<=u<mask.shape[1] and mask[v,u]: votes.setdefault(pid,{}).setdefault(label,0); votes[pid][label]+=1
 labels=sorted({l for v in votes.values() for l in v}); palette=[(235,90,70),(70,170,235),(100,200,130),(220,170,60),(170,110,220),(60,200,190),(230,120,180)]; colors={l:palette[i%len(palette)] for i,l in enumerate(labels)}; counts={l:0 for l in labels}
 with (out/'semantic.ply').open('w') as f:
  f.write(f'ply\nformat ascii 1.0\nelement vertex {len(pts)}\nproperty float x\nproperty float y\nproperty float z\nproperty uchar red\nproperty uchar green\nproperty uchar blue\nend_header\n')
  for pid,xyz,rgb in pts:
   vote=votes.get(pid,{})
   if vote: label=max(vote,key=vote.get); rgb=colors[label]; counts[label]+=1
   f.write(f'{xyz[0]} {xyz[1]} {xyz[2]} {rgb[0]} {rgb[1]} {rgb[2]}\n')
 objects=[{'label':l,'color':list(colors[l]),'point_count':counts[l]} for l in labels]; (out/'objects.json').write_text(json.dumps(objects,indent=2))
 return {'available':True,'semantic_ply':'semantic.ply','objects_found':objects,'assigned_points':sum(counts.values())}
