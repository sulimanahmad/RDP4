import os
import subprocess
import sys
import time
import random  # This is a built-in module, safe to import

def install_dependencies():
    """Install required packages if not already installed"""
    print("Installing required dependencies...")
    packages = [
        "selenium", "pynput", "opencv-python", "pillow", 
        "numpy", "requests", "psutil", "pyautogui", "pygetwindow"
    ]
    
    for package in packages:
        try:
            __import__(package.split('-')[0])  # Try to import to check if installed
            print(f"{package} is already installed")
        except ImportError:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"Successfully installed {package}")
        except Exception as e:
            print(f"Error installing {package}: {e}. Continuing...")
            
    
    print("Dependency installation process completed!")

# Install dependencies first
install_dependencies()

# Now import all required modules after installation
import requests
import psutil
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import pyautogui
import pygetwindow as gw

# ... rest of your code remains the same ...

# Import all required modules after installation
import random
import requests
import psutil
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import pyautogui
import pygetwindow as gw

# ==================== WARP SETUP FUNCTIONS ====================
def setup_download_folder():
    """Create a dedicated download folder and return its path"""
    download_path = os.path.join(os.getcwd(), "warp_downloads")
    if not os.path.exists(download_path):
        os.makedirs(download_path)
    return download_path

def configure_chrome_options(download_path):
    """Configure Chrome options to allow unverified downloads"""
    chrome_options = Options()
    
    # Set download preferences
    prefs = {
        "download.default_directory": download_path,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
        "safebrowsing.disable_download_protection": True,
    }
    chrome_options.add_experimental_option("prefs", prefs)
    
    # Add arguments to handle security warnings
    chrome_options.add_argument("--safebrowsing-disable-download-protection")
    chrome_options.add_argument("--safebrowsing-disable-extension-blacklist")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--allow-running-insecure-content")
    
    # Run in background (without visible browser window)
    chrome_options.add_argument("--headless")
    
    return chrome_options

def wait_for_download_completion(download_path, max_wait_time=120):
    """Wait for download to complete and return the downloaded file path"""
    print("Waiting for download to complete...")
    start_time = time.time()
    downloaded_file = None
    
    while time.time() - start_time < max_wait_time:
        time.sleep(2)
        # Check if any files exist in the download directory
        files = os.listdir(download_path)
        if files and not any(f.endswith('.crdownload') for f in files):
            # Get the most recently modified file
            downloaded_file = max([os.path.join(download_path, f) for f in files], key=os.path.getctime)
            print(f"Download completed! File: {downloaded_file}")
            return downloaded_file
            
        # Check if there are partially downloaded files (.crdownload)
        if any(f.endswith('.crdownload') for f in files):
            print("Download in progress...")
    
    print("Download may not have completed within the expected time")
    return None

def is_warp_installed():
    """Check if Warp is already installed"""
    try:
        # Check registry for Warp installation
        import winreg
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Cloudflare WARP")
            winreg.CloseKey(key)
            return True
        except FileNotFoundError:
            pass
        
        # Check if Warp process is running
        for proc in psutil.process_iter(['name']):
            if 'warp' in proc.info['name'].lower():
                return True
                
        # Check program files directory
        program_files = os.environ.get("ProgramFiles", "C:\\Program Files")
        warp_path = os.path.join(program_files, "Cloudflare", "Cloudflare WARP")
        if os.path.exists(warp_path):
            return True
            
    except Exception as e:
        print(f"Error checking installation: {e}")
    
    return False

