# YouTube Transcript Extractor

A fast, concurrent Python application for extracting transcripts from YouTube videos, channels, and playlists using Playwright. Features a simple GUI and produces clean, readable transcript files.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.7%2B-blue)
![Platform](https://img.shields.io/badge/platform-linux%20%7C%20windows-lightgrey)

## Features

- ✨ **Simple GUI** - Easy-to-use interface built with Tkinter
- ⚡ **Concurrent Processing** - Download multiple transcripts simultaneously (configurable)
- 📝 **Clean Output** - Produces both formatted and raw transcript files
- 🎯 **Multiple Input Types** - Works with single videos, channels, and playlists
- 📁 **Batch Operations** - Merge multiple transcripts into a single file
- 🚀 **Headless Operation** - Runs efficiently in the background
- 💾 **Automatic Saving** - Organized output with timestamps

## Installation

### Prerequisites

- Python 3.7 or higher
- Windows or Linux operating system
- Internet connection

---

## 🪟 Windows Installation

### Quick Install

1. **Download Python** (if not installed)
   - Go to https://www.python.org/downloads/
   - Download Python 3.7+ installer
   - ⚠️ **IMPORTANT**: Check "Add Python to PATH" during installation

2. **Download the Script**
   - Download `yt.py` from this repository
   - Or clone: `git clone https://github.com/LazyCodingKing/Bulk-Youtube-Transcript-Download.git`

3. **Open Command Prompt or PowerShell**
   ```cmd
   # Navigate to the script directory
   cd C:\path\to\youtube-transcript-extractor
   
   # Create virtual environment
   python -m venv venv
   
   # Activate virtual environment
   venv\Scripts\activate
   
   # Install playwright
   pip install playwright
   
   # Install Chromium browser
   python -m playwright install chromium
   
   # Run the application
   python yt.py
   ```

### Windows - Step by Step

#### Step 1: Install Python

1. Download from https://python.org
2. Run installer
3. ✅ **CHECK "Add Python to PATH"**
4. ✅ **CHECK "tcl/tk and IDLE"** (usually checked by default - this includes Tkinter)
5. Click "Install Now"

> **Note**: Tkinter is included with the standard Python installation on Windows. You don't need to install it separately.

#### Step 2: Download the Script

**Option A: Download ZIP**
- Click "Code" → "Download ZIP" from GitHub
- Extract to a folder like `C:\Users\YourName\youtube-transcript-extractor`

**Option B: Use Git**
```cmd
`git clone https://github.com/LazyCodingKing/Bulk-Youtube-Transcript-Download.git`
 cd youtube-transcript-extractor
```

#### Step 3: Setup Virtual Environment

Open **Command Prompt** or **PowerShell** as Administrator:

```cmd
# Navigate to script folder
cd C:\Users\YourName\youtube-transcript-extractor

# Create virtual environment
python -m venv venv

# Activate it (Command Prompt)
venv\Scripts\activate.bat

# OR Activate it (PowerShell)
venv\Scripts\Activate.ps1
```

**If you get PowerShell execution policy error:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### Step 4: Install Dependencies

```cmd
# Make sure venv is activated (you should see (venv) in prompt)
pip install playwright
python -m playwright install chromium
```

> **Note**: You only need to install `playwright`. Tkinter is already included with Python on Windows.

#### Step 5: Run the Application

```cmd
python yt.py
```

## 🐧 Linux Installation

**Make sure to use python3 instead of python if you have the latest python version**

### Quick Install (Recommended Method)

**For Modern Linux (Debian/Ubuntu/Fedora with externally-managed Python):**

```bash
# Clone the repository
git clone https://github.com/yourusername/youtube-transcript-extractor.git
cd youtube-transcript-extractor

# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install playwright
pip install playwright

# Install Chromium browser
python -m playwright install chromium

# Make script executable
chmod +x yt.py

# Run the application
python yt.py
```

**To run the app in the future:**
```bash
cd youtube-transcript-extractor
source venv/bin/activate  # Activate venv first
python yt.py
```

---


### Manual Installation (Step by Step)

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/youtube-transcript-extractor.git
cd youtube-transcript-extractor
```

### Step 2: Create Virtual Environment

**This is REQUIRED on modern Linux distributions (Debian 12+, Ubuntu 23.04+, Fedora 38+)**

```bash
# Install python3-venv if you don't have it
sudo apt install python3-venv python3-full  # Debian/Ubuntu
# OR
sudo dnf install python3  # Fedora (includes venv)

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Your prompt should now show (venv) at the start
```

### Step 3: Install Dependencies

**Inside the activated virtual environment:**

```bash
# Install playwright
pip install playwright

# Install Chromium browser
python -m playwright install chromium
```

**Tkinter Installation (Linux only):**

Tkinter is included with Python on Windows but may need to be installed separately on Linux:

**Ubuntu/Debian:**
```bash
sudo apt-get install python3-tk
```

**Fedora:**
```bash
sudo dnf install python3-tkinter
```

**Arch:**
```bash
sudo pacman -S tk
```

### Step 4: Run the Application

```bash
# Make sure venv is activated (you should see (venv) in your terminal)
python yt.py

# Or if you made it executable
./yt.py
```

### Verify Installation

```bash
# Make sure venv is activated
source venv/bin/activate

# Check if playwright is installed
python -c "import playwright; print('✓ Playwright installed successfully')"

# Check if tkinter is installed
python -c "import tkinter; print('✓ Tkinter installed successfully')"
```

### Step 3: Make the Script Executable (Optional)

```bash
chmod +x yt.py
```

## Usage

### Running the Application

**Windows:**
```cmd
cd C:\path\to\youtube-transcript-extractor
venv\Scripts\activate
python yt.py
```

**Linux:**
```bash
cd youtube-transcript-extractor
source venv/bin/activate
python yt.py
```

### Basic Workflow

1. **Enter URL**: Paste a YouTube URL into the input field:
   - Single video: `https://www.youtube.com/watch?v=VIDEO_ID`
   - Channel: `https://www.youtube.com/@channelname/videos`(**Make sure to use only the channel link ending with videos otherwise it cannot get all the videos in the channel**)
   - Playlist: `https://www.youtube.com/playlist?list=PLAYLIST_ID`

2. **Start Extraction**: Click "Start Extraction" button

3. **Monitor Progress**: Watch the progress log for real-time updates

4. **Access Files**: Click "Open Output Folder" to view downloaded transcripts

### Output Files

For each video, two files are generated:

#### 1. Clean Transcript (`VideoTitle_TIMESTAMP.txt`)
Formatted for easy reading with proper paragraphs:
```
Video: Amazing Documentary
URL: https://www.youtube.com/watch?v=...
Downloaded: 2025-11-05 10:30:45
================================================================================

This is the first sentence of the video. It continues with more information. 
The narrator explains the topic in detail. This provides great context.

Another paragraph begins here. More interesting facts are shared...
```

#### 2. Raw Transcript (`VideoTitle_TIMESTAMP_raw.txt`)
Original format with timestamps:
```
Video: Amazing Documentary
URL: https://www.youtube.com/watch?v=...
Downloaded: 2025-11-05 10:30:45
================================================================================

[0:00] This is the first sentence of the video.
[0:05] It continues with more information.
[0:12] The narrator explains the topic in detail.
```

### Additional Features

#### Change Output Folder
Click "Change Output Folder" to save transcripts to a custom location (default: `~/youtube_transcripts/`)

#### Merge Transcripts
- **Merge Selected Files**: Choose specific transcript files to combine
- **Merge All Files**: Automatically merge all transcripts in the output folder

#### Summary File
A JSON summary file is generated after each batch extraction: `summary_TIMESTAMP.json`

## Configuration

### Adjusting Concurrency

Edit the `CONCURRENT_DOWNLOADS` variable at the top of `yt.py`:

```python
# Number of videos to download at the same time
CONCURRENT_DOWNLOADS = 5  # Default: 5
```

- **Lower values (2-3)**: More stable, slower
- **Higher values (10-15)**: Faster, may cause errors on some systems
- **Recommended**: 5-7 for most use cases

### Headless Mode

The browser runs in headless mode by default. To see the browser window (for debugging):

```python
browser = await p.chromium.launch(
    headless=False,  # Change to False
    args=['--no-sandbox', '--disable-setuid-sandbox']
)
```

## Troubleshooting

### Windows-Specific Issues

**Issue**: `'python' is not recognized as an internal or external command`

**Solution**: Python not in PATH. Reinstall Python and check "Add Python to PATH", or add manually:
- Search "Environment Variables" in Windows
- Edit "Path" variable
- Add: `C:\Users\YourName\AppData\Local\Programs\Python\Python3x`

**Issue**: PowerShell won't run activate script

**Solution**: 
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Issue**: Tkinter import error on Windows

**Solution**: Tkinter is usually included with Python on Windows. If missing:
- Reinstall Python from python.org
- During installation, click "Customize installation"
- Ensure "tcl/tk and IDLE" is checked
- Complete installation

---

### Linux-Specific Issues

**Issue**: "externally-managed-environment" Error

**Issue**: `error: externally-managed-environment` when trying to install with pip3

**Solution**: Modern Linux distributions require virtual environments. Follow the installation steps above using `venv`.

```bash
# DON'T use: pip3 install playwright (this will fail)
# DO use:
python3 -m venv venv
source venv/bin/activate
pip install playwright
```

### No Transcripts Found

**Issue**: "No transcript available" messages

**Solutions**:
- Verify the video has captions/transcripts enabled on YouTube
- Try videos with auto-generated captions
- Some videos may have transcript access disabled by the creator

### Scrolling Takes Too Long

**Issue**: Channel extraction is slow

**Solutions**:
- The app scrolls until all videos are loaded (may take time for large channels)
- Default patience: stops after 5 consecutive scrolls with no new content
- Adjust `max_patience` in `extract_video_urls()` if needed

---

### General Issues

### Browser Errors

**Issue**: `ModuleNotFoundError: No module named 'playwright'`

**Solution**: Make sure you activated the virtual environment:

**Windows:**
```cmd
cd youtube-transcript-extractor
venv\Scripts\activate
python yt.py
```

**Linux:**
```bash
cd youtube-transcript-extractor
source venv/bin/activate
python yt.py
```

**Issue**: Playwright browser fails to launch

**Solutions**:

**Windows:**
```cmd
venv\Scripts\activate
python -m playwright install --force chromium
```

**Linux:**
```bash
source venv/bin/activate
python -m playwright install --force chromium
sudo python -m playwright install-deps
```

### Permission Errors

**Windows**: Run Command Prompt or PowerShell as Administrator

**Linux**:
```bash
# Check folder permissions
chmod 755 ~/youtube_transcripts

# Or change output folder in the GUI
```

## Limitations

- Only works with videos that have transcripts/captions available
- Requires active internet connection
- YouTube may rate-limit excessive requests
- Some videos may have transcript access restricted

## Technical Details

### Architecture

- **GUI Framework**: Tkinter
- **Web Automation**: Playwright (Chromium)
- **Concurrency**: Python asyncio with semaphores
- **File Handling**: Pathlib for cross-platform compatibility

### How It Works

1. **URL Detection**: Determines if input is a single video, channel, or playlist
2. **Video Extraction**: Scrolls and extracts all video links (for channels/playlists)
3. **Concurrent Processing**: Opens multiple browser contexts simultaneously
4. **Transcript Extraction**: Clicks transcript button and parses segments
5. **Formatting**: Converts segments into readable paragraphs
6. **Saving**: Writes both clean and raw versions to disk

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Ideas for Contributions

- [ ] Add support for multiple languages
- [ ] Implement transcript search functionality
- [ ] Add video metadata extraction
- [ ] Create CLI-only version
- [ ] Add progress bar visualization
- [ ] Support for other video platforms

## License

This project is licensed under the MIT License

## Disclaimer

This tool is for educational and personal use only. Please respect YouTube's Terms of Service and content creators' rights. Do not use this tool to infringe on copyrights or distribute content without permission.

## Acknowledgments

- Built with [Playwright](https://playwright.dev/)
- Built with claude ai

## Contact

For issues, questions, or suggestions, please open an issue on GitHub.

---

**Note**: This tool requires videos to have transcripts/captions enabled. It cannot generate transcripts for videos that don't have them.
