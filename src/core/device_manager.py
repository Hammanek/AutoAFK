"""Device connection and management module"""
import os
import sys
import io
import time
import logging
from typing import Optional, Tuple
from subprocess import Popen, PIPE, STARTUPINFO, CREATE_NO_WINDOW
from platform import system
from shutil import which

try:
    from ppadb.client import Client
    PPADB_AVAILABLE = True
except ImportError:
    PPADB_AVAILABLE = False
    Client = None  # Define as None if not available

from PIL import Image
import numpy as np

from src.core.config import Config
from src.utils.logger import Logger

logger = Logger.get_logger(__name__)


class DeviceManager:
    """Manages ADB device connection and screen capture"""
    
    def __init__(self, config: Config):
        self.config = config
        
        if not PPADB_AVAILABLE or Client is None:
            raise ImportError("ppadb (pure-python-adb) is not installed. Install it with: pip install pure-python-adb")
        
        self.adb = Client(host='127.0.0.1', port=5037)
        self.device: Optional[any] = None
        self.connected = False
        
    def connect(self) -> bool:
        """Connect to ADB device"""
        if self.connected:
            logger.info("Already connected")
            return True
        
        # Kill any hanging ADB processes first
        self._kill_adb_processes()
            
        logger.info("Attempting to connect to device...")
        
        # Start emulator if configured
        self._start_emulator_if_needed()
        
        # Configure ADB connection
        self.device = self._configure_adb()
        
        if not self.device:
            logger.error("Failed to connect to device")
            return False
            
        # Test connection with retries
        if not self._test_connection():
            return False
            
        # Verify device configuration
        self._verify_device_config()
        
        # Start AFK Arena
        logger.info("Starting AFK Arena...")
        if not self.start_afk_arena():
            logger.warning("Failed to start AFK Arena, but continuing...")
        
        self.connected = True
        logger.info(f"Device {self.device.serial} connected successfully")
        return True
        
    def _start_emulator_if_needed(self):
        """Start emulator if path is configured and not running"""
        emulator_path = self.config.get('ADVANCED', 'emulatorpath', fallback='')
        if not emulator_path or not os.path.exists(emulator_path):
            return
            
        process_name = os.path.basename(emulator_path)
        if self._is_process_running(process_name):
            logger.info("Emulator already running")
            return
            
        logger.info("Starting emulator...")
        Popen([emulator_path, '-v', '0'], 
              shell=False, 
              startupinfo=STARTUPINFO(), 
              creationflags=CREATE_NO_WINDOW)
        
        # Wait longer for emulator to start
        logger.info("Waiting for emulator to start (30 seconds)...")
        time.sleep(30)
        
        # Minimize window if on Windows
        self._minimize_window()
        
    def _configure_adb(self) -> Optional[any]:
        """Configure ADB connection using various methods"""
        # Restart ADB if configured
        if self.config.getboolean('ADVANCED', 'adbrestart', fallback=True):
            self._restart_adb()
            
        # Try configured port first
        port = self.config.getint('ADVANCED', 'port', fallback=0)
        if port and port != 5037:
            device = self._connect_to_port(port)
            if device:
                return device
                
        # Try existing devices
        for device in self.adb.devices():
            if device:
                logger.info(f"Found existing device: {device.serial}")
                return self.adb.device(device.serial)
                
        # Scan for port on Windows
        if system() == 'Windows':
            port = self._scan_for_port()
            if port:
                return self._connect_to_port(port)
                
        return None
        
    def _restart_adb(self):
        """Restart ADB server"""
        adb_path = self._get_adb_path()
        Popen([adb_path, "kill-server"], 
              stdout=PIPE, 
              startupinfo=STARTUPINFO(), 
              creationflags=CREATE_NO_WINDOW).communicate()
        Popen([adb_path, "start-server"], 
              stdout=PIPE, 
              startupinfo=STARTUPINFO(), 
              creationflags=CREATE_NO_WINDOW).communicate()
              
    def _connect_to_port(self, port: int) -> Optional[any]:
        """Connect to device on specific port"""
        adb_path = self._get_adb_path()
        device_addr = f'127.0.0.1:{port}'
        
        result = Popen([adb_path, 'connect', device_addr], 
                      stdout=PIPE, 
                      startupinfo=STARTUPINFO(), 
                      creationflags=CREATE_NO_WINDOW).communicate()[0]
                      
        if b'connected' in result:
            logger.info(f"Connected to {device_addr}")
            return self.adb.device(device_addr)
        return None
        
    def _scan_for_port(self) -> Optional[int]:
        """Scan for emulator port on Windows"""
        logger.info("Scanning for emulator port...")
        cmd = ("Get-NetTCPConnection -State Listen | "
               "Where-Object OwningProcess -eq (Get-Process hd-player | "
               "Select-Object -ExpandProperty Id) | "
               "Select-Object -ExpandProperty LocalPort")
               
        result = Popen(["powershell.exe", cmd], 
                      stdout=PIPE, 
                      startupinfo=STARTUPINFO(), 
                      creationflags=CREATE_NO_WINDOW).communicate()[0]
                      
        ports = result.decode().splitlines()
        adb_path = self._get_adb_path()
        
        for port_str in ports:
            try:
                port = int(port_str.strip())
                if port % 2 != 0:  # Odd ports only
                    device_addr = f'127.0.0.1:{port}'
                    result = Popen([adb_path, 'connect', device_addr], 
                                  stdout=PIPE, 
                                  startupinfo=STARTUPINFO(), 
                                  creationflags=CREATE_NO_WINDOW).communicate()[0]
                    if b'connected' in result:
                        logger.info(f"Found port: {port}")
                        return port
            except ValueError:
                continue
        return None
        
    def _test_connection(self, max_retries: int = 3) -> bool:
        """Test device connection with retries"""
        for attempt in range(1, max_retries + 1):
            try:
                self.device.shell('echo test')
                return True
            except Exception as e:
                error_msg = str(e)
                # Only show user-friendly message
                if 'device offline' in error_msg:
                    logger.warning(f"Device offline (attempt {attempt}/{max_retries})")
                elif 'closed' in error_msg:
                    logger.warning(f"Connection closed (attempt {attempt}/{max_retries})")
                else:
                    logger.warning(f"Connection test failed (attempt {attempt}/{max_retries})")
                if attempt < max_retries:
                    time.sleep(2)
        return False
        
    def _verify_device_config(self):
        """Verify device resolution and DPI"""
        resolution = self.device.shell('wm size')
        dpi = self.device.shell('wm density')
        
        logger.debug(f"Resolution: {resolution}")
        logger.debug(f"DPI: {dpi}")
        
        # Check for 1920x1080 or 1080x1920
        if '1920x1080' not in resolution and '1080x1920' not in resolution:
            logger.warning("Non-standard resolution detected. Image scaling will be applied.")
            
    def get_screenshot(self) -> Image.Image:
        """Get current screen as PIL Image using ADB screencap"""
        try:
            # Use ADB screencap - fastest and most reliable method
            result = self.device.screencap()
            if result:
                img = Image.open(io.BytesIO(result))
                
                # Resize if needed to standard resolution
                if img.size not in [(1080, 1920), (1920, 1080)]:
                    img = img.resize((1080, 1920), Image.Resampling.LANCZOS)
                
                return img
            
            # Return black image if screencap fails
            logger.warning("Screenshot failed, returning black image")
            return Image.new('RGB', (1080, 1920), color='black')
            
        except Exception as e:
            logger.error(f"Screenshot error: {e}")
            return Image.new('RGB', (1080, 1920), color='black')
            
    def get_screenshot_array(self) -> np.ndarray:
        """Get current screen as numpy array"""
        return np.asarray(self.get_screenshot())
        
    def tap(self, x: int, y: int) -> None:
        """Tap at coordinates"""
        self.device.input_tap(x, y)
        
    def swipe(self, x1: int, y1: int, x2: int, y2: int, duration: int = 100) -> None:
        """Swipe from (x1,y1) to (x2,y2)"""
        self.device.shell(f"input swipe {x1} {y1} {x2} {y2} {duration}")
        
    def long_press(self, x: int, y: int, duration_ms: int = 1000) -> None:
        """Long press at coordinates"""
        self.device.shell(f"input swipe {x} {y} {x} {y} {duration_ms}")
        
    def shell(self, command: str) -> str:
        """Execute shell command on device"""
        return self.device.shell(command)
        
    def is_app_running(self, package_name: str) -> bool:
        """Check if app is running"""
        try:
            result = self.shell(f'dumpsys meminfo {package_name}')
            return 'No process found' not in result
        except:
            result = self.shell('ps')
            return package_name in result
            
    def start_app(self, package_name: str, max_attempts: int = 15) -> bool:
        """Start app with retries"""
        if self.is_app_running(package_name):
            logger.info("App already running")
            return True
            
        logger.info(f"Starting app {package_name}...")
        for attempt in range(1, max_attempts + 1):
            logger.info(f"Launch attempt {attempt}/{max_attempts}")
            self.shell(f'monkey -p {package_name} 1')
            
            # Quick check after 2 seconds
            time.sleep(2)
            if self.is_app_running(package_name):
                logger.info(f"App launched successfully on attempt {attempt}")
                return True
            
            # If not running yet, wait a bit more before retry
            if attempt < max_attempts:
                time.sleep(3)  # Total 5 seconds between attempts
                
        logger.error("Failed to launch app")
        return False
        
    def start_afk_arena(self, test_mode: bool = False) -> bool:
        """Start AFK Arena with proper package name"""
        package_name = 'com.lilithgames.hgame.gp.id' if test_mode else 'com.lilithgame.hgame.gp'
        return self.start_app(package_name)
        
    def disconnect(self) -> None:
        """Disconnect from device"""
        self.connected = False
        logger.info("Disconnected from device")
    
    def _kill_adb_processes(self):
        """Kill any hanging ADB processes"""
        try:
            logger.info("Cleaning up ADB processes...")
            adb_path = self._get_adb_path()
            
            # Kill ADB server and wait for completion
            proc = Popen([adb_path, "kill-server"], 
                  stdout=PIPE, 
                  stderr=PIPE,
                  startupinfo=STARTUPINFO(), 
                  creationflags=CREATE_NO_WINDOW)
            proc.communicate(timeout=5)
            proc.wait()
            
            # On Windows, also kill any hanging adb.exe processes
            if system() == 'Windows':
                try:
                    proc = Popen(['taskkill', '/F', '/IM', 'adb.exe'], 
                          stdout=PIPE, 
                          stderr=PIPE,
                          startupinfo=STARTUPINFO(), 
                          creationflags=CREATE_NO_WINDOW)
                    proc.communicate(timeout=5)
                    proc.wait()
                except:
                    pass
            
            # Wait a moment for file handles to release
            time.sleep(1.5)
            logger.info("ADB processes cleaned up")
        except Exception as e:
            logger.debug(f"Could not kill ADB processes: {e}")
        
    @staticmethod
    def _get_adb_path() -> str:
        """Get ADB executable path"""
        # For compiled version (--onedir), adb.exe is in same folder as EXE
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            exe_dir = os.path.dirname(sys.executable)
            adb_path = os.path.join(exe_dir, 'adb.exe')
            if os.path.exists(adb_path):
                return adb_path
        
        # Try local adb.exe (for development)
        cwd = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        adb_path = os.path.join(cwd, 'adb.exe')
        
        if os.path.exists(adb_path):
            return adb_path
        
        # Try system adb
        adb_path = which('adb')
        if adb_path:
            return adb_path
        
        # Fallback to 'adb' and hope it's in PATH
        return 'adb'
        return 'adb'
        
    @staticmethod
    def _is_process_running(process_name: str) -> bool:
        """Check if process is running"""
        import psutil
        for proc in psutil.process_iter(['name']):
            if proc.info['name'] == process_name:
                return True
        return False
        
    @staticmethod
    def _minimize_window():
        """Minimize emulator window on Windows"""
        if system() != 'Windows':
            return
            
        try:
            import win32gui
            import win32con
            
            def callback(hwnd, windows):
                if win32gui.IsWindowVisible(hwnd):
                    title = win32gui.GetWindowText(hwnd)
                    if 'BlueStacks' in title or 'HD-Player' in title:
                        win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
                        
            win32gui.EnumWindows(callback, None)
        except Exception as e:
            logger.debug(f"Could not minimize window: {e}")
