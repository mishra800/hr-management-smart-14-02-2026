"""
Face Recognition Utilities for Attendance System
Uses DeepFace library for face matching (easier alternative to dlib)
"""
try:
    from deepface import DeepFace
    import cv2
    FACE_RECOGNITION_AVAILABLE = True
    print("INFO: DeepFace face recognition loaded successfully")
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False
    print("WARNING: DeepFace library not installed. Face recognition features will be disabled.")
    print("To enable face recognition, run: pip install deepface tensorflow opencv-python-headless")

import numpy as np
import base64
from io import BytesIO
from PIL import Image
import os
import tempfile

def decode_base64_image(base64_string):
    """Decode base64 image string to numpy array"""
    try:
        # Remove data URL prefix if present
        if ',' in base64_string:
            base64_string = base64_string.split(',')[1]
        
        image_data = base64.b64decode(base64_string)
        image = Image.open(BytesIO(image_data))
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        return np.array(image)
    except Exception as e:
        print(f"Error decoding image: {e}")
        return None

def save_temp_image(image_array):
    """Save numpy array as temporary image file for DeepFace"""
    try:
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
        image = Image.fromarray(image_array)
        image.save(temp_file.name)
        return temp_file.name
    except Exception as e:
        print(f"Error saving temp image: {e}")
        return None

def detect_image_quality(image_array):
    """Analyze image quality for face recognition"""
    try:
        if not FACE_RECOGNITION_AVAILABLE:
            return {"quality_score": 50, "acceptable": True, "issues": []}
        
        # Convert to grayscale for analysis
        if len(image_array.shape) == 3:
            gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = image_array
        
        height, width = gray.shape
        brightness = np.mean(gray)
        contrast = np.std(gray)
        blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        quality_issues = []
        quality_score = 100
        
        if brightness < 50:
            quality_issues.append("Image too dark")
            quality_score -= 20
        elif brightness > 200:
            quality_issues.append("Image too bright")
            quality_score -= 15
        
        if contrast < 30:
            quality_issues.append("Low contrast")
            quality_score -= 15
        
        if blur_score < 100:
            quality_issues.append("Image appears blurry")
            quality_score -= 25
        
        if min(height, width) < 200:
            quality_issues.append("Image too small")
            quality_score -= 30
        
        return {
            "quality_score": max(0, quality_score),
            "brightness": round(brightness, 2),
            "contrast": round(contrast, 2),
            "blur_score": round(blur_score, 2),
            "size": f"{width}x{height}",
            "issues": quality_issues,
            "acceptable": quality_score >= 60
        }
    except Exception as e:
        return {
            "quality_score": 50,
            "issues": [f"Quality analysis failed: {str(e)}"],
            "acceptable": True
        }

def compare_faces(profile_image_base64, attendance_image_base64, tolerance=0.4):
    """
    Compare two face images using DeepFace
    
    Args:
        profile_image_base64: Base64 encoded profile image
        attendance_image_base64: Base64 encoded attendance image
        tolerance: Distance threshold (lower = stricter, default 0.4 for cosine)
    
    Returns:
        dict with match result and analysis
    """
    if not FACE_RECOGNITION_AVAILABLE:
        return {
            "match": False,
            "confidence": 0,
            "message": "Face recognition library not installed",
            "security_analysis": {
                "quality_check": {"acceptable": False},
                "liveness_check": {"is_likely_live": False}
            }
        }
    
    temp_files = []
    try:
        # Decode images
        profile_image = decode_base64_image(profile_image_base64)
        attendance_image = decode_base64_image(attendance_image_base64)
        
        if profile_image is None or attendance_image is None:
            return {
                "match": False,
                "confidence": 0,
                "message": "Failed to decode images",
                "security_analysis": {"quality_check": {"acceptable": False}}
            }
        
        # Quality analysis
        quality_analysis = detect_image_quality(attendance_image)
        
        if not quality_analysis["acceptable"]:
            return {
                "match": False,
                "confidence": 0,
                "message": f"Image quality too low: {', '.join(quality_analysis['issues'])}",
                "security_analysis": {"quality_check": quality_analysis}
            }
        
        # Save as temp files for DeepFace
        profile_path = save_temp_image(profile_image)
        attendance_path = save_temp_image(attendance_image)
        temp_files = [profile_path, attendance_path]
        
        if not profile_path or not attendance_path:
            return {
                "match": False,
                "confidence": 0,
                "message": "Failed to process images",
                "security_analysis": {"quality_check": quality_analysis}
            }
        
        # Verify faces using DeepFace
        result = DeepFace.verify(
            img1_path=profile_path,
            img2_path=attendance_path,
            model_name='Facenet',  # Fast and accurate
            distance_metric='cosine',
            enforce_detection=True
        )
        
        # Calculate confidence (inverse of distance)
        distance = result['distance']
        confidence = max(0, min(100, (1 - distance) * 100))
        match = result['verified']
        
        # Adjust based on quality
        if quality_analysis["quality_score"] < 80:
            confidence *= 0.9
        
        message = "Face matched successfully" if match else "Face does not match profile"
        
        return {
            "match": match,
            "confidence": round(confidence, 2),
            "message": message,
            "face_distance": round(distance, 4),
            "security_analysis": {
                "quality_check": quality_analysis,
                "model_used": "Facenet",
                "threshold": tolerance
            }
        }
        
    except ValueError as e:
        # Face not detected
        return {
            "match": False,
            "confidence": 0,
            "message": f"Face detection failed: {str(e)}",
            "security_analysis": {"quality_check": {"acceptable": False}}
        }
    except Exception as e:
        return {
            "match": False,
            "confidence": 0,
            "message": f"Face recognition error: {str(e)}",
            "security_analysis": {"quality_check": {"acceptable": False}}
        }
    finally:
        # Cleanup temp files
        for temp_file in temp_files:
            if temp_file and os.path.exists(temp_file):
                try:
                    os.unlink(temp_file)
                except:
                    pass

