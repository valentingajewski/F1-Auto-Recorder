import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta
import time
import threading
import pyautogui
import keyboard
import json
import os
from PIL import Image, ImageTk, ImageFilter

CONFIG_FILE = "config.json"
BACKGROUND_IMAGE = "image1.jpg"

def save_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f)

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}

def start_recording_task(gp_time_str, live_btn_coords, flux_coords, sound_coords, live_win_coords):
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

        print("🖱 Clicking on Live button")
        pyautogui.moveTo(*live_btn_coords)
        pyautogui.click()

        time.sleep(2)

        print("🖱 Clicking on stream")
        pyautogui.moveTo(*flux_coords)
        pyautogui.click()

        time.sleep(5)

        print("🔊 Clicking on audio")
        pyautogui.moveTo(*sound_coords)
        pyautogui.click()

        print("⏳ Waiting 5 seconds before double click")
        time.sleep(2)

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
            flux_click = tuple(map(int, entry_flux.get().split(',')))
            sound_click = tuple(map(int, entry_sound.get().split(',')))
            live_win = tuple(map(int, entry_window.get().split(',')))
        except ValueError:
            messagebox.showerror("Error", "Invalid coordinates format. Use x,y.")
            return

        threading.Thread(
            target=start_recording_task,
            args=(gp_time, live_btn, flux_click, sound_click, live_win),
            daemon=True
        ).start()
        messagebox.showinfo("Running", "Script is now running and waiting for GP.")

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
            "live": entry_live.get(),
            "flux": entry_flux.get(),
            "sound": entry_sound.get(),
            "window": entry_window.get()
        }
        save_config(data)
        messagebox.showinfo("Saved", "Configuration saved.")

    # === GUI window ===
    window = tk.Tk()
    window.title("F1 Auto Recorder")
    window.geometry("460x440")
    window.resizable(False, False)

    # === Blurred background ===
    bg_image = Image.open(BACKGROUND_IMAGE).resize((460, 440))
    blurred = bg_image.filter(ImageFilter.GaussianBlur(4))
    bg_photo = ImageTk.PhotoImage(blurred)

    bg_label = tk.Label(window, image=bg_photo)
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    # === Main container ===
    container = tk.Frame(window, bg="#ffffff", bd=0)
    container.place(relx=0.5, rely=0.5, anchor="center")

    title = tk.Label(container, text="🎥 F1 Auto Recorder", font=("Helvetica", 14, "bold"), bg="#ffffff")
    title.grid(row=0, column=0, columnspan=2, pady=(10, 8))

    label_timer = tk.Label(container, text="Estimated time to GP: --:--:--", font=("Helvetica", 10), bg="#ffffff", fg="green")
    label_timer.grid(row=1, column=0, columnspan=2, pady=(0, 10))

    def add_row(label_text, row_index, default_value):
        label = tk.Label(container, text=label_text, bg="#ffffff", anchor="w")
        label.grid(row=row_index, column=0, sticky="w", padx=10, pady=5)
        entry = tk.Entry(container, width=25)
        entry.insert(0, default_value)
        entry.grid(row=row_index, column=1, padx=10, pady=5)
        return entry

    entry_time = add_row("GP Time (HH:MM):", 2, config.get("time", ""))
    entry_live = add_row("Live button coords (x,y):", 3, config.get("live", ""))
    entry_flux = add_row("Stream click coords (x,y):", 4, config.get("flux", ""))
    entry_sound = add_row("Audio button coords (x,y):", 5, config.get("sound", ""))
    entry_window = add_row("Video window coords (x,y):", 6, config.get("window", ""))

    btn_start = tk.Button(container, text="▶ Start", width=15, command=on_start)
    btn_start.grid(row=7, column=0, pady=10)

    btn_save = tk.Button(container, text="💾 Save Config", width=15, command=on_save_config)
    btn_save.grid(row=7, column=1, pady=10)

    label_cursor = tk.Label(container, text="Mouse position: ", fg="blue", bg="#ffffff")
    label_cursor.grid(row=8, column=0, columnspan=2, pady=(0, 10))

    update_cursor_position()
    update_timer()
    window.mainloop()

if __name__ == "__main__":
    launch_interface()
