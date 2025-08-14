# tasks.py
from .Audit.audit import RunAudit
from celery import shared_task
import asyncio

@shared_task
def run_audit_task(productlist_id):
    # Fetch all ProductInfo objects synchronously
    product_infos = RunAudit.get_product_infos(productlist_id)
    
    # Convert to list to evaluate the queryset synchronously
    product_infos = list(product_infos)

    # Run the async scraping part
    asyncio.run(RunAudit.run_scrape(productlist_id, product_infos))
