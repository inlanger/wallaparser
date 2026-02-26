"""Wallapop MCP Server — tools for searching and scraping Wallapop marketplace."""

import asyncio
import json
import re
import urllib.parse
from datetime import datetime
from typing import Optional

import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("wallapop")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Origin": "https://es.wallapop.com",
    "Referer": "https://es.wallapop.com/",
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    ),
    "X-DeviceOS": "0",
}

CITIES: dict[str, tuple[float, float]] = {
    "valencia": (39.4699, -0.3763),
    "madrid": (40.4168, -3.7038),
    "barcelona": (41.39, 2.17),
}

API_BASE = "https://api.wallapop.com/api/v3/search"
SSR_BASE = "https://es.wallapop.com"

USER_AGENTS = [
    HEADERS["User-Agent"],
    (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    ),
    (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    ),
]

# ---------------------------------------------------------------------------
# HTTP client (shared across tools)
# ---------------------------------------------------------------------------

_client: Optional[httpx.AsyncClient] = None


def _get_client() -> httpx.AsyncClient:
    global _client
    if _client is None or _client.is_closed:
        _client = httpx.AsyncClient(
            headers=HEADERS,
            timeout=httpx.Timeout(30.0),
            follow_redirects=True,
        )
    return _client


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _get_price(item: dict) -> float:
    p = item.get("price", {})
    if isinstance(p, dict) and "cash" in p:
        return p["cash"].get("amount", 0)
    if isinstance(p, dict):
        return p.get("amount", 0)
    return 0


def _is_reserved(item: dict) -> bool:
    r = item.get("reserved", False)
    if isinstance(r, dict):
        return r.get("flag", False)
    return bool(r)


def _get_description(item: dict) -> str:
    d = item.get("description", "")
    if isinstance(d, dict):
        return d.get("original", str(d))
    return str(d)


def _get_title(item: dict) -> str:
    t = item.get("title", "")
    if isinstance(t, dict):
        return t.get("original", str(t))
    return str(t)


def _coords(city: str) -> tuple[float, float]:
    return CITIES.get(city.lower(), CITIES["valencia"])


def _extract_slug(slug_or_url: str) -> str:
    slug_or_url = slug_or_url.strip()
    if "/item/" in slug_or_url:
        return slug_or_url.split("/item/")[-1].split("?")[0].split("#")[0]
    return slug_or_url


def _format_item(item: dict) -> dict:
    return {
        "slug": item.get("web_slug", ""),
        "title": _get_title(item),
        "price": _get_price(item),
        "currency": (item.get("price", {}).get("cash", {}) or item.get("price", {})).get("currency", "EUR"),
        "city": item.get("location", {}).get("city", ""),
        "country": item.get("location", {}).get("country_code", ""),
        "shipping": {
            "item_is_shippable": item.get("shipping", {}).get("item_is_shippable", False),
            "user_allows_shipping": item.get("shipping", {}).get("user_allows_shipping", False),
        },
        "reserved": _is_reserved(item),
        "link": f"https://es.wallapop.com/item/{item.get('web_slug', '')}",
    }


async def _api_get(url: str, retries: int = 3) -> httpx.Response:
    """GET with retry on 403/429."""
    client = _get_client()
    delay = 5.0
    for attempt in range(retries):
        resp = await client.get(url)
        if resp.status_code == 200:
            return resp
        if resp.status_code == 403 and attempt < retries - 1:
            ua = USER_AGENTS[(attempt + 1) % len(USER_AGENTS)]
            client.headers["User-Agent"] = ua
            await asyncio.sleep(1)
            continue
        if resp.status_code == 429 and attempt < retries - 1:
            await asyncio.sleep(delay)
            delay *= 2
            continue
        resp.raise_for_status()
    return resp  # type: ignore[return-value]


async def _ssr_get(url: str) -> httpx.Response:
    """GET for SSR pages (no special API headers needed, but reuse client)."""
    client = _get_client()
    resp = await client.get(url)
    resp.raise_for_status()
    return resp


def _parse_ssr(html: str) -> dict:
    """Extract __NEXT_DATA__ JSON from SSR HTML."""
    m = re.search(
        r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.DOTALL
    )
    if not m:
        raise ValueError("No __NEXT_DATA__ found — page may be behind captcha or blocked")
    return json.loads(m.group(1))["props"]["pageProps"]


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


