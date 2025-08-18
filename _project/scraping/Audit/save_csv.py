import os
import csv
import aiofiles
from datetime import datetime


async def csv_seller_list(data, filepath):
    if not os.path.exists(os.path.dirname(filepath)):
        os.makedirs(os.path.dirname(filepath))

    headers = [
        "index",
        "asin",
        "soldByNames",
        "sold_by1",
        "prices",
        "price1",
        "imagecount",
        "Deal",
        "main_img_url",
    ]

    file_exists = os.path.isfile(filepath) and os.stat(filepath).st_size != 0
    async with aiofiles.open(filepath, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=headers)

        if not file_exists:
            await file.write(",".join(headers) + "\n")

        await writer.writerow(data)
        await file.flush()

    # print(f"Data appended to {filepath}")


async def csv_myntra_audit(data, filepath):

    if not os.path.exists(os.path.dirname(filepath)):
        os.makedirs(os.path.dirname(filepath))

    headers = [
        "index",
        "style_id",
        "selling_price",
        "review_text",
        "seller",
        "image_url",
        "variation",
        "avg_rating",
        "buyer_count",
        "reviews_count",
    ]

    file_exists = os.path.isfile(filepath) and os.stat(filepath).st_size != 0
    async with aiofiles.open(filepath, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=headers)

        if not file_exists:
            await file.write(",".join(headers) + "\n")

        await writer.writerow(data)
        await file.flush()

    print(f"Data appended to {filepath}")


async def csv_audit_general(data, filepath):

    if not os.path.exists(os.path.dirname(filepath)):
        os.makedirs(os.path.dirname(filepath))

    headers = [
        "index",
        "asin",
        "reviews",
        "ratings",
        "seller",
        "status",
        "variations",
        "browse_node",
        "brand_name",
        "availability",
        "deal",
        "image_len",
        "video",
        "main_img_url",
        "bullet_point_len",
        "bestSellerRank",
        "price",
        "MRP",
        "title",
        "description",
        "A_plus",
        "store_link",
        "timestamp",
    ]

    file_exists = os.path.isfile(filepath) and os.stat(filepath).st_size != 0
    data["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    async with aiofiles.open(filepath, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=headers)

        if not file_exists:
            await file.write(",".join(headers) + "\n")

        await writer.writerow(data)
        await file.flush()

    # print(f" Data appended to {filepath}")


async def csv_flipkart_audit(data, filepath):

    if not os.path.exists(os.path.dirname(filepath)):
        os.makedirs(os.path.dirname(filepath))

    headers = [
        "index",
        "fsn",
        "selling_price",
        "rating",
        "ratings_count",
        "seller_name",
        "image_count",
        "main_img",
        "stock",
        "colorVariationCount",
        "CompartmentVariationCount",
        "packOfVariationCount",
    ]

    file_exists = os.path.isfile(filepath) and os.stat(filepath).st_size != 0
    async with aiofiles.open(filepath, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=headers)

        if not file_exists:
            await file.write(",".join(headers) + "\n")

        await writer.writerow(data)
        await file.flush()

    print(f" Data appended to {filepath}")
