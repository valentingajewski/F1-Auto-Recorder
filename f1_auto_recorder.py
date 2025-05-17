import tkinter as tk
from tkinter import messagebox, filedialog
from datetime import datetime, timedelta
import time
import threading
import pyautogui
import keyboard
import json
import os
from PIL import Image, ImageTk, ImageFilter
import subprocess

CONFIG_FILE = "config.json"
BACKGROUND_IMAGE = "image1.jpg"
DEFAULT_SOFTWARE_NAME = "MultiViewer for F1.exe"

def save_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f)

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}

def start_recording_task(gp_time_str, home_coords, live_btn_coords, flux_coords, sound_coords, live_win_coords):
    try:
        gp_time = datetime.strptime(gp_time_str, "%H:%M")
        now = datetime.now()
        target_time = now.replace(hour=gp_time.hour, minute=gp_time.minute, second=0, microsecond=0)
        if target_time < now:
            target_time += timedelta(days=1)

        press_live_time = target_time - timedelta(minutes=2)
        stop_recording_time = target_time + timedelta(hours=4)

        print(f"GP scheduled at: {target_time}")
        print(f"Pressing 'Live' at: {press_live_time}")
        print(f"Stopping recording at: {stop_recording_time}")

        while datetime.now() < press_live_time:
            time.sleep(1)

        # Click Home button
        print("🏠 Clicking on Home button")
        pyautogui.moveTo(*home_coords)
        pyautogui.click()

        print("⏳ Waiting 5 seconds before clicking Live...")
        time.sleep(5)

        print("🖱 Clicking on Live button")
        pyautogui.moveTo(*live_btn_coords)
        pyautogui.click()

        time.sleep(2)

        print("🖱 Clicking on stream")
        pyautogui.moveTo(*flux_coords)
        pyautogui.click()

        time.sleep(2)

        print("🔊 Clicking on audio")
        pyautogui.moveTo(*sound_coords)
        pyautogui.click()

        print("⏳ Waiting 5 seconds before double click")
        time.sleep(5)

        print("🖱 Double clicking on video window")
        pyautogui.moveTo(*live_win_coords)
        pyautogui.doubleClick()

        time.sleep(1)

        print("🟢 Starting recording (ALT+F9)")
        keyboard.press_and_release('alt+f9')

        while datetime.now() < stop_recording_time:
            time.sleep(10)

        print("🔴 Stopping recording (ALT+F9)")
        keyboard.press_and_release('alt+f9')

        print("✅ Done")

    except Exception as e:
        messagebox.showerror("Error", str(e))

