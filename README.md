# Image Detection Autoclicker

A fast and flexible Python-based real-time image detector that autoclicks on image detection until the image is no longer detected. Designed for games or apps where a fast response is required upon something appearing, such as an exclamation mark.

Make sure to place the images you want to detect in the images folder.

This script uses OpenCV for image detection.

## Features
- Easy to change settings
- Detects the selected image on a portion of the screen
- Supports multi-scale matching
- Fast detection loop with minimal CPU usage
- Optional preview with an FPS and match confidence display

## Settings
- Name of the image to detect
- Size of the detection box (width and height)
- Minimum confidence percentage for a match
- Turn on or off the preview preview window

## Setup

### 1. Install Python (if not already)
Make sure Python 3.8+ is installed

### 2. Install required libraries
```bash
pip install opencv-python numpy pyautogui mss
```

### 3. Choose image / change settings
Make sure to review the settings and make sure your image file name is correct

### 4. Allow permissions
On Windows, make sure to run as administrator. On Mac, go to Privacy and Security > Accessibility.

### 5. Run the file
```bash
python main.py
```
