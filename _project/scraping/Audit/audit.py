import asyncio

import logging
from asgiref.sync import sync_to_async
from .bowser_config import AmazonPageManager, BrowserManager
from scraping.models import ProductInfo
from .utils import TaskProgress 
logger = logging.getLogger("scraping")
from queue import Queue

class ResultSaver:
    def __init__(self, product_list, user, batch_size: int = 20):
        self.product_list = product_list
        self.user = user
        self.batch_size = batch_size
        self.buffer = []

    async def add_result(self, result: dict):
        self.buffer.append(
            ProductInfo(
                user=self.user,
                product_list=self.product_list,
                product_id=result.get("asin"),
                status=result.get("status"),
                title=result.get("title"),
                reviews=result.get("reviews"),
                ratings=result.get("ratings"),
                browse_node=result.get("browse_node"),
                brand_name=result.get("brand_name"),
                variations=result.get("variations"),
                deal=result.get("deal"),
                seller=result.get("seller"),
                image_len=result.get("image_len"),
                video=result.get("video"),
                main_img_url=result.get("main_img_url"),
                bullet_point_len=result.get("bullet_point_len"),
                bsr1=result.get("bestSellerRank", ""),
                bsr2="",  # optional fallback
                price=result.get("price"),
                mrp=result.get("MRP"),
                availability=result.get("availability"),
                description=result.get("description"),
                a_plus=result.get("A_plus"),
                store_link=result.get("store_link"),
            )
        )
        if len(self.buffer) >= self.batch_size:
            await self.flush()

    async def flush(self):
        if not self.buffer:
            return
        await sync_to_async(ProductInfo.objects.bulk_create)(
            self.buffer,
            batch_size=self.batch_size,
            update_conflicts=True,
            update_fields=[
                "status", "title", "reviews", "ratings", "browse_node",
                "brand_name", "variations", "deal", "seller", "image_len",
                "video", "main_img_url", "bullet_point_len", "bsr1", "bsr2",
                "price", "mrp", "availability", "description", "a_plus",
                "store_link", "updated_at",
            ],
            unique_fields=["product_list", "product_id"],
        )
        self.buffer.clear()


class BrowserLimiter:
    def __init__(self, redis_url="redis://localhost", max_browsers=20):
        self.redis_url = redis_url
        self.max_browsers = max_browsers
        self.redis = None

    async def _get_redis(self):
        if not self.redis:
            self.redis = await aioredis.from_url(self.redis_url)
        return self.redis

    async def acquire(self):
        redis = await self._get_redis()
        while True:
            count = await redis.incr("browser_count")
            if count <= self.max_browsers:
                return
            await redis.decr("browser_count")
            await asyncio.sleep(1)

    async def release(self):
        redis = await self._get_redis()
        await redis.decr("browser_count")



from asyncio import Queue, create_task, gather

class AuditWorkers:
    """Worker that processes a list of products using asyncio and browser limiter."""
    def __init__(self, product_infos, browser_instances, product_list, user, task_id, batch_size=20, max_browsers=20):
        self.product_infos = product_infos
        self.browser_instances = browser_instances
        self.saver = ResultSaver(product_list=product_list, user=user, batch_size=batch_size)
        self.limiter = BrowserLimiter(max_browsers=max_browsers)
        self.task_progress = TaskProgress(task_id) if task_id else None

    async def worker(self, queue: Queue):
        while True:
            product = await queue.get()
            if product is None:
                queue.task_done()
                break

            await self.limiter.acquire()
            try:
                browser = BrowserManager()
                context, context_settings = await browser.start()
                page_manager = AmazonPageManager(context, context_settings)
                result = await page_manager._navigate(product)

                if isinstance(result, dict):
                    await self.saver.add_result(result)
                else:
                    await self.saver.add_result({"asin": product, "status": "no_data"})

                # Increment progress (sync call is fine)
                if self.task_progress:
                    self.task_progress.increment()

            finally:
                await browser.close()
                await self.limiter.release()
                queue.task_done()

    async def run(self):
        queue = asyncio.Queue()
        # Fill queue
        for product in self.product_infos:
            await queue.put(product)

        # Initialize task progress (sync)
        if self.task_progress:
            self.task_progress.init_task(total=len(self.product_infos), user_id=self.saver.user.id)

        # Start workers
        tasks = [create_task(self.worker(queue)) for _ in range(self.browser_instances)]

        # Wait until queue is fully processed
        await queue.join()

        # Stop workers
        for _ in range(self.browser_instances):
            await queue.put(None)
        await gather(*tasks, return_exceptions=True)

        # Flush saved results
        await self.saver.flush()

        # Mark task as done (sync)
        if self.task_progress:
            self.task_progress.set_status("done")

        return {"status": "success", "processed_count": len(self.product_infos)}


class RunAudit:
    def __init__(self, product_list_id, task_id):
        self.product_list_id = product_list_id
        self.product_list = None
        self.task_id = task_id

    async def load_product_list(self):
        from scraping.models import ProductList
        self.product_list = await sync_to_async(ProductList.objects.get)(id=self.product_list_id)

    async def get_user(self):
        return await sync_to_async(lambda: self.product_list.user)()

    async def get_product_infos(self, reaudit=False):
        if reaudit:
            status = ['Live','Suppressed', 'Suppressed Asin Chnaged']
            return await sync_to_async(list)(
                self.product_list.products_list.exclude(status__in = status).values_list("product_id", flat=True)
            )
        return await sync_to_async(list)(
            self.product_list.products_list.values_list("product_id", flat=True)
        )

    async def run(self, max_browsers=5, batch_size=20, reaudit=False):
        await self.load_product_list()
        product_infos = await self.get_product_infos(reaudit)
        if not product_infos:
            return {"status": "error", "message": "No products found in this list"}

        user = await self.get_user()
        
        import math
        total_products = len(product_infos)
        chunk_size = math.ceil(total_products / max_browsers)
        product_chunks = [
            product_infos[i:i + chunk_size] for i in range(0, total_products, chunk_size)
        ]


        workers = [
            AuditWorkers(
                product_infos=chunk,
                browser_instances=1,
                product_list=self.product_list,
                user=user,
                task_id = self.task_id,
                batch_size=batch_size,
                max_browsers=max_browsers,
            )
            for chunk in product_chunks
        ]

        await asyncio.gather(*(w.run() for w in workers))
        return {"status": "success", "processed_count": total_products}