@mcp.tool()
async def wallapop_search(
    keywords: str,
    city: str = "valencia",
    order_by: str = "most_relevance",
    category_id: Optional[int] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
) -> dict:
    """Search Wallapop for items. Two-step: components (get search_id) then section (get items).

    Args:
        keywords: Search query
        city: One of valencia, madrid, barcelona
        order_by: most_relevance, newest, price_low_to_high, price_high_to_low
        category_id: Optional category filter
        min_price: Optional minimum price filter (client-side)
        max_price: Optional maximum price filter (client-side)
    """
    lat, lon = _coords(city)

    # Step 1: get search_id
    params1 = {
        "keywords": keywords,
        "order_by": order_by,
        "source": "search_box",
    }
    if category_id is not None:
        params1["category_id"] = str(category_id)

    url1 = f"{API_BASE}/components?{urllib.parse.urlencode(params1)}"
    resp1 = await _api_get(url1)
    data1 = resp1.json()

    search_id = None
    api_category_id = None
    for comp in data1.get("components", []):
        if comp.get("type") == "search_results":
            qp = comp["type_data"]["query_params"]
            search_id = qp["search_id"]
            api_category_id = qp.get("category_id")
            break

    if not search_id:
        return {"items": [], "total": 0, "next_page": None, "search_id": None, "category_id": None}

    # Step 2: fetch results
    params2 = {
        "keywords": keywords,
        "order_by": order_by,
        "search_id": search_id,
        "latitude": str(lat),
        "longitude": str(lon),
        "section_type": "organic_search_results",
        "source": "deep_link",
    }
    if api_category_id:
        params2["category_id"] = str(api_category_id)

    url2 = f"{API_BASE}/section?{urllib.parse.urlencode(params2)}"
    resp2 = await _api_get(url2)
    data2 = resp2.json()

    raw_items = data2.get("data", {}).get("section", {}).get("items", [])
    next_page = data2.get("meta", {}).get("next_page")

    # Client-side filtering
    items = []
    for item in raw_items:
        if _is_reserved(item):
            continue
        price = _get_price(item)
        if min_price is not None and price < min_price:
            continue
        if max_price is not None and price > max_price:
            continue
        items.append(_format_item(item))

    return {
        "items": items,
        "total": len(items),
        "next_page": next_page,
        "search_id": search_id,
        "category_id": api_category_id,
    }


@mcp.tool()
async def wallapop_search_next_page(
    keywords: str,
    search_id: str,
    next_page: str,
    city: str = "valencia",
    order_by: str = "most_relevance",
    category_id: Optional[int] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
) -> dict:
    """Continue a previous search with pagination.

    Args:
        keywords: Same keywords as original search
        search_id: search_id from the original search result
        next_page: JWT pagination token from previous result's next_page field
        city: One of valencia, madrid, barcelona
        order_by: Sort order used in original search
        category_id: Category ID from original search (if any)
        min_price: Optional minimum price filter (client-side)
        max_price: Optional maximum price filter (client-side)
    """
    lat, lon = _coords(city)

    params = {
        "keywords": keywords,
        "order_by": order_by,
        "search_id": search_id,
        "latitude": str(lat),
        "longitude": str(lon),
        "section_type": "organic_search_results",
        "source": "deep_link",
        "next_page": next_page,
    }
    if category_id is not None:
        params["category_id"] = str(category_id)

    url = f"{API_BASE}/section?{urllib.parse.urlencode(params)}"
    resp = await _api_get(url)
    data = resp.json()

    raw_items = data.get("data", {}).get("section", {}).get("items", [])
    new_next_page = data.get("meta", {}).get("next_page")

    items = []
    for item in raw_items:
        if _is_reserved(item):
            continue
        price = _get_price(item)
        if min_price is not None and price < min_price:
            continue
        if max_price is not None and price > max_price:
            continue
        items.append(_format_item(item))

    return {
        "items": items,
        "total": len(items),
        "next_page": new_next_page,
        "search_id": search_id,
        "category_id": category_id,
    }


@mcp.tool()
async def wallapop_item_details(slug: str) -> dict:
    """Get full item details via SSR scraping. Accepts a slug or full wallapop URL.

    Args:
        slug: Item slug (e.g. 'mini-pc-i7-12345') or full URL
    """
    slug = _extract_slug(slug)
    url = f"{SSR_BASE}/item/{slug}"

    resp = await _ssr_get(url)
    pp = _parse_ssr(resp.text)

    item = pp.get("item", {})
    seller = pp.get("itemSeller", {})
    delivery = pp.get("itemDeliveryInfo", {})

    price = item.get("price", {})
    if isinstance(price, dict) and "cash" in price:
        price_val = price["cash"].get("amount", 0)
        currency = price["cash"].get("currency", "EUR")
    elif isinstance(price, dict):
        price_val = price.get("amount", 0)
        currency = price.get("currency", "EUR")
    else:
        price_val = 0
        currency = "EUR"

    images = []
    for img in item.get("images", []):
        if isinstance(img, dict):
            images.append(img.get("urls", {}).get("big", img.get("url", "")))
        elif isinstance(img, str):
            images.append(img)

    characteristics = {}
    for ch in item.get("characteristics", []):
        if isinstance(ch, dict):
            characteristics[ch.get("title", ch.get("key", ""))] = ch.get("value", ch.get("text", ""))

    return {
        "title": _get_title(item),
        "description": _get_description(item),
        "price": price_val,
        "currency": currency,
        "condition": item.get("condition", ""),
        "category_id": item.get("categoryId", item.get("category_id")),
        "seller": {
            "name": seller.get("name", ""),
            "slug": seller.get("slug", seller.get("webSlug", "")),
            "city": seller.get("location", {}).get("city", ""),
            "country": seller.get("location", {}).get("countryCode", ""),
        },
        "delivery": delivery,
        "images": images[:5],
        "characteristics": characteristics,
        "link": f"https://es.wallapop.com/item/{slug}",
    }


