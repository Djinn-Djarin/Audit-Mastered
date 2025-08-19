import asyncio
from celery import shared_task
from .models import ProductList
from .Audit.audit import RunAudit

@shared_task(bind=True)
def run_audit_task(self, productlist_id , reaudit=False):
    """
    Single Celery task per product list.
    Uses multiprocessing / asyncio internally to run up to 20 browser instances.
    """
    print(f"Running audit task for product list ID: {productlist_id}")
    task_id = self.request.id
    try:
        audit = RunAudit(productlist_id,task_id)
    except ProductList.DoesNotExist:
        return {"status": "error", "message": f"ProductList {productlist_id} not found"}

    result = asyncio.run(audit.run(max_browsers=10, batch_size=1, reaudit=False))
    return result
