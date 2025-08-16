from .Audit.audit import RunAudit
from celery import shared_task
import asyncio
from .models import ProductList

@shared_task
def run_audit_task(productlist_id):
    print(f"Running audit task for product list ID: {productlist_id}")
    try:
        product_list_id = ProductList.objects.get(id=productlist_id)
        audit = RunAudit(product_list_id)
        product_infos = list(audit.get_product_infos())

        print(f"Retrieved product list: {list(product_infos)[:10]} \n {len(list(product_infos))}")
    except ProductList.DoesNotExist:
        return {"status": "error", "message": f"ProductList {productlist_id} not found"}


    if not product_infos:
        return {"status": "error", "message": "No products found in this list"}

    # Run async scrape
    result = asyncio.run(audit.run_scrape(product_infos))

    return {
        "status": "success",
        "productlist_id": productlist_id,
        "scraped_count": len(product_infos),
        "result": result,   # whatever audit.run_scrape() returns
    }
