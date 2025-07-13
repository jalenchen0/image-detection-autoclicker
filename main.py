import cv2
import numpy as np
import mss
import pyautogui
import time

# ===========================================================
# Image Detection Autoclicker Script
# ===========================================================
# This script detects a specific image on a portion of the screen.
# On detection, it autoclicks at the current mouse position
# until the image is no longer detected.
# ===========================================================
# SETTINGS
image_name = "exclamation.png"  # Name of the image to detect
box_size = 200  # Size of the detection box (width and height)
threshold = 0.75  # Minimum confidence percentage for a match
show_preview = True  # Set to False to disable the preview window
# ===========================================================

# === Load and preprocess template ===
template_orig = cv2.imread(f"images/{image_name}", cv2.IMREAD_UNCHANGED)
template_gray = cv2.cvtColor(template_orig, cv2.COLOR_BGR2GRAY)
template_gray = cv2.resize(template_gray, (0, 0), fx=0.6, fy=0.6)

scales = np.linspace(0.8, 1.2, 10)[::-1]

# === Screen region setup ===
sct = mss.mss()
screen_width = sct.monitors[1]["width"]
screen_height = sct.monitors[1]["height"]

monitor = {
    "top": screen_height // 2 - box_size // 2,
    "left": screen_width // 2 - box_size // 2,
    "width": box_size,
    "height": box_size,
}

def detect_mark(screen_gray):
    best_match = None
    best_val = 0

    for scale in scales:
        resized_template = cv2.resize(template_gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
        tH, tW = resized_template.shape

        if screen_gray.shape[0] < tH or screen_gray.shape[1] < tW:
            continue

        result = cv2.matchTemplate(screen_gray, resized_template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)

        if max_val >= threshold and max_val > best_val:
            best_match = (max_loc, tW, tH)
            best_val = max_val

    if best_match:
        (x, y), w, h = best_match
        return (x, y, w, h, best_val)
    return None

# === FPS tracking ===
frame_count = 0
start_time = time.time()

print("Running Image Detection Autoclicker Script. Press ESC on the preview window or press Ctrl+C in the terminal to stop the script.")

while True:
    screenshot = np.array(sct.grab(monitor))
    screen_bgr = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)
    screen_gray = cv2.cvtColor(screen_bgr, cv2.COLOR_BGR2GRAY)

    match = detect_mark(screen_gray)

    if match:
        x, y, w, h, confidence = match
        mouse_x, mouse_y = pyautogui.position()

        # Draw detection box
        cv2.rectangle(screen_bgr, (x, y), (x + w, y + h), (0, 255, 0), 2)
        # Show confidence
        cv2.putText(screen_bgr, f"Confidence: {confidence:.2f}", (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        # Auto click
        pyautogui.click(mouse_x, mouse_y)
    else:
        time.sleep(0.01)

    # FPS calculation
    frame_count += 1
    elapsed = time.time() - start_time
    if elapsed >= 1.0:
        fps = frame_count / elapsed
        frame_count = 0
        start_time = time.time()
    else:
        fps = None

    # Draw FPS in corner
    if fps:
        cv2.putText(screen_bgr, f"FPS: {fps:.1f}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

    # Show the preview
    if show_preview:
        cv2.imshow("Detection Preview", screen_bgr)
    if cv2.waitKey(1) == 27:  # ESC to quit
        break

cv2.destroyAllWindows()
