#!/usr/bin/env python3
"""
Python API Server for EitherAssistant
Provides HTTP API endpoints for voice recognition, command processing, and system control
"""

import sys
import os
import json
import asyncio
import threading
import queue
import time
from pathlib import Path
from typing import Dict, Any, Optional
import logging

# Add the Python directory to the path
sys.path.append(str(Path(__file__).parent))

# Import our modules
from STT.RTMicroPhone import stream_microPhone, SpeechDetector
from STT.sttOffline import stt_vosk
from STT.sttWhisper import stt_whisper
from STT.NetworkStatus import check_server_connectivity
from Browser.DriverManager import setup_driver
from Browser.IntelligentBrowser import process_voice_command, EnhancedIntelligentBrowser
from System.SystemController import SystemController

# FastAPI imports
try:
    from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
    from contextlib import asynccontextmanager
except ImportError:
    print("Installing required packages...")
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "fastapi", "uvicorn", "websockets"], check=True)
    from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
    from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables
browser_driver = None
system_controller = None
voice_queue = queue.Queue()
websocket_connections = set()
is_listening = False
speech_detector = None

# Pydantic models
class VoiceCommand(BaseModel):
    command: str

class SystemStatus(BaseModel):
    status: str
    message: str
    timestamp: float

class CommandResponse(BaseModel):
    success: bool
    message: str
    result: Optional[Dict[str, Any]] = None

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                # Remove dead connections
                self.active_connections.remove(connection)

manager = ConnectionManager()

# Initialize system components
def initialize_system():
    global system_controller, browser_driver, speech_detector
    
    logger.info("Initializing system components...")
    
    # Initialize system controller
    system_controller = SystemController()
    logger.info("System controller initialized")
    
    # Initialize speech detector
    speech_detector = SpeechDetector()
    logger.info("Speech detector initialized")
    
    # Check network connectivity
    network_available = check_server_connectivity("8.8.8.8", 53, 3)
    if network_available:
        logger.info("Network available - Whisper STT enabled")
    else:
        logger.info("Network unavailable - Vosk STT enabled")
    
    # Get system info
    system_controller.get_system_info()
    logger.info("System initialization complete")

# Voice processing function
def process_voice_input(audio_np):
    """Process voice input and send results via WebSocket"""
    global browser_driver, system_controller, speech_detector
    
    try:
        # Determine STT method based on network availability
        network_available = check_server_connectivity("8.8.8.8", 53, 3)
        
        if network_available:
            transcription = stt_whisper(audio_np)
        else:
            transcription = stt_vosk(audio_np)
        
        if transcription and transcription.strip():
            logger.info(f"Voice input: {transcription}")
            
            # Send transcription to WebSocket clients
            asyncio.create_task(manager.broadcast(json.dumps({
                "type": "voice_transcription",
                "text": transcription,
                "timestamp": time.time()
            })))
            
            # Process command if browser and system controller are available
            if browser_driver and system_controller:
                result = process_voice_command(browser_driver, system_controller, transcription)
                if result == "EXIT":
                    browser_driver = None
            elif system_controller:
                # Use dummy driver for system-only commands
                class DummyDriver:
                    def get(self, url): pass
                    def quit(self): pass
                
                dummy = DummyDriver()
                temp_browser = EnhancedIntelligentBrowser(dummy, system_controller)
                temp_browser.execute_command(transcription)
            
            # Send command result
            asyncio.create_task(manager.broadcast(json.dumps({
                "type": "command_result",
                "text": transcription,
                "result": "Command processed",
                "timestamp": time.time()
            })))
        
        return transcription
    except Exception as e:
        logger.error(f"Error processing voice input: {e}")
        asyncio.create_task(manager.broadcast(json.dumps({
            "type": "error",
            "message": str(e),
            "timestamp": time.time()
        })))
        return None

