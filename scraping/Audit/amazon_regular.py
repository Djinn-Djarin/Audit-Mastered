import gc
import re

import logging

from .save_csv import csv_audit_general
from playwright.async_api import Page


from typing import  Literal, Dict, Any
from .setup_browser import ScrapingLogic

logger = logging.getLogger('scraping')



class StatusChecker:
    def __init__(self, page: Page, asin: str):
        self.page = page
        self.asin = asin

    async def check(self) -> Literal[
        'Rush Hour', 'Suppressed', 'Live', 'Suppressed Asin Changed', 'Suppressed Detail Page Removed']:
        status: str = 'Suppressed'
        current_url: str = self.page.url

        expected_message_start = "Oops! It's rush hour and traffic is piling up on that page."
        rush_hour_element = await self.page.query_selector("center")
        if rush_hour_element:
            text_content = await rush_hour_element.text_content()
            clean_text = ' '.join([line.strip() for line in text_content.splitlines() if line.strip()])
            if clean_text.startswith(expected_message_start):
                return 'Rush Hour'

        if 'dp' in current_url:
            suppressed_element = await self.page.query_selector(".h1")
            if suppressed_element:
                status = 'Suppressed'
            else:
                asin_element = self.page.locator('div[data-card-metrics-id^="tell-amazon-desktop_DetailPage_"] div[data-asin]')
                try:
                    await asin_element.wait_for(state="visible", timeout=20000)
                    main_data_asin_val = await asin_element.get_attribute("data-asin")
                    if main_data_asin_val == self.asin:
                        status = 'Live'
                    else:
                        status = 'Suppressed Asin Changed'
                except Exception:
                    status = 'Suppressed Detail Page Removed'

        return status



