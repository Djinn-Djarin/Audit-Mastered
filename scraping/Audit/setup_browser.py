import logging
import random
import asyncio

from typing import  Dict, Any
from playwright.async_api import Page, Browser, BrowserContext, Response
from playwright.async_api import async_playwright

from .utils import handle_captcha, handle_network_response,\
                create_spoofed_context, spoof_browser_fingerprint
from .save_csv import csv_audit_general


logger = logging.getLogger('scraping')


class ScrapingLogic:
    def __init__(self, page, product_id, file_name, context_settings):
        self.page = page
        self.product_id =product_id
        self.file_name = file_name
        self.context_settings = context_settings

    def _status(self):
        raise NotImplementedError
    def _title(self):
        raise NotImplementedError
    def _brand_name(self):
        raise NotImplementedError
    def _price(self):
        raise NotImplementedError
    def _mrp(self):
        raise NotImplementedError
    def _variations(self):
        raise NotImplementedError
    def _reviews(self):
        raise NotImplementedError
    def _ratings(self):
        raise NotImplementedError
    def _seller(self):
        raise NotImplementedError
    def _image_length(self):
        raise NotImplementedError
    def _scrape_result(self):
        raise NotImplementedError
    def _run_scraper(self):
        raise NotImplementedError
    

class BrowserManager:
    def __init__(self, headless=False):
        self.headless = headless
        self.browser : Browser | None = None
        self.context : BrowserContext | None = None
        self.context_settings : dict = None

    async def start(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=self.headless, slow_mo=50)
        self.context, self.context_settings = await create_spoofed_context(self.browser)
        return self.context, self.context_settings

    async def close(self):
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()


class PageManager:
    def __init__(self, context: BrowserContext, context_settings: dict):
            self.context = context
            self.context_settings = context_settings
            self.page: Page | None = None
    
    async def change_browser_fingerprints(self, page,context_settings):
        return await spoof_browser_fingerprint(page, context_settings)

class AmazonPageManager(PageManager):
    async def _handle_captcha(self,) -> bool:
        captcha_result = await handle_captcha(self.page)
        if not captcha_result:
            logger.info(f"captcha not solved for {self.asin}")
                    
            return False
        return True
     
    async def _navigate(self, asin) -> bool:
        from .amazon_regular import AmazonScrapingLogic
        try:
            self.page = await self.context.new_page()
            self.page.on("response", handle_network_response)
            await self.change_browser_fingerprints(self.page, self.context_settings)
            url = f"https://www.amazon.in/dp/{asin}"
            print(f"Navigating to {url}")
            await self.page.goto(
                url, timeout=10000, wait_until="domcontentloaded"
            )
            await self.page.wait_for_load_state("domcontentloaded")
            await asyncio.sleep(random.uniform(3, 5))
            captcha_result = await self._handle_captcha()
            if not captcha_result:
                scraping_logic = AmazonScrapingLogic(self.page, self.product_id, self.context_settings, )
                await scraping_logic._run_scraper()
                return True        
        except Exception as e:
            logger.warning(f"Error : {e}")
            return False

   


