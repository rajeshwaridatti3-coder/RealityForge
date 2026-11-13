# RealityForge — AI-Powered 3D Scene Reconstruction

A full-stack computer-vision application for image/video ingestion, COLMAP sparse 3D reconstruction, Grounding DINO object detection, Segment Anything masks, 2D-to-3D semantic point voting, and a React/Three.js point-cloud viewer.

## Included capabilities
- React/Vite dashboard, project creation, uploads, job progress, artifacts and viewer.
- FastAPI API, SQLite persistence, file validation, video frame extraction and background processing.
- COLMAP feature extraction, exhaustive matching, mapping and PLY export; optional dense reconstruction.
- Optional pretrained Grounding DINO + SAM inference using Hugging Face Transformers.
- COLMAP camera/point text parsing and projection of 2D segmentation masks onto 3D points to create `semantic.ply` and `objects.json`.
- Docker starter, configuration examples and setup instructions.

## Important deployment truth
This is application source code, not a bundle of multi-gigabyte pretrained model weights or the COLMAP executable. Install COLMAP on the backend host. AI inference requires a compatible PyTorch build and `backend/requirements-ai.txt`; set `ENABLE_AI=true`. Model weights download on first run. COLMAP and transformer inference need significant CPU/RAM/GPU resources; many free web hosts are unsuitable. Dense reconstruction is disabled by default. Validate all five features on your own sample data before listing them as completed on a resume.

## Requirements
Python 3.10/3.11, Node.js 20+, npm, COLMAP available on PATH. AI: PyTorch matching your machine plus optional requirements.

## Windows PowerShell
Backend terminal:
```powershell
cd RealityForge
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backendequirements.txt
Copy-Item backend\.env.example backend\.env
# Install COLMAP separately and ensure `colmap -h` works
uvicorn backend.app.main:app --reload --port 8000
```
Frontend terminal:
```powershell
cd RealityForgerontend
npm install
Copy-Item .env.example .env
npm run dev
```
Open http://localhost:5173 and API docs at http://127.0.0.1:8000/docs.

Enable AI:
```powershell
# First install a suitable PyTorch build from https://pytorch.org/get-started/locally/
pip install -r backendequirements-ai.txt
# Edit backend/.env: ENABLE_AI=true
```

## Input guidance
Use 30–100 sharp, well-lit photos with 60–80% overlap, taken around a static scene. Start with sparse reconstruction. Video is sampled at the configured interval. Avoid reflective objects, moving subjects, blur and blank walls.

## API
`POST /api/projects` (multipart name + files), `POST /api/projects/{id}/process` (prompt), `GET /api/jobs/{id}`, `GET /api/projects`, `GET /api/projects/{id}/summary`, `GET /api/projects/{id}/assets/{path}`, `GET /health`.

## Resume verification checklist
1. Confirm COLMAP outputs a real sparse point cloud.
2. Confirm Grounding DINO detects objects from your prompt.
3. Confirm SAM produces mask images.
4. Confirm semantic PLY receives mask-voted point colors.
5. Confirm the Three.js viewer loads and orbits the real PLY.
6. Record registered image count, point count, processing time and sample results.

## Known practical limits
The backend uses FastAPI BackgroundTasks, suitable for a local demo/single worker. For production, move long jobs to a dedicated queue/worker (Celery/RQ), add authentication, persistent object storage, quotas and observability. The demo is not a multi-tenant secure production service.
