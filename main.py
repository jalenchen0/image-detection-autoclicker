import cv2
import numpy as np
from mss import mss
import pyautogui
import time
import json
import os
import threading
import dearpygui.dearpygui as dpg

# ===========================================================
# Image Detection Autoclicker Script
# ===========================================================
# This script detects a specific image on a portion of the screen.
# On detection, it autoclicks at the current mouse position
# until the image is no longer detected.
# ===========================================================

SETTINGS_FILE = "settings.json"

DEFAULT_SETTINGS = {
    "image_name": "images/exclamation.png",
    "box_size": 200,
    "threshold": 0.75,
    "show_preview": True
}

running = False
thread = None
settings = {}

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                print("⚠️ Error reading settings.json, using defaults.")
    save_settings(DEFAULT_SETTINGS)
    return DEFAULT_SETTINGS

def save_settings(settings):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=4)


# ============= BOT LOOP =============
def bot():
    global running, settings

    if not os.path.exists(settings["image_name"]):
        print(f"❌ Template image '{settings['image_name']}' not found!")
        running = False
        return

    template = cv2.imread(settings["image_name"], cv2.IMREAD_GRAYSCALE)
    template_w, template_h = template.shape[::-1]

    sct = mss()
    fps_time = time.time()
    frames = 0

    while running:
        frames += 1
        if time.time() - fps_time >= 1:
            dpg.set_value("fps_text", f"FPS: {frames}")
            frames = 0
            fps_time = time.time()

        screen_w, screen_h = pyautogui.size()
        left = screen_w // 2 - settings["box_size"] // 2
        top = screen_h // 2 - settings["box_size"] // 2
        monitor = {"left": left, "top": top, "width": settings["box_size"], "height": settings["box_size"]}

        img = np.array(sct.grab(monitor))
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        max_val = 0
        max_loc = None
        max_scale = 1.0
        scales = np.linspace(0.5, 1.5, 10)

        for scale in scales:
            w = int(template_w * scale)
            h = int(template_h * scale)

            if w > settings["box_size"] or h > settings["box_size"]:
                continue

            resized_template = cv2.resize(template, (w, h), interpolation=cv2.INTER_AREA)
            result = cv2.matchTemplate(gray, resized_template, cv2.TM_CCOEFF_NORMED)
            _, local_max_val, _, local_max_loc = cv2.minMaxLoc(result)

            if local_max_val > max_val:
                max_val = local_max_val
                max_loc = local_max_loc
                max_scale = scale

        dpg.set_value("conf_text", f"Confidence: {max_val:.2f}")

        if max_val >= settings["threshold"]:
            pyautogui.click()

        if settings["show_preview"]:
            rgba = cv2.cvtColor(img, cv2.COLOR_BGRA2RGBA)
            rgba = cv2.resize(rgba, (300, 300))
            dpg.set_value("preview_texture", rgba.flatten()/255.0)

        time.sleep(0.01)


# ============= UI CALLBACKS =============
def start_callback(sender, app_data):
    global running, thread, settings
    if running:
        return

    settings["image_name"] = dpg.get_value("Image File")
    settings["box_size"] = dpg.get_value("Box Size")
    settings["threshold"] = dpg.get_value("Threshold")
    settings["show_preview"] = dpg.get_value("Show Preview")

    save_settings(settings)
    running = True
    thread = threading.Thread(target=bot, daemon=True)
    thread.start()

def stop_callback(sender, app_data):
    global running
    running = False

def save_callback(sender, app_data):
    global settings
    settings["image_name"] = dpg.get_value("Image File")
    settings["box_size"] = dpg.get_value("Box Size")
    settings["threshold"] = dpg.get_value("Threshold")
    settings["show_preview"] = dpg.get_value("Show Preview")
    save_settings(settings)


# ============= GUI =============
def build_gui():
    global settings
    settings = load_settings()

    dpg.create_context()

    with dpg.texture_registry():
        dpg.add_dynamic_texture(300, 300, [0.0] * 300 * 300 * 4, tag="preview_texture")

    with dpg.window(label="Image Detection Autoclicker", width=400, height=750):
        dpg.add_input_text(label="Image File", default_value=settings["image_name"], tag="Image File")
        dpg.add_slider_int(label="Box Size", default_value=settings["box_size"], min_value=50, max_value=1000, tag="Box Size")
        dpg.add_slider_float(label="Threshold", default_value=settings["threshold"], min_value=0.1, max_value=1.0, format="%.2f", tag="Threshold")
        dpg.add_checkbox(label="Show Preview", default_value=settings["show_preview"], tag="Show Preview")

        dpg.add_button(label="Start", callback=start_callback)
        dpg.add_button(label="Stop", callback=stop_callback)
        dpg.add_button(label="Save Settings", callback=save_callback)

        dpg.add_text("FPS: 0", tag="fps_text")
        dpg.add_text("Confidence: 0.00", tag="conf_text")

        dpg.add_separator()
        dpg.add_text("Instructions:")
        dpg.add_text("1. Set the image name")
        dpg.add_text("2. Adjust detection box size and threshold")
        dpg.add_text("3. Click Save Settings to save your configuration")
        dpg.add_text("4. Click Start to begin detection")
        dpg.add_text("5. Click Stop to end detection")
        dpg.add_text("The script will autoclick when the image is detected")

        dpg.add_separator()
        dpg.add_text("Preview:")
        dpg.add_image("preview_texture")

    dpg.create_viewport(title="Image Detection Autoclicker", width=400, height=750)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()


if __name__ == "__main__":
    build_gui()
