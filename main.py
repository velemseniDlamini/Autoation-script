import time
import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

# ============================================================================
# CONFIGURATION - Edit these values
# ============================================================================

CONFIG = {
    "login_url": "https://velemsenidlamini.github.io/UEM-MDM/login.html",
    "username": "admin@example.com",
    "password": "password",
    
    # XPath selectors for login page
    "xpath_username_input": "/html/body/div/form[1]/div[3]/input",
    "xpath_password_input": "/html/body/div/form[1]/div[4]/input",
    "xpath_login_button": "/html/body/div/form[1]/button",
    
    # Navigation steps - each step will click a target element in the web app
    "navigation_steps": [
        {
            "name": "Dashboard",
            "xpath": "//a[contains(text(), 'Dashboard')]",
            "wait_seconds": 2,
            "description": "Navigate to Dashboard"
        },
        {
            "name": "Approvals",
            "xpath": "//a[contains(text(), 'Approvals')] | //button[contains(text(), 'Approvals')]",
            "wait_seconds": 2,
            "description": "Click Approvals menu"
        },
        {
            "name": "Decisions_Dropdown",
            "xpath": "//select[@id='decisions'] | //div[contains(@class, 'decisions')]//button",
            "wait_seconds": 1,
            "description": "Open Decisions dropdown"
        },
        {
            "name": "Notifications",
            "xpath": "//a[contains(text(), 'Notifications')] | //button[contains(@class, 'notification')]",
            "wait_seconds": 2,
            "description": "Click Notifications at the top"
        }
    ],
    
    "headless": False,  # Set to True to run without visible browser
    "window_size": "1920,1080",
    "timeout": 10  # seconds to wait for elements
}

# ============================================================================
# BROWSER AUTOMATION CLASS
# ============================================================================

class WebAppAutomation:
    def __init__(self, config):
        self.config = config
        self.driver = None
        self.results = []
        
    def setup_driver(self):
        """Initialize Chrome WebDriver with options"""
        print("🔧 Setting up Chrome WebDriver...")
        
        chrome_options = Options()
        
        if self.config["headless"]:
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-gpu")
        
        chrome_options.add_argument(f"--window-size={self.config['window_size']}")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Initialize driver
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.implicitly_wait(self.config["timeout"])
        
        print("✅ WebDriver initialized successfully")
        
    def wait_and_click(self, xpath, description="element"):
        """Wait for element and click it"""
        try:
            print(f"⏳ Waiting for {description}: {xpath}")
            element = WebDriverWait(self.driver, self.config["timeout"]).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
            element.click()
            print(f"✅ Clicked {description}")
            return True
        except TimeoutException:
            print(f"❌ Timeout waiting for {description}")
            return False
        except Exception as e:
            print(f"❌ Error clicking {description}: {str(e)}")
            return False
            
    def wait_and_input(self, xpath, text, description="input"):
        """Wait for input field and enter text"""
        try:
            print(f"⏳ Waiting for {description}: {xpath}")
            element = WebDriverWait(self.driver, self.config["timeout"]).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            element.clear()
            element.send_keys(text)
            print(f"✅ Entered text into {description}")
            return True
        except TimeoutException:
            print(f"❌ Timeout waiting for {description}")
            return False
        except Exception as e:
            print(f"❌ Error entering text into {description}: {str(e)}")
            return False
            
    def login(self):
        """Perform login sequence"""
        print("\n" + "="*60)
        print("🔐 STARTING LOGIN PROCESS")
        print("="*60)
        
        # Navigate to login page
        print(f"🌐 Navigating to: {self.config['login_url']}")
        self.driver.get(self.config["login_url"])
        time.sleep(2)
        
        # Enter username
        if not self.wait_and_input(
            self.config["xpath_username_input"],
            self.config["username"],
            "username field"
        ):
            self.results.append({
                "step": "Enter Username",
                "status": "failed",
                "error": "Could not find username input",
                "timestamp": datetime.now().isoformat()
            })
            return False
            
        # Enter password
        if not self.wait_and_input(
            self.config["xpath_password_input"],
            self.config["password"],
            "password field"
        ):
            self.results.append({
                "step": "Enter Password",
                "status": "failed",
                "error": "Could not find password input",
                "timestamp": datetime.now().isoformat()
            })
            return False
            
        # Click login button
        if not self.wait_and_click(
            self.config["xpath_login_button"],
            "login button"
        ):
            self.results.append({
                "step": "Click Login",
                "status": "failed",
                "error": "Could not click login button",
                "timestamp": datetime.now().isoformat()
            })
            return False
            
        # Wait for page to load after login
        time.sleep(3)
        
        print("✅ Login completed successfully")
        return True
        
    def navigate(self):
        """Execute navigation steps"""
        print("\n" + "="*60)
        print("🧭 STARTING NAVIGATION SEQUENCE")
        print("="*60)
        
        step_number = 4
        for step in self.config["navigation_steps"]:
            print(f"\n📍 Step: {step['description']}")
            
            # Try to click the element
            success = self.wait_and_click(step["xpath"], step["name"])
            
            # Wait for page to settle
            time.sleep(step["wait_seconds"])
            
            # Record result
            self.results.append({
                "step": step["name"],
                "description": step["description"],
                "status": "success" if success else "failed",
                "xpath": step["xpath"],
                "timestamp": datetime.now().isoformat()
            })
            
            if not success:
                print(f"⚠️  Warning: Could not complete step '{step['name']}', continuing...")
            
            step_number += 1
            
        print("\n✅ Navigation sequence completed")
        
    def save_results(self):
        """Save execution results to JSON file"""
        results_file = "execution_results.json"
        
        summary = {
            "execution_time": datetime.now().isoformat(),
            "total_steps": len(self.results),
            "successful_steps": len([r for r in self.results if r["status"] == "success"]),
            "failed_steps": len([r for r in self.results if r["status"] == "failed"]),
            "steps": self.results
        }
        
        with open(results_file, 'w') as f:
            json.dump(summary, f, indent=2)
            
        print(f"\n📄 Results saved to: {results_file}")
        return summary
        
    def run(self):
        """Main execution flow"""
        try:
            self.setup_driver()
            
            # Perform login
            if not self.login():
                print("\n❌ Login failed, aborting navigation")
                return False
                
            # Execute navigation steps
            self.navigate()
            
            # Save results
            summary = self.save_results()
            
            # Print summary
            print("\n" + "="*60)
            print("📊 EXECUTION SUMMARY")
            print("="*60)
            print(f"Total Steps: {summary['total_steps']}")
            print(f"✅ Successful: {summary['successful_steps']}")
            print(f"❌ Failed: {summary['failed_steps']}")
            print("="*60)
            
            return True
            
        except Exception as e:
            print(f"\n❌ Fatal error: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
            
        finally:
            if self.driver:
                print("\n🔒 Closing browser...")
                time.sleep(2)  # Brief pause before closing
                self.driver.quit()
                print("✅ Browser closed")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║  Web Application Browser Automation with XPath Navigation   ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    
    automation = WebAppAutomation(CONFIG)
    success = automation.run()
    
    if success:
        print("\n✅ Automation completed successfully!")
        exit(0)
    else:
        print("\n❌ Automation completed with errors")
        exit(1)
