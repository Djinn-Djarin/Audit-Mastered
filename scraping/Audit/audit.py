import asyncio
import logging
import random
from ..models import  ProductInfo
from .setup_browser import AmazonPageManager, BrowserManager


logger = logging.getLogger('scraping')

class RunAudit:
    def __init__(self, product_list_id):
        self.product_list_id= product_list_id

    def get_product_infos(self):
        products = self.product_list_id.products_list.all()
        product_list = products.values_list('product_id', flat=True)
        product_list = list(product_list)
        if not product_list:
            return {"status": "error", "message": "No products found in this list"} 
        return product_list


    async def run_scrape(self, product_infos):
        browser = BrowserManager()
        context, context_settings = await browser.start()
        page_manager = AmazonPageManager(context, context_settings)

        for idx, product in enumerate(product_infos):
      
            await page_manager._navigate(product)

        await browser.close()


