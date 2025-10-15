# Voice-Controlled System Automation

A powerful Python-based voice automation system that enables hands-free control of your computer through natural language commands. Perform web searches, download applications, manage files and folders, and control system operations using just your voice.

## Features

### Voice Recognition
- **Dual-mode STT (Speech-to-Text)**
  - Online: Whisper (GPU-accelerated) for high accuracy
  - Offline: Vosk for network-free operation
  - Automatic fallback based on network availability

### Browser Automation
- Multi-browser support (Chrome, Firefox, Brave, Edge, Chromium)
- Google search integration
- Smart application downloads (Steam, Discord, Spotify, etc.)
- Website navigation
- Automatic download button detection

### System Control
- File and folder management
- Package manager integration (apt, dnf, brew, chocolatey, etc.)
- Native app store access
- System information retrieval
- Cross-platform support (Windows, macOS, Linux)

### Audio Processing
- Real-time microphone streaming
- WebRTC Voice Activity Detection (VAD)
- Noise reduction and filtering
- Automatic noise calibration
- Energy-based speech detection

## Prerequisites

- Python 3.8 or higher
- Microphone
- Internet connection (optional, for Whisper STT)
- At least one supported browser installed

### System-Specific Requirements

**Linux:**
```bash
sudo apt install portaudio19-dev python3-dev
```

**macOS:**
```bash
brew install portaudio
```

**Windows:**
- Visual C++ Build Tools (for some dependencies)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd voice-automation
```

2. Run the main script (it will automatically set up the virtual environment):
```bash
python main.py
```

The script will automatically:
- Create a virtual environment
- Install all required dependencies
- Download necessary models
- Configure the system

### Manual Installation

If you prefer manual setup:

```bash
python -m venv venv

# Activate virtual environment
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Required Models

**Vosk Model (Offline STT):**
1. Download: [vosk-model-en-us-0.22](https://alphacephei.com/vosk/models)
2. Extract to `STT/vosk-model-en-us-0.22/`

## Usage

### Starting the System

```bash
python main.py
```

### Initial Setup

1. **Noise Calibration**: Remain silent for 3 seconds during calibration
2. **Browser Setup**: Choose whether to enable browser automation
3. **Voice Commands**: Start speaking after "Listening for speech..." appears

### Voice Commands

#### Browser Commands
```
search for [query]          - Search Google
open youtube.com            - Open website
download steam              - Download application
get discord                 - Download Discord
```

#### Installation Commands
```
install [app]               - Smart install with options
terminal install git        - Install via package manager
open app store              - Open native app store
```

#### File Operations
```
create folder MyFolder      - Create a new folder
delete folder TestFolder    - Delete a folder
create file test.txt        - Create a new file
delete file test.txt        - Delete a file
list files                  - List files in home directory
list files in Documents     - List files in specific folder
```

#### System Commands
```
system info                 - Show system information
exit                        - Quit the program
close browser               - Quit the program
```

## Project Structure

```
.
├── main.py                          # Main entry point
├── requirements.txt                 # Python dependencies
├── STT/                            # Speech-to-Text modules
│   ├── RTMicroPhone.py             # Real-time audio capture
│   ├── sttOffline.py               # Vosk offline recognition
│   ├── sttWhisper.py               # Whisper online recognition
│   └── NetworkStatus.py            # Network connectivity check
├── Browser/                        # Browser automation
│   ├── DriverManager.py            # Multi-browser driver setup
│   └── IntelligentBrowser.py       # Command parsing and execution
└── System/                         # System operations
    └── SystemController.py         # File/folder/package management
```

## Configuration

### Audio Settings (RTMicroPhone.py)

```python
fs = 16000                    # Sample rate
ENERGY_THRESHOLD = 0.015      # Speech detection threshold
MIN_SPEECH_DURATION = 0.5     # Minimum speech duration (seconds)
SILENCE_DURATION = 1.0        # Silence duration to end capture
```

### Browser Settings (DriverManager.py)

Browser priority order: Brave → Firefox → Chrome → Chromium → Edge

Modify `browsers` list in `get_default_browser_driver()` to change priority.

### Network Settings (NetworkStatus.py)

```python
check_server_connectivity("8.8.8.8", 53, 3)  # Google DNS, port 53, 3s timeout
```

## Troubleshooting

### No Browser Driver Initialized

**Solution:**
- Ensure at least one browser is installed
- Linux: `sudo apt install chromium-browser firefox`
- Check browser can run normally

### Audio Not Detected

**Solution:**
- Check microphone permissions
- Verify microphone is working: `python -m sounddevice`
- Adjust `ENERGY_THRESHOLD` if too sensitive/insensitive

### Vosk Model Not Found

**Solution:**
- Download and extract model to `STT/vosk-model-en-us-0.22/`
- Verify path matches in `sttOffline.py`

### Package Installation Fails

**Solution:**
- Install package manager (apt, brew, chocolatey)
- Run with sudo/admin privileges if needed
- Check package name is correct for your system

### GPU Not Used for Whisper

**Solution:**
- Install CUDA toolkit (NVIDIA GPUs)
- Install PyTorch with CUDA support
- For macOS: MPS backend used automatically on M1/M2

## Dependencies

### Core Libraries
- `sounddevice` - Audio capture
- `numpy` - Numerical processing
- `webrtcvad` - Voice activity detection
- `noisereduce` - Noise reduction
- `scipy` - Signal processing

### Speech Recognition
- `vosk` - Offline STT
- `transformers` - Whisper model
- `torch` - Deep learning backend

### Browser Automation
- `selenium` - Browser control
- `webdriver-manager` - Automatic driver setup

## Performance Tips

1. **Use GPU**: For Whisper, GPU acceleration significantly improves speed
2. **Network**: Online mode (Whisper) provides better accuracy
3. **Microphone**: Use quality microphone in quiet environment
4. **Calibration**: Recalibrate if environment changes significantly

## Platform Support

| Feature | Windows | macOS | Linux |
|---------|---------|-------|-------|
| Voice Recognition | ✅ | ✅ | ✅ |
| Browser Automation | ✅ | ✅ | ✅ |
| File Management | ✅ | ✅ | ✅ |
| Package Manager | Chocolatey | Homebrew | apt/dnf/etc |
| App Store | Microsoft Store | Mac App Store | GNOME/Snap |

## Known Limitations

- WhatsApp integration requires manual configuration
- Some download sites may not be automatically detected
- Package names vary across distributions
- Requires admin/sudo for system package installation

## Contributing

Contributions welcome! Areas for improvement:
- Additional browser support
- More voice command patterns
- Enhanced download detection
- Multi-language support
- Mobile app integration

## License

This project is open source and available under the MIT License.

## Acknowledgments

- OpenAI Whisper for speech recognition
- Vosk for offline STT capabilities
- Selenium for browser automation
- WebRTC for voice activity detection

## Support

For issues, questions, or suggestions, please open an issue on the project repository.

---

**Note**: This system is designed for personal use and automation. Always review commands before execution, especially those involving file deletion or system modifications.
