# audit.py
from ..models import  ProductInfo
from .create_browser import CreateBrowser
from .amazon_regular import scrape_page

from .utils import \
        handle_captcha, \
        handle_network_response, \
        spoof_browser_fingerprint


class RunAudit:
    @staticmethod
    def get_product_infos(productlist_id):
        # synchronous ORM query
        return ProductInfo.objects.filter(
            productlistitem__product_list_id=productlist_id
        )

    @staticmethod
    async def run_scrape(productlist_id, product_infos):
        browser = CreateBrowser()
        context, context_settings = await browser.start()

        for idx, product in enumerate(product_infos):
            page = await context.new_page()
            await scrape_page(
                page=page,
                asin=product.product_id,
                file_name=f"audit_{productlist_id}.csv",
                context_settings=context_settings,
                worker_id=idx
            )

        await browser.close()


class ScrapingLogic:
    def __init__(self, page, product_id,worker_id, file_name, context_settings):
        self.page = page
        self.product_id =product_id
        self.worker_id = worker_id
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
    
    

async def _navigate_and_prepare(self) -> bool:
    try:
        self.page.on("response", handle_network_response)
        await spoof_browser_fingerprint(self.page, self.context_settings)
        await self.page.goto(
            f"https://www.amazon.in/dp/{self.asin}", timeout=40000, wait_until="domcontentloaded"
        )
        await self.page.wait_for_load_state("domcontentloaded")
        await asyncio.sleep(random.uniform(3, 5))
        return True
    except Exception as e:
        logger.warning(f"Error for ASIN {self.asin}: {e}")
        self.result['status'] = 'Suppressed Page Timeout'
        await csv_audit_general(self.result, self.file_name)
        return False

async def _handle_captcha(self) -> bool:
    captcha_result = await handle_captcha(self.page)
    if not captcha_result:
        logger.info(f"captcha not solved for {self.asin}")
        self.result['status'] = 'Suppressed Captcha Failure'
        await csv_audit_general(self.result, self.file_name)
        return False
    return True

async def scrape_page(
    page: Page,
    asin: str,
    file_name: str,
    context_settings: Dict[str, Any],
    worker_id: int
) -> Dict[str, Any]:
    scraper = AmazonScraper(page, asin, file_name, context_settings, worker_id)
    return await scraper.scrape()

def scrape_page_sync(
    page: Page,
    asin: str,
    file_name: str,
    context_settings: Dict[str, Any],
    worker_id: int
) -> Dict[str, Any]:
    
    return asyncio.run(scrape_page(asin, file_name, context_settings, worker_id))