def install_warp_windows(installer_path):
    """Silently install Warp on Windows with multiple approaches"""
    print("Starting silent installation on Windows...")
    
    # Try different installation methods
    methods = [
        # Method 1: Standard MSI installation
        (['msiexec', '/i', installer_path, '/quiet', '/norestart', '/log', 'warp_install.log'], "Standard MSI installation"),
        
        # Method 2: MSI with passive UI
        (['msiexec', '/i', installer_path, '/passive', '/norestart', '/log', 'warp_install.log'], "Passive MSI installation"),
        
        # Method 3: Try with different privilege levels
        (['msiexec', '/i', installer_path, '/quiet', '/norestart', '/log', 'warp_install.log'], "MSI installation with logging"),
    ]
    
    for method_args, method_name in methods:
        print(f"Trying {method_name}...")
        try:
            result = subprocess.run(method_args, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print("Warp installed successfully!")
                return True
            else:
                print(f"Installation failed with return code: {result.returncode}")
                if os.path.exists('warp_install.log'):
                    with open('warp_install.log', 'r') as f:
                        log_content = f.read()
                        print(f"Installation log: {log_content[:500]}...")  # First 500 chars
                
                # Check if it's already installed error
                if result.returncode == 1605 or "already installed" in result.stderr.lower():
                    print("Warp might already be installed.")
                    if is_warp_installed():
                        print("Confirmed: Warp is already installed.")
                        return True
                        
        except subprocess.TimeoutExpired:
            print("Installation timed out after 5 minutes")
        except Exception as e:
            print(f"Error during installation: {e}")
    
    # If all methods failed, try a direct approach with the installer
    print("Trying direct installer execution...")
    try:
        result = subprocess.run([installer_path, '/S'], capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            print("Warp installed successfully via direct installer!")
            return True
    except Exception as e:
        print(f"Direct installer also failed: {e}")
    
    return False

def wait_for_warp_ui():
    """Wait for Warp UI to appear after installation"""
    print("Waiting for Warp UI to appear...")
    max_wait_time = 60
    start_time = time.time()
    warp_detected = False
    
    while time.time() - start_time < max_wait_time:
        try:
            # Look for Warp window with various possible titles
            warp_titles = ['WARP', 'Cloudflare', 'Cloudflare WARP']
            for title in warp_titles:
                warp_windows = gw.getWindowsWithTitle(title)
                if warp_windows:
                    print(f"Warp UI detected with title: {title}!")
                    warp_detected = True
                    # Bring the window to front and wait for it to stabilize
                    try:
                        warp_windows[0].activate()
                        time.sleep(3)  # Wait for window to fully load and stabilize
                    except:
                        pass
                    return True
        except Exception as e:
            print(f"Error detecting Warp UI: {e}")
        
        time.sleep(2)
    
    print("Warp UI did not appear within expected time")
    return False

def connect_warp_cli():
    """Connect to WARP using command line interface"""
    try:
        # Try to connect using WARP CLI
        program_files = os.environ.get("ProgramFiles", "C:\\Program Files")
        warp_cli_path = os.path.join(program_files, "Cloudflare", "Cloudflare WARP", "warp-cli.exe")
        
        if os.path.exists(warp_cli_path):
            print("Found WARP CLI, attempting to connect...")
            
            # Check status first
            result = subprocess.run([warp_cli_path, 'status'], capture_output=True, text=True)
            print(f"Current status: {result.stdout}")
            
            # Connect to WARP
            result = subprocess.run([warp_cli_path, 'connect'], capture_output=True, text=True)
            if result.returncode == 0:
                print("WARP connected successfully via CLI!")
                return True
            else:
                print(f"CLI connect failed: {result.stderr}")
                return False
        else:
            print("WARP CLI not found")
            return False
            
    except Exception as e:
        print(f"Error using WARP CLI: {e}")
        return False

def complete_initial_setup():
    """Complete the initial setup of Warp automatically"""
    print("Starting automatic setup completion...")
    
    # Wait for the Warp UI to appear
    if not wait_for_warp_ui():
        print("Could not find Warp UI, attempting to start it manually...")
        try:
            # Try to start Warp manually
            program_files = os.environ.get("ProgramFiles", "C:\\Program Files")
            warp_exe_path = os.path.join(program_files, "Cloudflare", "Cloudflare WARP", "Cloudflare WARP.exe")
            subprocess.Popen([warp_exe_path])
            time.sleep(5)
            
            # Wait again for UI
            if not wait_for_warp_ui():
                print("Failed to start Warp UI automatically")
                return False
        except Exception as e:
            print(f"Error starting Warp manually: {e}")
            
    print("Proceeding with WARP conncting.")
    try:
        # Give the UI time to stabilize
        time.sleep(5)
        
        # Press Tab multiple times to navigate to the "Get Started" button
        # The exact number of tabs needed may vary based on the UI version
        #pyautogui.press('tab', presses=3)
        #time.sleep(1)
        
        # Press Enter to click the "Get Started" button
        pyautogui.press('enter')
        time.sleep(3)                      
        
        
        pyautogui.press('enter')  # Press Enter to accept
        print("Used keyboard navigation to accept")
        time.sleep(8)
        
        # Wait for the next screen and navigate to the connect button        
        if connect_warp_cli():
            return True
        
        # Use keyboard to activate whatever is under cursor
        # Method 1: Space key (usually works for buttons)
        
        
        #return True
        
    except Exception as e:
        print(f"Error during automatic setup: {e}")
        return False

def download_and_install_warp():
    """Main function to download and install Warp automatically"""
    print("Starting automated Warp download and installation process...")
    
    # Check if already installed first
    if is_warp_installed():
        print("Warp is already installed. Launching and connecting...")
        # Try to complete setup if already installed
        complete_initial_setup()
        return True
    
    # Set up download folder
    download_path = setup_download_folder()
    print(f"Downloads will be saved to: {download_path}")
    
    # Configure Chrome options
    chrome_options = configure_chrome_options(download_path)
    
    # Initialize the driver
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # Navigate to the website
        print("Navigating to https://one.one.one.one/")
        driver.get("https://one.one.one.one/")
        
        # Wait for page to load
        wait = WebDriverWait(driver, 30)
        
        # Wait for and click the download button
        print("Looking for download button...")
        download_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div[1]/div[1]/div[4]/div[2]/a[1]"))
        )
        
        print("Clicking download button...")
        download_button.click()
        print("Download started successfully!")
        
        # Wait for download to complete
        installer_path = wait_for_download_completion(download_path)
        
        if installer_path and os.path.exists(installer_path):
            # Install Warp
            if install_warp_windows(installer_path):
                print("Warp installation completed successfully!")
                
                # Complete the initial setup automatically
                if complete_initial_setup():
                    print("Warp setup completed and connected successfully!")
                else:
                    print("Warp installed but automatic setup failed.")
                
                # Clean up installer if desired
                try:
                    os.remove(installer_path)
                    print("Installer cleaned up.")
                except:
                    print("Could not remove installer file.")
            else:
                print("Warp installation failed after all attempts.")
                return False
        else:
            print("Download failed or file not found.")
            return False
            
    except Exception as e:
        print(f"An error occurred: {e}")
        return False
        
    finally:
        # Close the browser
        driver.quit()
        print("Browser closed.")
    
    return True

# ==================== COINIMP FUNCTIONS ====================
class TestCoinimp:
    def setup_method(self, method):
        # Chrome driver setup
        chrome_options = Options()
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--disable-infobars')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disk-cache-size=1')  # Minimize cache
        chrome_options.add_argument('--disable-application-cache')
        chrome_options.add_argument('--disable-cache')
        chrome_options.add_argument('--disable-background-networking')
        chrome_options.add_argument('--media-cache-size=1')
        chrome_options.add_argument('--disable-offline-load-stale-cache')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-software-rasterizer")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--enable-unsafe-webgl")  # New
        chrome_options.add_argument("--use-angle=swiftshader")  # New
        chrome_options.add_argument("--disable-webgl")  # New
        chrome_options.add_argument("--disable-3d-apis")  # New
        chrome_options.add_argument('--disable-features=VizDisplayCompositor')
        chrome_options.add_argument('--disable-gl-drawing-for-tests')
        chrome_options.add_argument('--disable-accelerated-2d-canvas')
        chrome_options.add_argument('--disk-cache-size=1')
        chrome_options.add_argument("--disable-3d-apis")
        chrome_options.add_argument("--disable-accelerated-2d-canvas")
        chrome_options.add_argument("--disable-gpu-compositing")
        chrome_options.add_argument('--disable-logging')
        chrome_options.add_argument('--log-level=3')
        
        # Initialize driver
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(5)  # Set implicit wait
        self.vars = {}

    def teardown_method(self, method):
        self.driver.quit()

    def wait_and_click(self, by, locator, timeout=10):
        """Helper method to wait for element and click it"""
        element = WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable((by, locator))
        )
        element.click()
        return element

    def test_coinimp(self):
        try:
            # 1. Open website
            self.driver.get("https://varisha.kesug.com/")
            print("Website opened successfully")
            time.sleep(5)

            # 2. Wait for iframe to load and switch to it
            iframe = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "iframe"))
            )
            self.driver.switch_to.frame(iframe)
            print("Switched to iframe")

            # 3. Click play button
            self.wait_and_click(By.CSS_SELECTOR, ".ytp-large-play-button")
            print("Play button clicked")

            # 4. Wait for random time (15-17 minutes)
            watch_time = random.randint(15 * 60, 17 * 60)  # 900 to 1020 seconds
            print(f"Watching video for {watch_time} seconds ({watch_time//60} minutes)...")
            time.sleep(watch_time)
            
            # 5. Switch back to main content
            self.driver.switch_to.default_content()
            print("Switched back to main content")

            # 6. Click on home div (if still needed)
            try:
                self.wait_and_click(By.CSS_SELECTOR, ".home > div > div > div")
                print("Home div clicked")
            except Exception as e:
                print(f"Could not click home div: {str(e)}")

            print("Test completed successfully")
            return True

        except Exception as e:
            print(f"Test failed: {str(e)}")
            return False

