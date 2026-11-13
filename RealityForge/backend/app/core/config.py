from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    data_dir:str='../data'; database_url:str='sqlite:///../data/realityforge.db'
    cors_origins:str='http://localhost:5173,http://127.0.0.1:5173'
    max_upload_mb:int=500; video_frame_interval_sec:float=1.5; colmap_bin:str='colmap'
    enable_ai:bool=False; grounding_dino_model:str='IDEA-Research/grounding-dino-tiny'
    sam_model:str='facebook/sam-vit-base'; ai_device:str='auto'; dense_reconstruction:bool=False
    model_config=SettingsConfigDict(env_file='.env',extra='ignore')
    @property
    def data_path(self):
        p=Path(self.data_dir); p=p if p.is_absolute() else (Path(__file__).resolve().parents[3]/p).resolve(); p.mkdir(parents=True,exist_ok=True); return p
    @property
    def origins(self): return [x.strip() for x in self.cors_origins.split(',') if x.strip()]
settings=Settings()
