from pathlib import Path
from PIL import Image
import torch,json
class AIUnavailable(RuntimeError): pass
class VisionModels:
 def __init__(self,dino_id,sam_id,device_setting='auto'):
  try: from transformers import AutoProcessor,AutoModelForZeroShotObjectDetection,SamProcessor,SamModel
  except Exception as e: raise AIUnavailable('Install requirements-ai.txt and a compatible PyTorch build to enable Grounding DINO + SAM.') from e
  self.device=('cuda' if torch.cuda.is_available() else 'cpu') if device_setting=='auto' else device_setting
  self.dp=AutoProcessor.from_pretrained(dino_id); self.dino=AutoModelForZeroShotObjectDetection.from_pretrained(dino_id).to(self.device).eval()
  self.sp=SamProcessor.from_pretrained(sam_id); self.sam=SamModel.from_pretrained(sam_id).to(self.device).eval()
 @torch.inference_mode()
 def run_image(self,path,prompt,outdir):
  image=Image.open(path).convert('RGB'); inp=self.dp(images=image,text=prompt,return_tensors='pt').to(self.device); outputs=self.dino(**inp)
  result=self.dp.post_process_grounded_object_detection(outputs,inp.input_ids,box_threshold=.30,text_threshold=.25,target_sizes=[image.size[::-1]])[0]
  boxes=result['boxes'].detach().cpu(); scores=result['scores'].detach().cpu(); labels=result['labels']; records=[]
  if len(boxes):
   si=self.sp(images=image,input_boxes=[boxes.tolist()],return_tensors='pt').to(self.device); so=self.sam(**si)
   masks=self.sp.image_processor.post_process_masks(so.pred_masks.detach().cpu(),si['original_sizes'].cpu(),si['reshaped_input_sizes'].cpu())[0]
   for i,(box,score,label) in enumerate(zip(boxes,scores,labels)):
    mask=masks[0,i].numpy().astype('uint8'); mp=outdir/'masks'/f'{path.stem}_{i}.png'; mp.parent.mkdir(parents=True,exist_ok=True); Image.fromarray(mask*255).save(mp)
    records.append({'label':str(label),'score':float(score),'box':[float(x) for x in box.tolist()],'mask':str(mp.relative_to(outdir)),'image':path.name})
  return records
def run_ai(images,out,prompt,dino,sam,device):
 model=VisionModels(dino,sam,device); records=[]
 for p in sorted(images.iterdir()):
  if p.suffix.lower() in {'.jpg','.jpeg','.png','.webp'}:
   try: records.extend(model.run_image(p,prompt,out))
   except Exception as e: records.append({'image':p.name,'error':str(e)})
 (out/'detections.json').write_text(json.dumps(records,indent=2),encoding='utf-8'); return records
