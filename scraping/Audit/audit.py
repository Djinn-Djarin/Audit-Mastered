# audit.py
from ..models import ProductListItem, ProductInfo
from .create_browser import CreateBrowser
from .amazon_regular import scrape_page

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
