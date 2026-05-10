# Image Detection Autoclicker

A fast Python-based real-time image detector that autoclicks until the selected image is no longer detected in the detection box. Designed for games or apps where there are quick time events (a fast response is required upon something appearing, such as an exclamation mark).

This app uses OpenCV for image detection and Dear PyGUI for the GUI.

## Features
- Clean, easy to use GUI
- FPS and match confidence display
- Easy to change settings
- Detects the selected image on a portion of the screen
- Supports multi-scale matching
- Fast detection loop with minimal CPU usage
- Optional preview of the detection box

## Settings
- Path of the image to detect
- Size and position of the detection box
- Minimum confidence percentage for a match
- Preview window toggle
- Always on top toggle

## Setup

### 1. Install Python (if not already)
Make sure Python 3.8+ is installed

### 2. Install required libraries
```bash
pip install opencv-python numpy pyautogui mss dearpygui pynput
```

### 3. Choose image / change settings
Make sure to review the settings and make sure your image file name is correct

### 4. Allow permissions
On Windows, make sure to run as administrator. On Mac, go to Privacy and Security > Accessibility.

### 5. Run the file
```bash
python main.py
```

### 6. Set your settings
Make sure the image path is correct and the image you intend to detect will appear within the detection box

### 7. Start the bot, and enjoy!
