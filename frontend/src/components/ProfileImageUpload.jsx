import { useState, useRef } from 'react';
import api from '../api/axios';
import API_BASE_URL from '../config/api';

export default function ProfileImageUpload({ currentImage, onImageUpdate }) {
  const [uploading, setUploading] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [cameraActive, setCameraActive] = useState(false);
  const [cameraReady, setCameraReady] = useState(false);
  const [capturedImage, setCapturedImage] = useState(null);
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);
  const fileInputRef = useRef(null);

  const startCamera = async () => {
    try {
      setCameraReady(false);
      setCameraActive(true);
      
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { 
          facingMode: 'user', 
          width: { ideal: 640 }, 
          height: { ideal: 480 } 
        } 
      });
      
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        streamRef.current = stream;
        
        // Wait for video to be ready
        videoRef.current.onloadedmetadata = () => {
          videoRef.current.play().then(() => {
            setCameraReady(true);
          }).catch(err => {
            console.error('Error playing video:', err);
            alert('Failed to start camera preview');
            stopCamera();
          });
        };
      }
    } catch (err) {
      console.error('Camera error:', err);
      setCameraActive(false);
      if (err.name === 'NotAllowedError') {
        alert('Camera access denied. Please allow camera access in your browser settings.');
      } else if (err.name === 'NotFoundError') {
        alert('No camera found. Please connect a camera or use file upload.');
      } else {
        alert('Camera access failed: ' + err.message + '. Please use file upload instead.');
      }
    }
  };

  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    setCameraActive(false);
    setCameraReady(false);
  };

  const capturePhoto = () => {
    if (!videoRef.current || !canvasRef.current || !cameraReady) {
      alert('Camera not ready. Please wait.');
      return null;
    }
    
    const canvas = canvasRef.current;
    const video = videoRef.current;
    
    canvas.width = video.videoWidth || 640;
    canvas.height = video.videoHeight || 480;
    
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    
    const photoData = canvas.toDataURL('image/jpeg', 0.8);
    setCapturedImage(photoData);
    stopCamera();
    return photoData;
  };

  const handleCapture = () => {
    capturePhoto();
  };

  const handleUploadCaptured = async () => {
    if (!capturedImage) return;

    setUploading(true);
    try {
      console.log('Uploading captured image...');
      const response = await api.post('/attendance/upload-profile-image', {
        image: capturedImage
      });
      
      console.log('Upload response:', response.data);
      
      if (response.data.success) {
        alert('Profile image updated successfully!');
        const imageUrl = response.data.data?.profile_image_url || capturedImage;
        setCapturedImage(null);
        onImageUpdate && onImageUpdate(imageUrl);
      } else {
        alert('Failed to upload image: ' + (response.data.message || 'Unknown error'));
      }
    } catch (error) {
      console.error('Upload error:', error);
      alert('Failed to upload image: ' + (error.response?.data?.detail || error.message));
    } finally {
      setUploading(false);
    }
  };

  const handleRetakePhoto = () => {
    setCapturedImage(null);
    startCamera();
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    // Validate file type
    if (!file.type.startsWith('image/')) {
      alert('Please select a valid image file');
      return;
    }

    // Validate file size (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
      alert('Image size must be less than 5MB');
      return;
    }

    // Convert file to base64
    const reader = new FileReader();
    reader.onload = async (e) => {
      setUploading(true);
      try {
        console.log('Uploading file...');
        const response = await api.post('/attendance/upload-profile-image', {
          image: e.target.result
        });
        
        console.log('Upload response:', response.data);
        
        if (response.data.success) {
          alert('Profile image updated successfully!');
          const imageUrl = response.data.data?.profile_image_url || e.target.result;
          setCapturedImage(null);
          onImageUpdate && onImageUpdate(imageUrl);
        } else {
          alert('Failed to upload image: ' + (response.data.message || 'Unknown error'));
        }
      } catch (error) {
        console.error('Upload error:', error);
        alert('Failed to upload image: ' + (error.response?.data?.detail || error.message));
      } finally {
        setUploading(false);
        // Reset file input
        if (fileInputRef.current) {
          fileInputRef.current.value = '';
        }
      }
    };
    reader.onerror = () => {
      alert('Failed to read file');
    };
    reader.readAsDataURL(file);
  };

  const handleDeleteImage = async () => {
    if (!window.confirm('Are you sure you want to delete your profile photo? You can upload a new one anytime.')) {
      return;
    }

    setDeleting(true);
    try {
      console.log('Deleting profile image...');
      const response = await api.delete('/attendance/delete-profile-image');
      
      console.log('Delete response:', response.data);
      
      if (response.data.success) {
        alert('Profile image deleted successfully!');
        setCapturedImage(null);
        onImageUpdate && onImageUpdate(null);
      } else {
        alert('Failed to delete image: ' + (response.data.message || 'Unknown error'));
      }
    } catch (error) {
      console.error('Delete error:', error);
      alert('Failed to delete image: ' + (error.response?.data?.detail || error.message));
    } finally {
      setDeleting(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">📸 Profile Photo</h3>
      
      {/* Current Image */}
      {currentImage && !capturedImage && (
        <div className="mb-4 text-center">
          <img 
            src={
              currentImage.startsWith('data:') 
                ? currentImage 
                : currentImage.startsWith('http')
                ? currentImage
                : currentImage.startsWith('/')
                ? `${API_BASE_URL}${currentImage}`
                : `${API_BASE_URL}/${currentImage}`
            } 
            alt="Profile" 
            className="w-32 h-32 rounded-full mx-auto border-4 border-gray-200 object-cover"
            onError={(e) => {
              console.error('Failed to load image:', currentImage);
              e.target.style.display = 'none';
            }}
          />
          <p className="text-sm text-gray-600 mt-2">Current profile photo</p>
          
          {/* Delete and Update Buttons */}
          <div className="flex space-x-3 mt-4">
            <button
              onClick={handleDeleteImage}
              disabled={deleting}
              className="flex-1 bg-red-600 text-white py-2 px-4 rounded-lg hover:bg-red-700 disabled:bg-gray-400 font-semibold transition"
            >
              {deleting ? '🗑️ Deleting...' : '🗑️ Delete Photo'}
            </button>
            <button
              onClick={startCamera}
              className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 font-semibold transition"
            >
              📷 Update Photo
            </button>
          </div>
        </div>
      )}

      {/* Captured Image Preview */}
      {capturedImage && (
        <div className="mb-4 text-center">
          <img 
            src={capturedImage} 
            alt="Captured" 
            className="w-32 h-32 rounded-full mx-auto border-4 border-green-200"
          />
          <p className="text-sm text-green-600 mt-2">📸 Photo captured!</p>
          <div className="flex space-x-3 mt-4">
            <button
              onClick={handleUploadCaptured}
              disabled={uploading}
              className="flex-1 bg-green-600 text-white py-2 px-4 rounded-lg hover:bg-green-700 disabled:bg-gray-400 font-semibold transition"
            >
              {uploading ? 'Uploading...' : '✅ Save Photo'}
            </button>
            <button
              onClick={handleRetakePhoto}
              className="flex-1 bg-gray-600 text-white py-2 px-4 rounded-lg hover:bg-gray-700 font-semibold transition"
            >
              🔄 Retake
            </button>
          </div>
        </div>
      )}

      {/* Camera Section */}
      {cameraActive && !capturedImage ? (
        <div className="mb-4">
          <div className="relative bg-black rounded-lg overflow-hidden">
            <video 
              ref={videoRef} 
              autoPlay 
              playsInline
              muted
              className="w-full h-64 object-cover"
            />
            <div className="absolute inset-0 border-4 border-blue-400 opacity-30 rounded-full w-48 h-48 m-auto pointer-events-none"></div>
            {cameraReady && (
              <div className="absolute top-4 right-4">
                <span className="bg-green-500 text-white px-3 py-1 rounded-full text-xs font-semibold flex items-center">
                  <span className="w-2 h-2 bg-white rounded-full mr-2 animate-pulse"></span>
                  LIVE
                </span>
              </div>
            )}
          </div>
          <canvas ref={canvasRef} className="hidden" />
          
          <div className="flex space-x-3 mt-4">
            <button
              onClick={handleCapture}
              disabled={!cameraReady}
              className="flex-1 bg-green-600 text-white py-2 px-4 rounded-lg hover:bg-green-700 disabled:bg-gray-400 font-semibold transition"
            >
              📸 Capture Photo
            </button>
            <button
              onClick={stopCamera}
              className="flex-1 bg-gray-600 text-white py-2 px-4 rounded-lg hover:bg-gray-700 font-semibold transition"
            >
              Cancel
            </button>
          </div>
        </div>
      ) : !capturedImage ? (
        <div className="space-y-3">
          <button
            onClick={startCamera}
            className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 font-semibold transition"
          >
            📷 Take Photo with Camera
          </button>
          
          <div className="text-center text-gray-500">or</div>
          
          <button
            onClick={() => fileInputRef.current?.click()}
            className="w-full bg-purple-600 text-white py-3 rounded-lg hover:bg-purple-700 font-semibold transition"
          >
            📁 Upload from Files
          </button>
          
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={handleFileUpload}
            className="hidden"
          />
        </div>
      ) : null}

      <p className="text-xs text-gray-500 mt-3">
        This photo will be used for face recognition during attendance marking.
      </p>
    </div>
  );
}