# Background voice listening task
def start_voice_listening():
    """Start voice listening in a separate thread"""
    global is_listening
    
    if is_listening:
        return
    
    is_listening = True
    logger.info("Starting voice recognition...")
    
    def voice_thread():
        try:
            stream_microPhone(process_voice_input, buffer_seconds=3)
        except Exception as e:
            logger.error(f"Voice recognition error: {e}")
        finally:
            is_listening = False
    
    thread = threading.Thread(target=voice_thread, daemon=True)
    thread.start()

# FastAPI application
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    initialize_system()
    yield
    # Shutdown
    if browser_driver:
        try:
            browser_driver.quit()
        except:
            pass

app = FastAPI(
    title="EitherAssistant API",
    description="Voice-controlled system automation API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routes
@app.get("/")
async def root():
    return {"message": "EitherAssistant API Server", "status": "running"}

@app.get("/status")
async def get_status():
    """Get system status"""
    return {
        "status": "online",
        "voice_listening": is_listening,
        "browser_enabled": browser_driver is not None,
        "system_controller": system_controller is not None,
        "timestamp": time.time()
    }

@app.post("/voice/start")
async def start_voice():
    """Start voice recognition"""
    global is_listening
    
    if not is_listening:
        start_voice_listening()
        return {"success": True, "message": "Voice recognition started"}
    else:
        return {"success": True, "message": "Voice recognition already running"}

@app.post("/voice/stop")
async def stop_voice():
    """Stop voice recognition"""
    global is_listening
    
    is_listening = False
    return {"success": True, "message": "Voice recognition stopped"}

@app.post("/command")
async def process_command(command: VoiceCommand):
    """Process a text command"""
    global browser_driver, system_controller
    
    try:
        if system_controller:
            if browser_driver:
                result = process_voice_command(browser_driver, system_controller, command.command)
            else:
                # Use dummy driver for system-only commands
                class DummyDriver:
                    def get(self, url): pass
                    def quit(self): pass
                
                dummy = DummyDriver()
                temp_browser = EnhancedIntelligentBrowser(dummy, system_controller)
                temp_browser.execute_command(command.command)
                result = "Command processed"
            
            return CommandResponse(
                success=True,
                message="Command processed successfully",
                result={"output": result}
            )
        else:
            return CommandResponse(
                success=False,
                message="System controller not initialized"
            )
    except Exception as e:
        logger.error(f"Error processing command: {e}")
        return CommandResponse(
            success=False,
            message=f"Error: {str(e)}"
        )

@app.post("/browser/enable")
async def enable_browser():
    """Enable browser automation"""
    global browser_driver
    
    try:
        if not browser_driver:
            browser_driver = setup_driver()
            if browser_driver:
                return {"success": True, "message": "Browser automation enabled"}
            else:
                return {"success": False, "message": "Failed to initialize browser"}
        else:
            return {"success": True, "message": "Browser already enabled"}
    except Exception as e:
        logger.error(f"Error enabling browser: {e}")
        return {"success": False, "message": f"Error: {str(e)}"}

@app.post("/browser/disable")
async def disable_browser():
    """Disable browser automation"""
    global browser_driver
    
    try:
        if browser_driver:
            browser_driver.quit()
            browser_driver = None
            return {"success": True, "message": "Browser automation disabled"}
        else:
            return {"success": True, "message": "Browser already disabled"}
    except Exception as e:
        logger.error(f"Error disabling browser: {e}")
        return {"success": False, "message": f"Error: {str(e)}"}

@app.get("/system/info")
async def get_system_info():
    """Get system information"""
    if system_controller:
        return {
            "success": True,
            "info": system_controller.get_system_info()
        }
    else:
        return {"success": False, "message": "System controller not initialized"}

# WebSocket endpoint for real-time communication
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    
    # Check if we're in a virtual environment
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("Warning: Not running in a virtual environment")
        print("Consider running: python -m venv venv && source venv/bin/activate")
    
    print("Starting EitherAssistant API Server...")
    print("API will be available at: http://localhost:8000")
    print("WebSocket endpoint: ws://localhost:8000/ws")
    print("API documentation: http://localhost:8000/docs")
    
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )
