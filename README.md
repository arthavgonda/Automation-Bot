# EitherAssistant

An AI-powered voice assistant application built with Avalonia UI (C#) frontend and Python backend, featuring real-time speech recognition, intelligent browser automation, and system control capabilities.

## 🚀 Features

### Frontend (C# Avalonia UI)
- **Modern Cross-platform UI**: Built with Avalonia UI framework
- **Real-time Communication**: WebSocket support for live voice streaming
- **Settings Management**: User-friendly configuration interface
- **Message Display**: Real-time feedback and status updates
- **Cross-platform**: Runs on Windows, macOS, and Linux

### Backend (Python Voice Automation)
- **Dual-mode STT (Speech-to-Text)**
  - Online: Whisper (GPU-accelerated) for high accuracy
  - Offline: Vosk for network-free operation
  - Automatic fallback based on network availability
- **Multi-browser Automation**: Chrome, Firefox, Brave, Edge, Chromium support
- **Smart System Control**: File management, package installation, app store access
- **Real-time Audio Processing**: WebRTC VAD, noise reduction, automatic calibration
- **RESTful API**: Comprehensive API for voice processing and automation

## 📁 Project Structure

```
EitherAssistant/
├── EitherAssistant/          # C# Avalonia UI Frontend
│   ├── Assets/              # Application icons and images
│   ├── Converters/          # UI data converters
│   ├── Models/              # Data models
│   ├── Services/            # Frontend services
│   ├── ViewModels/          # MVVM view models
│   ├── Views/               # UI views (XAML)
│   └── EitherAssistant.csproj
├── Python/                  # Python Backend
│   ├── STT/                 # Speech-to-Text modules
│   │   ├── RTMicroPhone.py  # Real-time microphone processing
│   │   ├── sttOffline.py     # Vosk offline STT
│   │   ├── sttWhisper.py     # Whisper online STT
│   │   └── vosk-model-en-us-0.22/  # Vosk model files
│   ├── Browser/             # Browser automation
│   │   ├── DriverManager.py  # WebDriver management
│   │   └── IntelligentBrowser.py  # Smart browser control
│   ├── System/              # System control
│   │   └── SystemController.py
│   ├── api_server.py        # Main FastAPI server
│   └── requirements.txt     # Python dependencies
└── FinalApp/                # Compiled binaries
    ├── EitherAssistant.exe   # Windows executable
    ├── EitherAssistant-1.0.0-Linux.deb  # Linux package
    ├── EitherAssistant-1.0.0-x86_64.AppImage  # Linux AppImage
    └── EitherAssistant.app/ # macOS application
```

## 🛠️ Prerequisites

### System Requirements
- **Windows**: Windows 10/11 (x64)
- **macOS**: macOS 10.15+ (Intel/Apple Silicon)
- **Linux**: Ubuntu 20.04+ or equivalent (x64)
- **Microphone**: Required for voice input
- **Internet connection**: Optional (for Whisper STT)

### Development Tools
- **.NET 8.0 SDK** (for C# frontend)
- **Python 3.8+** (for backend)
- **Git** (for version control)
- **At least one supported browser** (Chrome, Firefox, Brave, Edge, Chromium)

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

## 📦 Installation

### Option 1: Using Pre-built Binaries (Recommended)

1. **Download** the appropriate binary from the `FinalApp/` directory:
   - **Windows**: `EitherAssistant.exe`
   - **Linux**: `EitherAssistant-1.0.0-Linux.deb` or `EitherAssistant-1.0.0-x86_64.AppImage`
   - **macOS**: `EitherAssistant.app`

2. **Install**:
   - **Windows**: Run `EitherAssistant.exe`
   - **Linux**: 
     ```bash
     # For .deb package
     sudo dpkg -i EitherAssistant-1.0.0-Linux.deb
     
     # For AppImage
     chmod +x EitherAssistant-1.0.0-x86_64.AppImage
     ./EitherAssistant-1.0.0-x86_64.AppImage
     ```
   - **macOS**: Mount and drag `EitherAssistant.app` to Applications

### Option 2: Build from Source

#### Frontend (C# Avalonia)

1. **Install .NET 8.0 SDK**:
   ```bash
   # Ubuntu/Debian
   wget https://packages.microsoft.com/config/ubuntu/22.04/packages-microsoft-prod.deb -O packages-microsoft-prod.deb
   sudo dpkg -i packages-microsoft-prod.deb
   sudo apt-get update
   sudo apt-get install -y dotnet-sdk-8.0
   
   # Windows (using winget)
   winget install Microsoft.DotNet.SDK.8
   
   # macOS (using Homebrew)
   brew install --cask dotnet-sdk
   ```

2. **Build the application**:
   ```bash
   cd EitherAssistant
   dotnet restore
   dotnet build
   dotnet publish -c Release -r win-x64 --self-contained true
   ```

#### Backend (Python)

1. **Install Python 3.8+**:
   ```bash
   # Ubuntu/Debian
   sudo apt update
   sudo apt install python3.8 python3.8-venv python3.8-pip
   
   # Windows (using winget)
   winget install Python.Python.3.8
   
   # macOS (using Homebrew)
   brew install python@3.8
   ```

2. **Set up Python environment**:
   ```bash
   cd Python
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   pip install torch  # Additional dependency for Whisper
   ```

3. **Download Required Models**:
   ```bash
   # Vosk Model (Offline STT)
   # Download: https://alphacephei.com/vosk/models
   # Extract to: STT/vosk-model-en-us-0.22/
   ```

## 🚀 Running the Application

### Start the Backend Server

1. **Navigate to Python directory**:
   ```bash
   cd Python
   ```

2. **Activate virtual environment**:
   ```bash
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Start the API server**:
   ```bash
   python3 api_server.py
   ```

   The server will start on `http://localhost:8000` with:
   - **API Documentation**: `http://localhost:8000/docs`
   - **WebSocket Endpoint**: `ws://localhost:8000/ws`
   - **Health Check**: `http://localhost:8000/health`

### Backend Initial Setup

1. **Noise Calibration**: Remain silent for 3 seconds during calibration
2. **Browser Setup**: Choose whether to enable browser automation
3. **Voice Commands**: Start speaking after "Listening for speech..." appears

### Start the Frontend Application

1. **Run the compiled application**:
   ```bash
   # From FinalApp directory
   ./EitherAssistant.exe        # Windows
   ./EitherAssistant-1.0.0-x86_64.AppImage  # Linux
   open EitherAssistant.app     # macOS
   ```

   Or if building from source:
   ```bash
   cd EitherAssistant
   dotnet run
   ```

## 🔧 Configuration

### Backend Configuration

The Python backend can be configured through environment variables:

```bash
# API Server Settings
export API_HOST=0.0.0.0
export API_PORT=8000
export LOG_LEVEL=INFO

# Speech Recognition Settings
export STT_METHOD=vosk  # or 'whisper'
export VOSK_MODEL_PATH=./STT/vosk-model-en-us-0.22
export WHISPER_MODEL=base

# Browser Settings
export BROWSER_HEADLESS=false
export BROWSER_TIMEOUT=30
```

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

### Frontend Configuration

Settings can be modified through the application's settings window or by editing configuration files in the user's application data directory.

## 📡 API Endpoints

### REST API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/api/voice/process` | POST | Process voice command |
| `/api/browser/navigate` | POST | Navigate to URL |
| `/api/browser/click` | POST | Click element |
| `/api/browser/type` | POST | Type text |
| `/api/system/command` | POST | Execute system command |
| `/api/settings` | GET/POST | Get/update settings |

### WebSocket

- **Endpoint**: `ws://localhost:8000/ws`
- **Purpose**: Real-time voice streaming and command processing
- **Message Format**: JSON with `type` and `data` fields

## 🎤 Voice Commands

### Browser Commands
```
search for [query]          - Search Google
open youtube.com            - Open website
download steam              - Download application
get discord                 - Download Discord
click [element]             - Click on page elements
type [text]                 - Enter text in forms
scroll up/down              - Scroll the page
go back/forward             - Navigate browser history
```

### Installation Commands
```
install [app]               - Smart install with options
terminal install git        - Install via package manager
open app store              - Open native app store
```

### File Operations
```
create folder MyFolder      - Create a new folder
delete folder TestFolder    - Delete a folder
create file test.txt        - Create a new file
delete file test.txt        - Delete a file
list files                  - List files in home directory
list files in Documents     - List files in specific folder
```

### System Commands
```
system info                 - Show system information
exit                        - Quit the program
close browser               - Quit the program
open [application]          - Launch applications
close [application]         - Close applications
volume up/down              - Control system volume
brightness up/down          - Adjust screen brightness
```

## 🐛 Troubleshooting

### Common Issues

1. **"ModuleNotFoundError: No module named 'torch'"**
   ```bash
   pip install torch
   ```

2. **"Command 'python' not found"**
   ```bash
   # Use python3 instead
   python3 api_server.py
   ```

3. **"Port 8000 already in use"**
   ```bash
   # Kill existing process
   lsof -ti:8000 | xargs kill -9
   ```

4. **No Browser Driver Initialized**
   - Ensure at least one browser is installed
   - Linux: `sudo apt install chromium-browser firefox`
   - Check browser can run normally

5. **Audio Not Detected**
   - Check microphone permissions
   - Verify microphone is working: `python -m sounddevice`
   - Adjust `ENERGY_THRESHOLD` if too sensitive/insensitive

6. **Vosk Model Not Found**
   - Download and extract model to `STT/vosk-model-en-us-0.22/`
   - Verify path matches in `sttOffline.py`

7. **Package Installation Fails**
   - Install package manager (apt, brew, chocolatey)
   - Run with sudo/admin privileges if needed
   - Check package name is correct for your system

8. **GPU Not Used for Whisper**
   - Install CUDA toolkit (NVIDIA GPUs)
   - Install PyTorch with CUDA support
   - For macOS: MPS backend used automatically on M1/M2

### Logs and Debugging

- **Backend logs**: Check console output when running `api_server.py`
- **Frontend logs**: Check application logs in user data directory
- **WebSocket connection**: Use browser developer tools to inspect WebSocket messages

## 📦 Dependencies

### Backend Dependencies

#### Core Libraries
- `sounddevice` - Audio capture
- `numpy` - Numerical processing
- `webrtcvad` - Voice activity detection
- `noisereduce` - Noise reduction
- `scipy` - Signal processing

#### Speech Recognition
- `vosk` - Offline STT
- `transformers` - Whisper model
- `torch` - Deep learning backend

#### Browser Automation
- `selenium` - Browser control
- `webdriver-manager` - Automatic driver setup

#### Web Framework
- `fastapi` - Modern Python web framework
- `uvicorn` - ASGI server
- `websockets` - WebSocket support
- `pydantic` - Data validation

### Frontend Dependencies

#### .NET Packages
- `Avalonia` - Cross-platform UI framework
- `Avalonia.Desktop` - Desktop platform support
- `Avalonia.Themes.Fluent` - Fluent Design theme
- `Avalonia.ReactiveUI` - Reactive UI patterns
- `CommunityToolkit.Mvvm` - MVVM toolkit
- `Newtonsoft.Json` - JSON serialization

## ⚡ Performance Tips

1. **Use GPU**: For Whisper, GPU acceleration significantly improves speed
2. **Network**: Online mode (Whisper) provides better accuracy
3. **Microphone**: Use quality microphone in quiet environment
4. **Calibration**: Recalibrate if environment changes significantly
5. **Browser Priority**: Configure browser priority for optimal performance

## 🌐 Platform Support

| Feature | Windows | macOS | Linux |
|---------|---------|-------|-------|
| Voice Recognition | ✅ | ✅ | ✅ |
| Browser Automation | ✅ | ✅ | ✅ |
| File Management | ✅ | ✅ | ✅ |
| Package Manager | Chocolatey | Homebrew | apt/dnf/etc |
| App Store | Microsoft Store | Mac App Store | GNOME/Snap |
| Frontend UI | ✅ | ✅ | ✅ |

## ⚠️ Known Limitations

- WhatsApp integration requires manual configuration
- Some download sites may not be automatically detected
- Package names vary across distributions
- Requires admin/sudo for system package installation
- GPU acceleration requires CUDA toolkit on NVIDIA systems

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature-name`
3. **Make your changes**
4. **Test thoroughly**
5. **Submit a pull request**

### Development Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd EitherAssistant
   ```

2. **Set up development environment**:
   ```bash
   # Backend
   cd Python
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   pip install torch
   
   # Frontend
   cd ../EitherAssistant
   dotnet restore
   ```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Avalonia UI** - Cross-platform UI framework
- **FastAPI** - Modern Python web framework
- **Vosk** - Offline speech recognition
- **Whisper** - OpenAI's speech recognition model
- **Selenium** - Browser automation framework
- **WebRTC** - Voice activity detection
- **OpenAI Whisper** - High-accuracy speech recognition
- **PyTorch** - Deep learning framework

## 📞 Support

For support, feature requests, or bug reports:
- Create an issue on GitHub
- Check the troubleshooting section
- Review the API documentation at `http://localhost:8000/docs`

---

**Version**: 1.0.0  
**Last Updated**: October, 2025
