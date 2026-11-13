from pathlib import Path
import subprocess,shutil
class ColmapError(RuntimeError): pass
def find_colmap(binary): return shutil.which(binary) or (str(Path(binary).resolve()) if Path(binary).exists() else None)
def run(args):
 p=subprocess.run(args,capture_output=True,text=True)
 if p.returncode: raise ColmapError((p.stderr or p.stdout)[-5000:])
 return p.stdout
def reconstruct(images,out,binary,dense=False):
 exe=find_colmap(binary)
 if not exe: raise ColmapError('COLMAP not found. Install COLMAP and add it to PATH.')
 out.mkdir(parents=True,exist_ok=True); db=out/'database.db'; sparse=out/'sparse'; sparse.mkdir(exist_ok=True)
 run([exe,'feature_extractor','--database_path',str(db),'--image_path',str(images),'--ImageReader.single_camera','1'])
 run([exe,'exhaustive_matcher','--database_path',str(db)])
 run([exe,'mapper','--database_path',str(db),'--image_path',str(images),'--output_path',str(sparse)])
 models=[p for p in sparse.iterdir() if p.is_dir()]
 if not models: raise ColmapError('No registered images. Use more sharp photos with stronger overlap and textured surfaces.')
 model=max(models,key=lambda p:len(list(p.iterdir()))); ply=out/'sparse.ply'
 run([exe,'model_converter','--input_path',str(model),'--output_path',str(ply),'--output_type','PLY'])
 result={'model_dir':str(model),'sparse_ply':str(ply),'dense':False}
 if dense:
  d=out/'dense'; d.mkdir(exist_ok=True)
  run([exe,'image_undistorter','--image_path',str(images),'--input_path',str(model),'--output_path',str(d),'--output_type','COLMAP'])
  run([exe,'patch_match_stereo','--workspace_path',str(d),'--workspace_format','COLMAP'])
  fused=d/'fused.ply'; run([exe,'stereo_fusion','--workspace_path',str(d),'--workspace_format','COLMAP','--input_type','geometric','--output_path',str(fused)])
  result.update(dense=True,dense_ply=str(fused))
 return result