def save_profile_image(employee_id, image_base64):
    """Save employee profile image for future face matching"""
    try:
        upload_dir = "uploads/profile_images"
        os.makedirs(upload_dir, exist_ok=True)
        
        if ',' in image_base64:
            image_base64 = image_base64.split(',')[1]
        
        image_data = base64.b64decode(image_base64)
        file_path = os.path.join(upload_dir, f"employee_{employee_id}.jpg")
        
        with open(file_path, 'wb') as f:
            f.write(image_data)
        
        return file_path
    except Exception as e:
        print(f"Error saving profile image: {e}")
        return None

def load_profile_image(employee_id):
    """Load employee profile image as base64"""
    try:
        file_path = f"uploads/profile_images/employee_{employee_id}.jpg"
        
        if not os.path.exists(file_path):
            return None
        
        with open(file_path, 'rb') as f:
            image_data = f.read()
            return base64.b64encode(image_data).decode('utf-8')
    except Exception as e:
        print(f"Error loading profile image: {e}")
        return None

async def verify_face(employee_id, attendance_image_base64, tolerance=0.4):
    """
    Verify face against stored profile image
    
    Args:
        employee_id: Employee ID to verify against
        attendance_image_base64: Base64 encoded attendance image
        tolerance: Face matching tolerance (lower = stricter, default 0.4)
    
    Returns:
        dict with verification result
    """
    if not FACE_RECOGNITION_AVAILABLE:
        return {
            "success": False,
            "error": "face_recognition_unavailable",
            "message": "Face recognition library not installed",
            "confidence": 0
        }
    
    try:
        profile_image_base64 = load_profile_image(employee_id)
        
        if not profile_image_base64:
            return {
                "success": False,
                "error": "no_profile_image",
                "message": "No profile image found for employee",
                "confidence": 0
            }
        
        result = compare_faces(profile_image_base64, attendance_image_base64, tolerance)
        
        if result["match"]:
            return {
                "success": True,
                "message": "Face verification successful",
                "confidence": result["confidence"],
                "face_distance": result.get("face_distance", 0),
                "security_analysis": result.get("security_analysis", {})
            }
        else:
            return {
                "success": False,
                "error": "face_mismatch",
                "message": result["message"],
                "confidence": result["confidence"],
                "face_distance": result.get("face_distance", 1),
                "security_analysis": result.get("security_analysis", {})
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": "verification_failed",
            "message": f"Face verification failed: {str(e)}",
            "confidence": 0
        }

def validate_profile_image(image_base64):
    """
    Validate profile image quality and suitability for face recognition
    
    Args:
        image_base64: Base64 encoded image
    
    Returns:
        dict with validation result and recommendations
    """
    if not FACE_RECOGNITION_AVAILABLE:
        return {
            "valid": False,
            "message": "Face recognition library not installed",
            "recommendations": ["Install face recognition dependencies"]
        }
    
    temp_file = None
    try:
        image_array = decode_base64_image(image_base64)
        if image_array is None:
            return {
                "valid": False,
                "message": "Failed to decode image",
                "recommendations": ["Use a valid image format (JPEG, PNG)"]
            }
        
        quality_analysis = detect_image_quality(image_array)
        
        # Try to detect face
        temp_file = save_temp_image(image_array)
        face_detected = False
        face_error = None
        
        try:
            DeepFace.extract_faces(img_path=temp_file, enforce_detection=True)
            face_detected = True
        except Exception as e:
            face_error = str(e)
        
        recommendations = []
        issues = []
        
        if not quality_analysis["acceptable"]:
            issues.extend(quality_analysis["issues"])
            if quality_analysis["brightness"] < 50:
                recommendations.append("Take photo in better lighting")
            elif quality_analysis["brightness"] > 200:
                recommendations.append("Reduce lighting or avoid direct flash")
            if quality_analysis["blur_score"] < 100:
                recommendations.append("Hold camera steady and ensure focus")
        
        if not face_detected:
            issues.append("No face detected" if "detect" in str(face_error).lower() else "Face detection failed")
            recommendations.append("Ensure your face is clearly visible and centered")
        
        is_valid = len(issues) == 0 and quality_analysis["acceptable"] and face_detected
        message = "Profile image is suitable for face recognition" if is_valid else f"Image validation failed: {', '.join(issues)}"
        
        return {
            "valid": is_valid,
            "message": message,
            "quality_score": quality_analysis["quality_score"],
            "face_detected": face_detected,
            "issues": issues,
            "recommendations": recommendations,
            "quality_details": quality_analysis
        }
        
    except Exception as e:
        return {
            "valid": False,
            "message": f"Validation error: {str(e)}",
            "recommendations": ["Try uploading the image again"]
        }
    finally:
        if temp_file and os.path.exists(temp_file):
            try:
                os.unlink(temp_file)
            except:
                pass
