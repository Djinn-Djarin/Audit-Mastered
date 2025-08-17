import logging
import random
import asyncio

from typing import Dict, Any
from playwright.async_api import Page, Browser, BrowserContext, Response
from playwright.async_api import async_playwright

from .utils import (
    handle_captcha,
    handle_network_response,
    create_spoofed_context,
    spoof_browser_fingerprint,
)

logger = logging.getLogger("scraping")


class ScrapingLogic:
    def __init__(self, page, product_id, context_settings):
        self.page = page
        self.product_id = product_id
        self.file_name = f"./scraping.csv"
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
    def __init__(self, headless=True):
        self.headless = headless
        self.browser: Browser | None = None
        self.context: BrowserContext | None = None
        self.context_settings: dict = None

    async def start(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless, slow_mo=50
        )
        self.context, self.context_settings = await create_spoofed_context(self.browser)
        return self.context, self.context_settings

    async def close(self):
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if hasattr(self, "playwright"):
            await self.playwright.stop()


class PageManager:
    def __init__(self, context: BrowserContext, context_settings: dict):
        self.context = context
        self.context_settings = context_settings
        self.page: Page | None = None

    async def change_browser_fingerprints(self, page, context_settings):
        return await spoof_browser_fingerprint(page, context_settings)


class AmazonPageManager(PageManager):
    async def _handle_captcha(self) -> bool:
        captcha_result = await handle_captcha(self.page)
        if not captcha_result:
            logger.info(f"captcha not solved")
            return False
        return True

    async def _navigate(self, asin) -> dict | None:
        from .amazon_regular import AmazonScrapingLogic

        self.page = None
        try:
            self.page = await self.context.new_page()
            self.page.on("response", handle_network_response)
            await self.change_browser_fingerprints(self.page, self.context_settings)

            url = f"https://www.amazon.in/dp/{asin}"
            logger.warning(f"Navigating to {url}")
            await self.page.goto(url, timeout=20000, wait_until="domcontentloaded")
            await self.page.wait_for_load_state("domcontentloaded")
            await asyncio.sleep(random.uniform(3, 5))

            if not await self._handle_captcha():
                return None

            logger.warning(f"Page loaded for {asin}")
            scraping_logic = AmazonScrapingLogic(self.page, asin, self.context_settings)

            # IMPORTANT: get the dict result from your scraper
            result: Dict[str, Any] = await scraping_logic._run_scraper()
            # ensure the result at least carries the asin
            if isinstance(result, dict) and "asin" not in result:
                result["asin"] = asin
            return result

        except Exception as e:
            logger.warning(f"_navigate error for {asin}: {e}")
            # Return a minimal error record so the pipeline continues
            return {"asin": asin, "status": "error", "error": str(e)}
        finally:
            # Always close the page to avoid handle leaks
            try:
                if self.page:
                    await self.page.close()
            except Exception:
                pass
