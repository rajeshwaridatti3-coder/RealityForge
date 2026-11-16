# RealityForge
### AI-Powered 3D Scene Reconstruction

RealityForge is a computer-vision-based project that explores converting image and video inputs into navigable 3D scene representations. It combines 3D reconstruction techniques with AI-powered object detection and segmentation to support scene understanding and interactive visualization.

The project aims to connect computer vision, deep learning, and 3D visualization in one workflow.

## 🎯 Project Overview

Reconstructing a 3D environment from ordinary images or videos involves understanding scene geometry, identifying objects, and representing the environment in a form that can be explored interactively.

RealityForge explores this process through:

- **3D Reconstruction:** Using COLMAP to support scene reconstruction from visual inputs.
- **Object Detection:** Applying Grounding DINO to identify objects in images.
- **Image Segmentation:** Using Segment Anything Model (SAM) for object-level segmentation.
- **Deep Learning:** Leveraging PyTorch for computer-vision model integration.
- **3D Visualization:** Using Three.js to create an interactive environment for exploring reconstructed scenes.
- **Backend Services:** Using FastAPI to support communication between processing components and the application.

## ✨ Key Components

| Component | Purpose |
|---|---|
| COLMAP | Structure-from-Motion and 3D reconstruction |
| Grounding DINO | Text-prompt-based object detection |
| SAM | Object segmentation |
| PyTorch | Deep-learning framework |
| FastAPI | Backend API development |
| React | Frontend application |
| Three.js | Interactive 3D visualization |

## 🔄 High-Level Workflow

The intended workflow connects the following stages:

1. **Input Processing** – Provide images or video frames as visual input.
2. **Scene Reconstruction** – Use COLMAP-based reconstruction techniques to estimate scene structure.
3. **Object Detection** – Identify objects using Grounding DINO.
4. **Object Segmentation** – Generate object-level masks using SAM.
5. **Backend Integration** – Organize processing and application communication through FastAPI.
6. **3D Visualization** – Present scene representations through a React interface with Three.js.

## 🛠️ Technology Stack

**Programming Language:** Python, JavaScript

**AI & Computer Vision:** PyTorch, Grounding DINO, Segment Anything Model (SAM)

**3D Reconstruction:** COLMAP

**Backend:** FastAPI

**Frontend:** React.js

**3D Rendering:** Three.js

## 🏗️ Architecture

RealityForge is organized around three major application layers:

- **Computer Vision Layer:** Handles reconstruction, object detection, and segmentation components.
- **Backend Layer:** Provides API communication and connects processing components with the application.
- **Visualization Layer:** Uses React and Three.js to support interactive 3D scene exploration.

## 🎓 Learning Outcomes

Working on RealityForge involves exploring:

- Structure-from-Motion and 3D scene reconstruction.
- Deep-learning-based object detection and segmentation.
- Integration of multiple computer-vision technologies.
- Python backend development using FastAPI.
- Interactive 3D visualization using Three.js.
- Connecting AI processing components with web applications.

## 🚀 Project Goal

The long-term goal of RealityForge is to develop an interactive platform that transforms visual inputs into meaningful 3D scene representations, making scene inspection and object-level exploration easier.

## 👩‍💻 Author

**Rajeshwari Datti**

Computer Science and Engineering  
National Institute of Technology, Patna

## 📌 Project Status

Development in progress. The project explores an integrated computer-vision and 3D visualization workflow; individual components and end-to-end functionality should be validated as implementation progresses.

