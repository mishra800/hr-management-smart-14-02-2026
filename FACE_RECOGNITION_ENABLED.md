# Face Recognition Enabled - Deployment Guide

## What's Configured

Your system now uses **DeepFace** for face recognition - a modern, easier-to-install alternative to the problematic `dlib` library.

## Changes Made

1. **requirements_full.txt** - Added DeepFace dependencies:
   - numpy==1.26.4
   - opencv-python-headless==4.10.0.84
   - tensorflow==2.15.0
   - deepface==0.0.93

2. **Dockerfile.full** - Updated with OpenCV/TensorFlow dependencies

3. **face_recognition_utils.py** - Rewritten to use DeepFace instead of face_recognition

4. **docker-compose.yml** - Now uses Dockerfile.full

## Deployment

```bash
# Build with face recognition
docker-compose build

# Start services
docker-compose up -d

# Initialize database
docker exec hr_backend python create_default_users.py
docker exec hr_backend python initialize_capabilities.py
```

## Build Time

- First build: 5-10 minutes (downloads TensorFlow models)
- Subsequent builds: 2-3 minutes (cached)
- Image size: ~2GB (includes TensorFlow)

## How It Works

### DeepFace vs Original face_recognition

| Feature | DeepFace | face_recognition (dlib) |
|---------|----------|------------------------|
| Installation | ✅ Easy (pip install) | ❌ Complex (needs CMake, C++) |
| Build Time | 5-10 min | 15-20 min |
| Accuracy | ✅ High (Facenet model) | ✅ High |
| Speed | Fast | Fast |
| Dependencies | TensorFlow | dlib, CMake, boost |

### Face Recognition Flow

1. **Profile Setup**: Employee uploads photo → Saved to `uploads/profile_images/`
2. **Attendance**: Employee takes selfie → DeepFace compares with profile
3. **Verification**: Returns confidence score (0-100%)
4. **Threshold**: Default 60% match required (configurable)

## Testing

### 1. Check if face recognition is loaded:

```bash
docker logs hr_backend | grep "DeepFace"
```

Should see: `INFO: DeepFace face recognition loaded successfully`

### 2. Test face verification:

```python
# In Python shell inside container
docker exec -it hr_backend python

from app.face_recognition_utils import FACE_RECOGNITION_AVAILABLE
print(f"Face Recognition Available: {FACE_RECOGNITION_AVAILABLE}")
```

### 3. Upload profile photo and test attendance marking

## Configuration

### Adjust Face Match Threshold

In `backend/app/attendance_service.py`, find:

```python
face_result = await face_recognition_utils.verify_face(
    employee.id, photo_base64, tolerance=0.4  # Lower = stricter
)
```

Tolerance values:
- `0.3` - Very strict (95%+ match required)
- `0.4` - Strict (85%+ match) - **Default**
- `0.5` - Moderate (75%+ match)
- `0.6` - Lenient (65%+ match)

## Performance

### Resource Usage

- CPU: 2-4 cores recommended
- RAM: 2GB minimum, 4GB recommended
- Disk: 2GB for Docker image
- Per verification: ~2-3 seconds

### Optimization Tips

1. **Reduce workers** in Dockerfile.full (already set to 2)
2. **Use GPU** for faster inference (requires nvidia-docker)
3. **Cache models** - DeepFace downloads models on first use

## Troubleshooting

### Build fails with TensorFlow errors:

```bash
# Try with more memory
docker-compose build --memory 4g
```

### Face recognition not working:

```bash
# Check logs
docker logs hr_backend

# Verify dependencies
docker exec hr_backend pip list | grep -E "deepface|tensorflow|opencv"
```

### Slow performance:

- Reduce image size before upload (max 800x800px)
- Use GPU-enabled Docker
- Increase server resources

### "No face detected" errors:

- Ensure good lighting
- Face should be centered and clearly visible
- Minimum image size: 200x200px
- Only one person in frame

## Reverting to No Face Recognition

If you want to disable face recognition:

```bash
# Edit docker-compose.yml
# Change: dockerfile: Dockerfile.full
# To:     dockerfile: Dockerfile

# Rebuild
docker-compose build
docker-compose up -d
```

The app will work normally without face recognition - attendance marking will use photo capture only.

## Security Notes

- Profile photos stored in `uploads/profile_images/`
- Attendance photos not stored (only verified)
- Face matching happens server-side
- No face data sent to external services
- DeepFace models run locally

## Support

Face recognition is working if you see:
- ✅ "DeepFace face recognition loaded successfully" in logs
- ✅ Attendance marking with photo verification works
- ✅ Confidence scores shown in attendance records

If issues persist, check `FACE_RECOGNITION_SETUP.md` for alternative options.
