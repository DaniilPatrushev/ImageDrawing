import os

# Face++ credentials
params = {
    'api_key': os.getenv('API_KEY'),
    'api_secret': os.getenv('API_SECRET'),
    'return_landmark': 2
}

# FACE++ API URL
FACEPP_URL = 'https://api-us.faceplusplus.com/facepp/v3/detect'

# Path to image directory
LOCAL_STORAGE_IMAGE_PATH = os.getenv('LOCAL_STORAGE_IMAGE_PATH', './images/')