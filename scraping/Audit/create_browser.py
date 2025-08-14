from playwright.async_api import async_playwright
from .utils import create_spoofed_context


class CreateBrowser:
    def __init__(self, headless=True):
        self.headless = headless
        self.browser = None
        self.context = None
        self.context_settings = None

    async def start(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=[
                "--disable-quic",
                "--disable-http2",
                "--disable-blink-features=AutomationControlled",
                "--enable-webgl",
                "--use-gl=swiftshader",
                "--enable-accelerated-2d-canvas",
                "--disable-features=UseDnsHttpsSvcbAlpn",
            ]
        )
        self.context, self.context_settings = await create_spoofed_context(self.browser)
        return self.context, self.context_settings

    async def close(self):
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()