class AmazonScrapingLogic(ScrapingLogic):

    async def _status(self, page: Page, asin: str) :
        return await StatusChecker(page, asin).check()

    async def _title(self) -> str:
        title_locator = self.page.locator("span#productTitle").first
        try:
            await title_locator.wait_for(state="visible", timeout=5000)
            title = await title_locator.text_content()
            return title.strip() if title else "N/A"
        except Exception:
            return "N/A"

    async def _brand_name(self) -> str:
        brand_name_element = self.page.locator("a#bylineInfo").first
        if await brand_name_element.count() > 0:
            await brand_name_element.wait_for(state="visible", timeout=10000)
            raw_brand = (await brand_name_element.text_content()).strip()
            return re.sub(r'^(Visit the\s+)?(.*?)(\s+Store)?$', r'\2', raw_brand).strip()
        logger.info("brand name link not found")
        return 'N/A'
    
    async def _price(self) -> str:
        price_loc = self.page.locator("span.a-price-whole")
        if await price_loc.count() > 0:
            price_text = await price_loc.first.text_content()
            return price_text.strip() if price_text else "N/A"
        return "N/A"

    async def _mrp(self) -> float:
        try:
            mrp_label = self.page.locator(".basisPrice > span > span").first
            await mrp_label.wait_for(timeout=10000)
            if mrp_label:
                mrp_text = await mrp_label.text_content()
                if mrp_text:
                    mrp_text = mrp_text.replace('₹', '').replace(',', '').strip()
                    try:
                        return float(mrp_text)
                    except Exception as e:
                        print("error in mrp", e)
        except Exception:
            logger.info(f"mrp not found {self.asin}")
        return 0

    async def _variations(self) -> str:
        variations_locator = self.page.locator(
            "#twister-plus-inline-twister, "
            "#variation_color_name, "
            "#variation_size_name, "
            "#inline-twister-row-pattern_name, "
            "#variation_style_name"
        )
        return "Available" if await variations_locator.count() > 0 else "N/A"
    
    async def _reviews(self) -> str:
        reviews_locator = self.page.locator("span#acrPopover").first
        try:
            await reviews_locator.wait_for(state="visible", timeout=10000)
            reviews_title = await reviews_locator.get_attribute("title")
            return reviews_title.split(" ")[0].strip() if reviews_title else "0"
        except Exception:
            logger.error(f"review 0")
            return "0"

    async def _ratings(self) -> str:
        ratings_locator = self.page.locator("span#acrCustomerReviewText").first
        if await ratings_locator.count() > 0:
            ratings_text = await ratings_locator.text_content()
            return ratings_text.split(" ")[0].replace(",", "").strip() if ratings_text else "0"
        return "0"

    async def _seller(self) -> str:
        seller_locator = self.page.locator("#sellerProfileTriggerId").first
        return (await seller_locator.text_content()).strip() if await seller_locator.count() > 0 else "N/A"

    async def _availability(self) -> str:
        availability_locator = self.page.locator("div#availability").first
        if await availability_locator.count() > 0:
            availability_text = await availability_locator.inner_text()
            if availability_text:
                return " ".join(availability_text.replace("\n", " ").split())
        return "N/A"

    async def _browse_node(self) -> str:
        breadcrumb_locator = self.page.locator(
            "div#wayfinding-breadcrumbs_feature_div ul.a-unordered-list.a-horizontal.a-size-small a"
        )
        if await breadcrumb_locator.count() > 0:
            browse_node_list = await breadcrumb_locator.all_inner_texts()
            return " > ".join(text.strip() for text in browse_node_list)
        return "N/A"

    async def _deal(self) -> str:
        deal_locator = self.page.locator("span.dealBadgeTextColor").first
        if await deal_locator.count() > 0:
            deal_text = await deal_locator.text_content()
            return deal_text.strip() if deal_text else "N/A"
        return "N/A"

    async def _image_length(self):
        image_locators = self.page.locator("#altImages img")
        image_count = await image_locators.count()
        # img_urls = [await image_locators.nth(i).get_attribute("src") for i in range(image_count)]
        return image_count

    async def _video(self) -> str:
        video_locator = self.page.locator("li.videoThumbnail img").first
        return "Available" if await video_locator.count() > 0 else "Not Available"

    async def _main_img_url(self) -> str:
        try:
            ul_locator = self.page.locator(
                "ul.a-unordered-list.a-nostyle.a-button-list.a-vertical.a-spacing-top-micro.gridAltImageViewLayoutIn1x7"
            ).first
            if await ul_locator.count() == 0:
                ul_locator = self.page.locator(
                    "ul.a-unordered-list.a-nostyle.a-button-list.a-vertical.a-spacing-top-extra-large.regularAltImageViewLayout"
                ).first
            if await ul_locator.count() > 0:
                img_locators = ul_locator.locator("img")
                count = await img_locators.count()
                for i in range(count):
                    src = await img_locators.nth(i).get_attribute("src")
                    if src and src.endswith(".jpg"):
                        return src.replace("SS100", "SS500")
        except Exception as e:
            logger.warning(f"Error fetching main image URL: {e}")
        return "N/A"

    async def _bullet_point_len(self) -> int:
        try:
            ul_locator = self.page.locator("div#feature-bullets ul.a-unordered-list.a-vertical.a-spacing-mini").first
            if await ul_locator.count() > 0:
                return await ul_locator.locator("li").count()
        except Exception as e:
            logger.warning(f"Error counting bullet points: {e}")
        return 0

    async def _best_seller_rank(self) -> str:
        bsr1, bsr2 = "Not Available", "Not Available"
        try:
            table = self.page.locator("table#productDetails_detailBullets_sections1").first
            if await table.count() > 0:
                th_elements = await table.locator("th").all()
                best_sellers_th = None
                for th in th_elements:
                    text = (await th.text_content() or "").strip()
                    if text == "Best Sellers Rank":
                        best_sellers_th = th
                        break
                if best_sellers_th:
                    best_sellers_td = await best_sellers_th.evaluate_handle("th => th.nextElementSibling")
                    if best_sellers_td:
                        span_texts = await best_sellers_td.eval_on_selector_all(
                            "li span.a-list-item span", "els => els.map(e => e.textContent.trim())"
                        )
                        if span_texts:
                            ranks = span_texts[:2]
                            if len(ranks) < 2:
                                ranks += ["Not Available"] * (2 - len(ranks))
                            bsr1 = re.sub(r"\s*\(.*?\)", "", ranks[0]).strip()
                            bsr2 = re.sub(r"\s*\(.*?\)", "", ranks[1]).strip()
        except Exception as e:
            print(f"Error extracting Best Sellers Rank: {e}")
        return f"{bsr1}, {bsr2}"

    async def _description(self) -> str:
        desc_loc = self.page.locator("#productDescription").first
        if await desc_loc.count() > 0:
            desc_text = await desc_loc.first.text_content()
            if desc_text:
                return desc_text.strip()
        return "Not Available"

    async def _aplus(self) -> str:
        aplus_data = self.page.locator("#aplus")
        return "Available" if await aplus_data.count() > 0 else "N/A"

    async def _store_link(self) -> str:
        byline_info = self.page.locator("a#bylineInfo").first
        if await byline_info.count() > 0:
            href = await byline_info.first.get_attribute("href")
            if href:
                return f"http://amazon.in{href}"
        return "N/A"

    async def _handle_continue_shopping(self) -> bool:
            button = self.page.locator("button", has_text=re.compile(r'continue shopping', re.IGNORECASE))
            if await button.count() > 0 and await button.is_visible():
                logger.info(f'Continue Shopping button found {self.asin}')
                try:
                    await button.click()
                except Exception as e:
                    logger.error(f"Button click failed: {e}")
                    self.result['status'] = 'Suppressed Continue Button'
                    await csv_audit_general(self.result, self.file_name)
                    return False
            else:
                logger.error(f"Button not found  {self.asin}")
            return True

    def _scrape_result(self) -> Dict[str, Any]:
        return {
            'index': self.worker_id + 1,
            "asin": self.asin,
            "status": 'Suppressed',
            "brand_name": "N/A",
            "browse_node": "N/A",
            "title": "N/A",
            "reviews": "0",
            "ratings": "0",
            "variations": "N/A",
            "deal": "N/A",
            "seller": "N/A",
            "image_len": 0,
            "video": "N/A",
            "main_img_url": "N/A",
            "bullet_point_len": 0,
            "bestSellerRank": "",
            "price": "N/A",
            "MRP": 0,
            "availability": "N/A",
            "description": "N/A",
            "A_plus": "N/A",
            "store_link": "N/A",
        }
    
    async def _run_scraper(self) -> Dict[str, Any]:
        if not await self._navigate_and_prepare():
            return self.result

        if not await self._handle_captcha():
            return self.result

        if not await self._handle_continue_shopping():
            return self.result

        status = await self._status(self.page, self.asin)
        if status in ['Suppressed' , 'Rush Hour']:
            self.result['status'] = status
            await csv_audit_general(self.result, self.file_name)
            return self.result

        try:
            self.result.update({
                "status": status,
                "brand_name": await self._extract_brand_name(),
                "browse_node": await self._extract_browse_node(),
                "title": await self._extract_title(),
                "reviews": await self._extract_reviews(),
                "ratings": await self._extract_ratings(),
                "variations": await self._extract_variations(),
                "deal": await self._extract_deal(),
                "seller": await self._extract_seller(),
            })
            image_count, _ = await self._extract_images()
            self.result["image_len"] = image_count
            self.result["video"] = await self._extract_video()
            self.result["main_img_url"] = await self._extract_main_img_url()
            self.result["bullet_point_len"] = await self._extract_bullet_point_len()
            self.result["bestSellerRank"] = await self._extract_best_seller_rank()
            self.result["price"] = await self._extract_price()
            self.result["MRP"] = await self._extract_mrp()
            self.result["availability"] = await self._extract_availability()
            self.result["description"] = await self._extract_description()
            self.result["A_plus"] = await self._extract_aplus()
            self.result["store_link"] = await self._extract_store_link()
            try:
                await csv_audit_general(self.result, self.file_name)
            except Exception as e:
                logger.info(f"error at the end of csv file {e}")
            await self.page.close()
            gc.collect()
            return self.result
        except Exception as e:
            logger.info(f"error {e}")
            self.result['status'] = 'Suppressed'
            await csv_audit_general(self.result, self.file_name)
            await self.page.close()
            gc.collect()
            return self.result