def coinimp_main_loop():
    """Main continuous loop function for CoinImp"""
    action_counter = 0
    
    while True:
        try:
            # Initialize the test class
            test = TestCoinimp()
            test.setup_method(None)
            
            try:
                # Perform the main test
                success = test.test_coinimp()
                if success:
                    print("Test completed successfully in this iteration")
                else:
                    print("Test failed in this iteration")
                    
            except Exception as e:
                print(f"Error during test execution: {e}")
                
            finally:
                # Always clean up
                test.teardown_method(None)
                
            # Increment counter
            action_counter += 1
            print(f"Total iterations completed: {action_counter}")
            
            # Add a small delay before next iteration
            print("Waiting 10 seconds before next iteration...")
            time.sleep(10)
            
        except KeyboardInterrupt:
            print("Stopped by user")
            break
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            print("Waiting 30 seconds before retrying...")
            time.sleep(10)

# ==================== MAIN EXECUTION ====================
if __name__ == "__main__":
    # Step 1: Install dependencies
    install_dependencies()
    
    # Step 2: Execute Warp setup
    print("\n" + "="*50)
    print("STARTING WARP SETUP")
    print("="*50)
    warp_success = download_and_install_warp()
    if warp_success:
        print("Warp setup completed successfully!")
    else:
        print("Warp setup failed. Continuing with CoinImp...")
    
    # Step 3: Execute CoinImp automation
    print("\n" + "="*50)
    print("STARTING COINIMP AUTOMATION")
    print("="*50)
    coinimp_main_loop()
