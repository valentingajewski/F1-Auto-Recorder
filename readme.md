# 🏎️ F1 Auto Recorder

A simple automation script that launches a Formula 1 stream via MultiViewer for F1 and starts recording your screen using NVIDIA ShadowPlay at the perfect time — automatically.

## 📦 Features

- Set the Grand Prix time
- Predefine screen coordinates for UI actions (clicks)
- Automatically clicks on the stream, activates audio, and fullscreen
- Starts and stops screen recording with ShadowPlay
- Live countdown timer until race begins
- Mouse position tracker
- Configuration is saved locally

---

## 🖥️ How It Works

1. You input the **scheduled time** of the Grand Prix (e.g. `15:00`).
2. You specify the **screen coordinates** for:
   - Live button
   - Home button
   - Stream tile
   - Audio selector
   - Video window (for fullscreen double-click)

[image](parameters_config.PNG)

3. When you click **Start**, the script waits until:
   - **2 minutes before the race**: clicks "Live"
   - Then clicks the stream tile
   - Then clicks the audio stream
   - Then **waits 5 seconds**, and double-clicks the video to fullscreen
   - Then sends `Alt + F9` to start recording with NVIDIA ShadowPlay
   - After **4 hours**, it automatically sends `Alt + F9` again to stop recording

---

# 🖥️ How to launch the script

Simply double click on the .bat file. The script will launch the Multiviewer for F1 software.
You need to let you PC switch on.

## 🛠 Requirements

- NVDIA GeForce Experience
- F1 TV PRO account
- MultiViewer for F1
- Python =>3.12

Make sure the following Python packages are installed:

```bash
pip install pyautogui keyboard pillow
