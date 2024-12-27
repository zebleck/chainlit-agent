from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


def test_selenium():
    print("Starting Selenium test...")

    # Set up Chrome options
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    try:
        print("Initializing Chrome driver...")
        driver = webdriver.Chrome(options=options)

        print("Navigating to Google...")
        driver.get("https://www.google.com")

        print(f"Page title: {driver.title}")

        time.sleep(10)

        print("Test completed successfully!")
        return True

    except Exception as e:
        print(f"Test failed with error: {str(e)}")
        return False

    finally:
        try:
            driver.quit()
            print("Driver closed successfully")
        except:
            pass


if __name__ == "__main__":
    test_selenium()
