import asyncio
from celery import shared_task
from .models import ProductList
from .Audit.audit import RunAudit

@shared_task(bind=True)
def run_audit_task(self, productlist_id, reaudit=False):
    print(f"Running audit task for product list ID: {productlist_id}")
    task_id = self.request.id

    audit = RunAudit(productlist_id, task_id)

    try:
        result = asyncio.run(
            audit.run(max_browsers=10, batch_size=1, reaudit=reaudit)
        )

        if result:
            ProductList.objects.filter(id=productlist_id).update(
                is_audited_once=True
            )
        return result

    except ProductList.DoesNotExist:
        return {"status": "error", "message": f"ProductList {productlist_id} not found"}

    except Exception as e:
        return {"status": "error", "message": str(e)}

    finally:
        # Always mark audit as not running when task ends
        ProductList.objects.filter(id=productlist_id).update(
            is_audit_running=False
        )