def launch_interface():
    config = load_config()

    def on_start():
        gp_time = entry_time.get()
        try:
            datetime.strptime(gp_time, "%H:%M")
        except ValueError:
            messagebox.showerror("Error", "Invalid time format. Use HH:MM.")
            return

        try:
            live_btn = tuple(map(int, entry_live.get().split(',')))
            home_click = tuple(map(int, entry_home.get().split(',')))
            flux_click = tuple(map(int, entry_flux.get().split(',')))
            sound_click = tuple(map(int, entry_sound.get().split(',')))
            live_win = tuple(map(int, entry_window.get().split(',')))
        except ValueError:
            messagebox.showerror("Error", "Invalid coordinates format. Use x,y.")
            return

        if not os.path.exists(software_path.get()):
            messagebox.showerror("Error", "MultiViewer for F1 path is invalid.")
            return

        # Launch MultiViewer
        subprocess.Popen(software_path.get())
        threading.Thread(
            target=start_recording_task,
            args=(gp_time, home_click, live_btn, flux_click, sound_click, live_win),
            daemon=True
        ).start()

    def update_cursor_position():
        x, y = pyautogui.position()
        label_cursor.config(text=f"Mouse position: {x}, {y}")
        window.after(100, update_cursor_position)

    def update_timer():
        try:
            gp_time = datetime.strptime(entry_time.get(), "%H:%M")
            now = datetime.now()
            target_time = now.replace(hour=gp_time.hour, minute=gp_time.minute, second=0, microsecond=0)
            if target_time < now:
                target_time += timedelta(days=1)
            delta = target_time - now
            label_timer.config(text=f"Estimated time to GP: {str(delta).split('.')[0]}")
        except:
            label_timer.config(text="Estimated time to GP: --:--:--")
        window.after(1000, update_timer)

    def on_save_config():
        data = {
            "time": entry_time.get(),
            "home": entry_home.get(),
            "live": entry_live.get(),
            "flux": entry_flux.get(),
            "sound": entry_sound.get(),
            "window": entry_window.get(),
            "multiviewer_path": os.path.dirname(software_path.get())
        }
        save_config(data)
        messagebox.showinfo("Saved", "Configuration saved.")

    def choose_folder():
        folder = filedialog.askdirectory()
        if folder:
            full_path = os.path.join(folder, DEFAULT_SOFTWARE_NAME)
            software_path.set(full_path)

    # === GUI ===
    window = tk.Tk()
    window.title("F1 Auto Recorder")
    window.geometry("480x470")
    window.resizable(False, False)

    # Background image
    bg_image = Image.open(BACKGROUND_IMAGE).resize((480, 470))
    blurred = bg_image.filter(ImageFilter.GaussianBlur(4))
    bg_photo = ImageTk.PhotoImage(blurred)
    bg_label = tk.Label(window, image=bg_photo)
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    container = tk.Frame(window, bg="#ffffff", bd=0)
    container.place(relx=0.5, rely=0.5, anchor="center")

    tk.Label(container, text="🎥 F1 Auto Recorder", font=("Helvetica", 14, "bold"), bg="#ffffff").grid(row=0, column=0, columnspan=2, pady=(10, 8))
    label_timer = tk.Label(container, text="Estimated time to GP: --:--:--", font=("Helvetica", 10), bg="#ffffff", fg="green")
    label_timer.grid(row=1, column=0, columnspan=2, pady=(0, 10))

    def add_row(label_text, row_index, default_value):
        tk.Label(container, text=label_text, bg="#ffffff", anchor="w").grid(row=row_index, column=0, sticky="w", padx=10, pady=5)
        entry = tk.Entry(container, width=25)
        entry.insert(0, default_value)
        entry.grid(row=row_index, column=1, padx=10, pady=5)
        return entry

    entry_time = add_row("GP Time (HH:MM):", 2, config.get("time", ""))
    entry_home = add_row("Home button coords (x,y):", 3, config.get("home", ""))
    entry_live = add_row("Live button coords (x,y):", 4, config.get("live", ""))
    entry_flux = add_row("Stream click coords (x,y):", 5, config.get("flux", ""))
    entry_sound = add_row("Audio button coords (x,y):", 6, config.get("sound", ""))
    entry_window = add_row("Video window coords (x,y):", 7, config.get("window", ""))

    # MultiViewer path row
    tk.Label(container, text="MultiViewer folder:", bg="#ffffff", anchor="w").grid(row=7, column=0, sticky="w", padx=10, pady=5)
    software_path = tk.StringVar()
    default_folder = config.get("multiviewer_path", "")
    if default_folder:
        software_path.set(os.path.join(default_folder, DEFAULT_SOFTWARE_NAME))
    entry_path = tk.Entry(container, textvariable=software_path, width=25)
    entry_path.grid(row=7, column=1, padx=10, pady=5)

    btn_browse = tk.Button(container, text="Browse...", command=choose_folder, width=15)
    btn_browse.grid(row=8, column=0, columnspan=2, pady=(0, 8))

    tk.Button(container, text="▶ Start", width=15, command=on_start).grid(row=9, column=0, pady=10)
    tk.Button(container, text="💾 Save Config", width=15, command=on_save_config).grid(row=9, column=1, pady=10)

    label_cursor = tk.Label(container, text="Mouse position: ", fg="blue", bg="#ffffff")
    label_cursor.grid(row=10, column=0, columnspan=2, pady=(0, 10))

    update_cursor_position()
    update_timer()
    window.mainloop()

if __name__ == "__main__":
    launch_interface()
