# MP3 Splitter Application

A modern, user-friendly desktop application for splitting large MP3 files into smaller tracks based on silence detection. Built with Python, Tkinter, and pydub, this tool is ideal for musicians, podcasters, and anyone needing to batch-split audio files.

## Features

- **Waveform Visualization:** See your audio's waveform for easy navigation.
- **Automatic Splitting:** Detects silence and splits tracks automatically.
- **Custom Parameters:** Set minimum silence length (in mm:ss) and silence threshold (dBFS).
- **Batch Export:** Export all split tracks to your chosen folder.
- **Modern UI:** Responsive, resizable interface with progress and status indicators.
- **Bundled FFmpeg:** No need to install FFmpeg separately—just run the app!

## Getting Started

### Prerequisites
- Python 3.8+
- [pip](https://pip.pypa.io/en/stable/)

### Installation
1. **Clone the repository:**
   ```sh
   git clone https://github.com/PrashantK4747/MP3-Splitter-App.git
   cd MP3-Splitter-App
   ```
2. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
3. **Ensure FFmpeg binaries are present:**
   - The `bin/` folder should contain `ffmpeg.exe`, `ffplay.exe`, and `ffprobe.exe`.
   - _Do not commit these binaries to GitHub (see .gitignore)._

### Usage
1. Run the application:
   ```sh
   python main.py
   ```
2. Select your source MP3 file and output folder.
3. Set splitting parameters:
   - **Min Silence Length:** Format `mm:ss` (e.g., `00:02` for 2 seconds)
   - **Silence Threshold:** dBFS value (e.g., `-40`)
4. Click **Start Splitting**. Tracks will be saved in the output folder.

## Parameters Explained
- **Min Silence Length (mm:ss):** The minimum duration of silence to be considered a split point.
- **Silence Threshold (dBFS):** The volume below which audio is considered silent. Lower (more negative) values are less sensitive.

## Troubleshooting
- If splitting fails, ensure your MP3 is valid and FFmpeg binaries are present in the `bin/` folder.
- For large files, splitting may take a few minutes.

## Contributing
Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

## Credits
- [pydub](https://github.com/jiaaro/pydub)
- [Tkinter](https://docs.python.org/3/library/tkinter.html)
- [FFmpeg](https://ffmpeg.org/)

🔗 Links
FFmpeg: https://ffmpeg.org/
Python: https://www.python.org/
Inno Setup: https://jrsoftware.org/isinfo.php

## Contact

For questions or suggestions, open an issue or contact [prashantk4747@gmail.com]
