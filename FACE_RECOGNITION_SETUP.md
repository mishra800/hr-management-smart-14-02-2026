# Face Recognition Setup Guide

## Current Status

Face recognition is **disabled by default** to avoid complex build dependencies. The app works perfectly without it.

## Why Disabled?

The `face-recognition` library requires `dlib`, which:
- Needs CMake 3.5+ and C++ compiler
- Takes 5-10 minutes to build
- Has compatibility issues with newer Python
- Adds 500MB+ to Docker image

## How It Works Without Face Recognition

The app gracefully handles this:
- ✅ Attendance marking with photo capture works
- ✅ All HR features work normally
- ❌ Face verification is skipped (not critical)

## Deployment Options

### Option 1: Without Face Recognition (Recommended)

```bash
docker-compose up -d
```

Uses `requirements.txt` - fast, reliable, no issues.

### Option 2: With DeepFace (Easier Alternative)

Add to `requirements_full.txt`:
```txt
numpy==1.26.4
opencv-python-headless==4.10.0.84
tensorflow==2.15.0
deepface==0.0.93
```

Update `face_recognition_utils.py`:
```python
from deepface import DeepFace
```

Build:
```bash
docker build -f backend/Dockerfile.full -t hr-backend-full .
```

### Option 3: Original face-recognition (Not Recommended)

Requires significant build time and resources. Only use if absolutely necessary.

Add to `requirements_full.txt`:
```txt
cmake==3.28.0
dlib==19.24.6
face-recognition==1.3.0
numpy==1.26.4
opencv-python-headless==4.10.0.84
```

Update Dockerfile.full with boost libraries:
```dockerfile
RUN apt-get install -y libboost-all-dev
```

Build time: 15-20 minutes, requires 4GB+ RAM.

## Recommendation

Use **Option 1** for production. Face recognition is not critical for HR operations - photo capture provides sufficient verification.
