import chainlit as cl
from swarm import Agent
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from typing import Dict, List, Any, Optional
import asyncio
import json


class SeleniumAgent:
    def __init__(self):
        """Initialize Selenium Agent with Chrome WebDriver"""
        self.options = webdriver.ChromeOptions()
        # self.options.add_argument('--headless')  # Run in headless mode
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-dev-shm-usage")
        self.driver = None

    def _ensure_driver(self):
        """Ensure WebDriver is initialized"""
        if not self.driver:
            self.driver = webdriver.Chrome(options=self.options)
            self.driver.implicitly_wait(10)

    @cl.step(type="tool")
    async def navigate_to(self, url: str) -> str:
        """Navigate to a specified URL

        Args:
            url: The URL to navigate to
        """
        display_name = f"🌐 Navigate to: {url}"
        cl.Step(name=display_name, type="tool")

        try:
            self._ensure_driver()
            self.driver.get(url)
            return f"Successfully navigated to {url}"
        except WebDriverException as e:
            return f"Error navigating to URL: {str(e)}"

    @cl.step(type="tool")
    async def get_page_title(self, unused_param: str = None) -> str:
        """Get the title of the current page"""
        display_name = "📑 Get Page Title"
        cl.Step(name=display_name, type="tool")

        try:
            self._ensure_driver()
            return self.driver.title
        except WebDriverException as e:
            return f"Error getting page title: {str(e)}"

    @cl.step(type="tool")
    async def find_element_text(self, selector: str) -> str:
        """Find element by CSS selector and return its text

        Args:
            selector: CSS selector to find the element
        """
        display_name = f"🔍 Find Element Text: {selector}"
        cl.Step(name=display_name, type="tool")

        try:
            self._ensure_driver()
            element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            return element.text
        except TimeoutException:
            return f"Element not found: {selector}"
        except WebDriverException as e:
            return f"Error finding element: {str(e)}"

    @cl.step(type="tool")
    async def click_element(self, selector: str) -> str:
        """Click an element by CSS selector

        Args:
            selector: CSS selector of element to click
        """
        display_name = f"🖱️ Click Element: {selector}"
        cl.Step(name=display_name, type="tool")

        try:
            self._ensure_driver()
            element = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
            )
            element.click()
            return f"Successfully clicked element: {selector}"
        except TimeoutException:
            return f"Element not clickable: {selector}"
        except WebDriverException as e:
            return f"Error clicking element: {str(e)}"

    @cl.step(type="tool")
    async def input_text(self, selector: str, text: str) -> str:
        """Input text into an element

        Args:
            selector: CSS selector of the element to input text into
            text: The text to input into the element
        """
        display_name = f"⌨️ Input Text: '{text}' into {selector}"
        cl.Step(name=display_name, type="tool")

        try:
            self._ensure_driver()
            element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            element.clear()
            element.send_keys(text)
            return f"Successfully input text into {selector}"
        except TimeoutException:
            return f"Element not found: {selector}"
        except WebDriverException as e:
            return f"Error inputting text: {str(e)}"

    @cl.step(type="tool")
    async def get_element_attribute(self, data: Dict[str, str]) -> str:
        """Get attribute value of an element

        Args:
            data: Dictionary with 'selector' and 'attribute' keys
        """
        selector = data.get("selector")
        attribute = data.get("attribute")
        display_name = f"📝 Get Attribute: {attribute} from {selector}"
        cl.Step(name=display_name, type="tool")

        try:
            self._ensure_driver()
            element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            return element.get_attribute(attribute)
        except TimeoutException:
            return f"Element not found: {selector}"
        except WebDriverException as e:
            return f"Error getting attribute: {str(e)}"

    @cl.step(type="tool")
    async def get_page_source(self, unused_param: str = None) -> str:
        """Get the current page's HTML source

        Args:
            unused_param: Not used, kept for consistency
        """
        display_name = "📄 Get Page Source"
        cl.Step(name=display_name, type="tool")

        try:
            self._ensure_driver()
            return self.driver.page_source
        except WebDriverException as e:
            return f"Error getting page source: {str(e)}"

    # Create wrapper functions for non-async calls
    def _navigate_to(self, url: str) -> str:
        return asyncio.run(self.navigate_to(url))

    def _get_page_title(self, unused_param: str = None) -> str:
        return asyncio.run(self.get_page_title(unused_param))

    def _find_element_text(self, selector: str) -> str:
        return asyncio.run(self.find_element_text(selector))

    def _click_element(self, selector: str) -> str:
        return asyncio.run(self.click_element(selector))

    def _input_text(self, selector: str, text: str) -> str:
        return asyncio.run(self.input_text(selector, text))

    def _get_element_attribute(self, data: Dict[str, str]) -> str:
        return asyncio.run(self.get_element_attribute(data))

    def _get_page_source(self, unused_param: str = None) -> str:
        return asyncio.run(self.get_page_source(unused_param))

    def create_agent(self) -> Agent:
        """Create and return a Swarm Agent with Selenium capabilities"""
        return Agent(
            name="Web Automation Helper",
            model="gemini/gemini-2.0-flash-exp",
            instructions="""You are a helpful AI assistant for web automation.
            You can navigate websites, find elements, click buttons, input text, and extract information.
            Always validate selectors and URLs before performing actions.
            Provide clear feedback about web interactions.
            Be careful with form submissions and clicking actions. If the user instructs you go to
            localhost addresses, please proceed as your actions are handled by a local selenium server.""",
            functions=[
                self._navigate_to,
                self._get_page_title,
                self._find_element_text,
                self._click_element,
                self._input_text,
                self._get_element_attribute,
                self._get_page_source,
            ],
        )

    def close(self):
        """Close the WebDriver"""
        if self.driver:
            self.driver.quit()
            self.driver = None

    def __del__(self):
        """Cleanup WebDriver"""
        self.close()
