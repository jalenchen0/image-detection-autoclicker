import cv2
import numpy as np
from mss import mss
import pyautogui
import time
import json
import os
import threading
import dearpygui.dearpygui as dpg
from pynput import mouse

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
    "box_x": 800,
    "box_y": 400,
    "box_size": 200,
    "threshold": 0.75,
    "show_preview": True,
    "always_on_top": True
}

running = False
thread = None
settings = {}

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            try:
                return {**DEFAULT_SETTINGS, **json.load(f)}
            except:
                pass
    return DEFAULT_SETTINGS

def save_settings(settings):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=4)

# ============= BOT LOOP =============
def bot():
    global running, settings

    template_path = settings["image_name"]

    if not os.path.exists(template_path):
        print(f"❌ Template image '{template_path}' not found!")
        running = False
        return

    template = cv2.imread(template_path, cv2.IMREAD_COLOR)
    if template is None:
        print("❌ Failed to load image.")
        running = False
        return

    template_w, template_h = template.shape[:2]
    sct = mss()
    fps_time = time.time()
    frames = 0

    while running:
        frames += 1
        if time.time() - fps_time >= 1:
            dpg.set_value("fps_text", f"FPS: {frames}")
            frames = 0
            fps_time = time.time()

        monitor = {
            "left": int(settings["box_x"]),
            "top": int(settings["box_y"]),
            "width": int(settings["box_size"]),
            "height": int(settings["box_size"])
        }

        scr_raw = np.array(sct.grab(monitor))
        frame_bgr = cv2.cvtColor(scr_raw, cv2.COLOR_BGRA2BGR)

        best_val = -1
        best_loc = None
        best_scale = 1

        scales = np.linspace(0.5, 1.5, 10)
        for scale in scales:
            w = int(template_w * scale)
            h = int(template_h * scale)

            if w >= settings["box_size"] or h >= settings["box_size"] or w < 10 or h < 10:
                continue

            resized = cv2.resize(template, (w, h), interpolation=cv2.INTER_LINEAR)
            res = cv2.matchTemplate(frame_bgr, resized, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(res)

            if max_val > best_val:
                best_val = max_val

        dpg.set_value("conf_text", f"Confidence: {best_val:.2f}")

        if best_val >= settings["threshold"]:
            pyautogui.click()

        if settings["show_preview"]:
            rgba = cv2.cvtColor(frame_bgr, cv2.COLOR_BGRA2RGBA)
            rgba = cv2.resize(rgba, (300, 300))
            dpg.set_value("preview_texture", rgba.flatten()/255.0)

        time.sleep(0.05)

# ============= ALWAYS ON TOP CALLBACK =============
def toggle_on_top(sender, app_data):
    dpg.set_viewport_always_top(app_data)

# ============= CLICK LISTENER =============
def on_click(x, y, button, pressed):
    if button == mouse.Button.left and pressed:
        offset = dpg.get_value("Box Size") // 2
        dpg.set_value("Box X", int(x - offset))
        dpg.set_value("Box Y", int(y - offset))
        dpg.set_item_label("pos_btn", "Select Location (Click anywhere)")
        return False

def start_click_selection():
    dpg.set_item_label("pos_btn", "LISTENING... CLICK ON POSITION")
    listener = mouse.Listener(on_click=on_click)
    listener.start()

# ============= UI CALLBACKS =============
def start_callback():
    global running, settings
    if not running:
        settings.update({
            "image_name": dpg.get_value("Image File"),
            "box_x": dpg.get_value("Box X"),
            "box_y": dpg.get_value("Box Y"),
            "box_size": dpg.get_value("Box Size"),
            "threshold": dpg.get_value("Threshold"),
            "show_preview": dpg.get_value("Show Preview"),
            "always_on_top": dpg.get_value("Always On Top")
        })
        save_settings(settings)
        running = True
        threading.Thread(target=bot, daemon=True).start()

def stop_callback():
    global running
    running = False

# ============= GUI =============
def add_help_marker(message):
    dpg.add_text("(?)")
    with dpg.tooltip(dpg.last_item()):
        dpg.add_text(message)

def build_gui():
    global settings
    settings = load_settings()

    dpg.create_context()

    with dpg.texture_registry():
        dpg.add_dynamic_texture(300, 300, [0.0] * 300 * 300 * 4, tag="preview_texture")

    with dpg.window(label="Image Detection Bot", width=400, height=750):
        dpg.add_input_text(label="Image File", default_value=settings["image_name"], tag="Image File")

        with dpg.group(horizontal=True):
            dpg.add_button(label="Select Screen Location", callback=start_click_selection)
            add_help_marker("1. Click button\n2. Click the target on your screen")
        dpg.add_slider_int(label="Box X", default_value=settings["box_x"], min_value=0, max_value=pyautogui.size()[0], tag="Box X")
        dpg.add_slider_int(label="Box Y", default_value=settings["box_y"], min_value=0, max_value=pyautogui.size()[1], tag="Box Y")
        dpg.add_slider_int(label="Box Size", default_value=settings["box_size"], min_value=50, max_value=1000, tag="Box Size")
        with dpg.group(horizontal=True):
            dpg.add_slider_float(label="Threshold", default_value=settings["threshold"], min_value=0.1, max_value=1.0, tag="Threshold")
            add_help_marker("The percentage confidence of the detection\nrequired to trigger the autoclick.\n\nHigher = more accurate but less sensitive.")
        dpg.add_checkbox(label="Show Preview", default_value=settings["show_preview"], tag="Show Preview")
        dpg.add_checkbox(label="Always On Top", default_value=settings["always_on_top"], tag="Always On Top", callback=toggle_on_top)

        dpg.add_spacer(height=10)
        with dpg.group(horizontal=True):
            dpg.add_button(label="START BOT", callback=start_callback)
            dpg.add_button(label="STOP BOT", callback=stop_callback)

        dpg.add_separator()
        dpg.add_text("FPS: 0", tag="fps_text")
        dpg.add_text("Confidence: 0.00", tag="conf_text")

        dpg.add_text("Preview (300x300 scaled):")
        dpg.add_image("preview_texture")

    dpg.create_viewport(title="Image Bot", width=400, height=750)
    dpg.setup_dearpygui()
    dpg.show_viewport()

    dpg.set_viewport_always_top(settings["always_on_top"])

    dpg.start_dearpygui()
    dpg.destroy_context()


if __name__ == "__main__":
    build_gui()