@mcp.tool()
async def wallapop_seller_info(user_slug: str) -> dict:
    """Get seller profile info via SSR scraping.

    Args:
        user_slug: Seller's URL slug (e.g. 'sergiof-462579195')
    """
    user_slug = user_slug.strip()
    if "/user/" in user_slug:
        user_slug = user_slug.split("/user/")[-1].split("?")[0].split("#")[0]

    url = f"{SSR_BASE}/user/{user_slug}"
    resp = await _ssr_get(url)
    pp = _parse_ssr(resp.text)

    user = pp.get("user", {})
    stats = pp.get("userStats", {})
    counters = stats.get("counters", {})
    ratings = stats.get("ratings", {})

    reg_ts = user.get("registerDate", 0)
    since = ""
    if reg_ts:
        since = datetime.fromtimestamp(reg_ts / 1000).strftime("%Y-%m")

    ship = pp.get("shippingCounter", {})
    if isinstance(ship, dict):
        shipments = ship.get("succeededCount", 0)
    else:
        shipments = ship or 0

    published = pp.get("publishedItems", [])

    return {
        "name": user.get("name", ""),
        "slug": user_slug,
        "rating": ratings.get("reviews", None),
        "reviews": counters.get("reviews", 0),
        "sold": counters.get("sold", 0),
        "shipments": shipments,
        "since": since,
        "top_seller": user.get("isTopProfile", False),
        "city": user.get("location", {}).get("city", ""),
        "country": user.get("location", {}).get("countryCode", ""),
        "published_items_count": len(published) if isinstance(published, list) else 0,
        "link": f"https://es.wallapop.com/user/{user_slug}",
    }


@mcp.tool()
async def wallapop_batch_search(
    keywords: list[str],
    cities: list[str] | None = None,
    order_by: str = "most_relevance",
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    max_pages: int = 1,
) -> dict:
    """Search multiple keywords across multiple cities with deduplication.

    Args:
        keywords: List of search queries
        cities: List of cities (valencia, madrid, barcelona). Default: ["valencia"]
        order_by: Sort order
        min_price: Optional minimum price filter
        max_price: Optional maximum price filter
        max_pages: Max pages to fetch per keyword+city combo (default 1)
    """
    if cities is None:
        cities = ["valencia"]

    seen_slugs: set[str] = set()
    all_items: list[dict] = []

    for kw in keywords:
        for city in cities:
            result = await wallapop_search(
                keywords=kw,
                city=city,
                order_by=order_by,
                min_price=min_price,
                max_price=max_price,
            )

            for item in result["items"]:
                if item["slug"] not in seen_slugs:
                    seen_slugs.add(item["slug"])
                    all_items.append(item)

            # Pagination
            next_page = result.get("next_page")
            search_id = result.get("search_id")
            category_id = result.get("category_id")
            pages_fetched = 1

            while next_page and pages_fetched < max_pages and search_id:
                await asyncio.sleep(0.3)
                page_result = await wallapop_search_next_page(
                    keywords=kw,
                    search_id=search_id,
                    next_page=next_page,
                    city=city,
                    order_by=order_by,
                    category_id=category_id,
                    min_price=min_price,
                    max_price=max_price,
                )
                for item in page_result["items"]:
                    if item["slug"] not in seen_slugs:
                        seen_slugs.add(item["slug"])
                        all_items.append(item)
                next_page = page_result.get("next_page")
                pages_fetched += 1

            await asyncio.sleep(0.3)  # rate limit between queries

    return {
        "items": all_items,
        "total": len(all_items),
        "queries": len(keywords),
        "cities": cities,
    }


@mcp.tool()
async def wallapop_categories() -> dict:
    """List all Wallapop categories via SSR scraping of the homepage."""
    url = SSR_BASE + "/"
    resp = await _ssr_get(url)
    pp = _parse_ssr(resp.text)

    categories = []
    for cat in pp.get("categories", []):
        subcats = []
        for sub in cat.get("subcategories", []):
            subcats.append({
                "id": sub.get("categoryId"),
                "name": sub.get("title", ""),
            })
        categories.append({
            "id": cat.get("categoryId"),
            "name": cat.get("title", ""),
            "subcategories": subcats,
        })

    return {"categories": categories, "total": len(categories)}


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run(transport="stdio")
