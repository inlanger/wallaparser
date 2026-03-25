---
name: wallapop
description: >-
  Searches and retrieves data from Wallapop marketplace via its undocumented API.
  Handles item search with filters, item detail pages, user profiles, and category
  browsing. Use when the user asks to search Wallapop, find items on Wallapop,
  check a Wallapop listing, look up a Wallapop seller, parse Wallapop, scrape
  Wallapop, or mentions wallapop.com URLs.
---

# Wallapop API

## Required Headers

All API calls to `api.wallapop.com` need these headers — without them CloudFront returns 403. Set once per session:

```bash
H=(-H 'Accept: application/json, text/plain, */*' \
   -H 'Origin: https://es.wallapop.com' \
   -H 'Referer: https://es.wallapop.com/' \
   -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36' \
   -H 'X-DeviceOS: 0')
```

Use `"${H[@]}"` in all API curl commands below. No auth token needed for search, item detail, categories, or filters.

## Workflows

### Search Items

Search is two-step. First get a `search_id`, then fetch results.

**Step 1 — get search_id:**
```bash
curl -s 'https://api.wallapop.com/api/v3/search/components?keywords=QUERY&order_by=most_relevance&source=search_box' "${H[@]}"
```

`category_id` is optional — omit it for broad discovery, include only when you specifically need to narrow results to a known category.

Extract `search_id` from: `components[type=search_results].type_data.query_params.search_id`

Also grab `category_id` from the same `query_params` if present — pass it to Step 2.

**Step 2 — fetch results:**
```bash
curl -s 'https://api.wallapop.com/api/v3/search/section?keywords=QUERY&order_by=most_relevance&search_id=SEARCH_ID&latitude=LAT&longitude=LON&section_type=organic_search_results&source=deep_link' "${H[@]}"
```

Add `&category_id=ID` only if Step 1 returned one and you want to keep the narrowed scope.

Results are at `data.section.items[]` (up to 40 items). Pagination token at `meta.next_page`.

Use `python3 -c` inline to parse and filter JSON. Example — filter by max price:

```bash
| python3 -c "
import sys, json
items = json.load(sys.stdin)['data']['section']['items']
for i in items:
    if i['price']['amount'] <= 300:
        print('%s EUR | %s' % (i['price']['amount'], i['title']))
        print('  https://es.wallapop.com/item/%s' % i['web_slug'])
"
```

**order_by values:** `most_relevance`, `newest`, `price_low_to_high`, `price_high_to_low`

**Default coordinates (Valencia):** `latitude=39.4699&longitude=-0.3763`

### Pagination

The `meta.next_page` value from Step 2 is a JWT token. Pass it as `next_page` query parameter to the same `search/section` endpoint:

```bash
curl -s 'https://api.wallapop.com/api/v3/search/section?keywords=QUERY&category_id=REAL_CAT_ID&order_by=most_relevance&search_id=SEARCH_ID&latitude=LAT&longitude=LON&section_type=organic_search_results&source=deep_link&next_page=TOKEN' "${H[@]}"
```

The token contains dots and base64 characters — URL-encode it. When `meta.next_page` is `null` or absent, there are no more pages.

### Batch Search

Search multiple keywords in one go with deduplication and filtering. Use inline `python3 -c` — no script files.

```bash
curl -s 'https://api.wallapop.com/api/v3/search/components?keywords=QUERY&order_by=most_relevance&source=search_box' "${H[@]}" | \
python3 -c "
import sys, json
d = json.load(sys.stdin)
for c in d.get('components', []):
    if c.get('type') == 'search_results':
        qp = c['type_data']['query_params']
        print(qp['search_id'], qp.get('category_id', ''))
        break
"
```

Full batch pattern — run for each keyword, collect results, deduplicate:

```bash
python3 -c "
import subprocess, json, re, urllib.parse, time

KEYWORDS = ['keyword1', 'keyword2', 'keyword3']
LAT, LON = 39.4699, -0.3763
HEADERS = ['-H', 'Accept: application/json, text/plain, */*',
           '-H', 'Origin: https://es.wallapop.com',
           '-H', 'Referer: https://es.wallapop.com/',
           '-H', 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
           '-H', 'X-DeviceOS: 0']

seen_slugs = set()
results = []

def is_reserved(item):
    r = item.get('reserved', False)
    if isinstance(r, dict):
        return r.get('flag', False)
    return bool(r)

def is_shippable(item):
    s = item.get('shipping', {})
    return s.get('item_is_shippable', False) or s.get('user_allows_shipping', False)

for kw in KEYWORDS:
    # Step 1: get search_id
    url1 = f'https://api.wallapop.com/api/v3/search/components?keywords={urllib.parse.quote(kw)}&order_by=most_relevance&source=search_box'
    r1 = subprocess.run(['curl', '-s', url1] + HEADERS, capture_output=True, text=True, timeout=30)
    d1 = json.loads(r1.stdout)
    sid, cid = None, None
    for c in d1.get('components', []):
        if c.get('type') == 'search_results':
            qp = c['type_data']['query_params']
            sid, cid = qp['search_id'], qp.get('category_id', '')
            break
    if not sid:
        continue

    # Step 2: fetch results
    url2 = f'https://api.wallapop.com/api/v3/search/section?keywords={urllib.parse.quote(kw)}&category_id={cid}&order_by=most_relevance&search_id={sid}&latitude={LAT}&longitude={LON}&section_type=organic_search_results&source=deep_link'
    r2 = subprocess.run(['curl', '-s', url2] + HEADERS, capture_output=True, text=True, timeout=30)
    d2 = json.loads(r2.stdout)
    items = d2.get('data', {}).get('section', {}).get('items', [])

    for item in items:
        slug = item.get('web_slug', '')
        if not slug or slug in seen_slugs:
            continue
        price = item.get('price', {}).get('amount', 0)
        if price < MIN_PRICE or price > MAX_PRICE:
            continue
        if is_reserved(item):
            continue
        if not is_shippable(item):
            continue
        seen_slugs.add(slug)
        results.append(item)
    time.sleep(1)  # rate limit courtesy

for i, item in enumerate(results, 1):
    print(f\"{i}. {item['price']['amount']}€ | {item['title']}\")
    print(f\"   https://es.wallapop.com/item/{item['web_slug']}\")
"
```

Adapt `KEYWORDS`, `MIN_PRICE`, `MAX_PRICE` per search session. Add pagination by reading `meta.next_page` from Step 2 response.

### Cache

**Cache structure:**
```
wallaparser/cache/
  YYYY-MM-DD/
    search_raw.json      — all items from search (slug, title, price, shipping, location)
    search_filtered.json — filtered candidates
    ssr_items.json       — items with full details via SSR scraping
    sellers.json         — verified sellers
```

**Saving to cache** — after each deep search:
- Merge all raw results (across keywords, cities, sort orders) → `search_raw.json`
- Filtered candidates → `search_filtered.json`
- SSR-verified items → `ssr_items.json` (key = slug, value = full data)
- Verified sellers → `sellers.json` (key = user_slug)

**Loading cache** — before a new search:
- Check `cache/` for folders from the last N days
- Load `search_raw.json` → skip slugs already seen (no redundant SSR)
- Load `sellers.json` → skip already-verified sellers
- Prices in cache may be stale — re-check when needed

**JSON file formats:**
- `search_raw.json`: `[{slug, title, price, city, shipping, ...}, ...]` — array of items as returned by the API
- `search_filtered.json`: same format, subset of search_raw
- `ssr_items.json`: `{slug: {title, description, price, condition, seller, delivery}, ...}` — dict keyed by slug
- `sellers.json`: `{user_slug: {rating, reviews, sold, shipments, since, top, city}, ...}` — dict keyed by user_slug

### Seller Check

Quick seller verification via SSR scraping:

```bash
curl -s 'https://es.wallapop.com/user/USER_SLUG' | python3 -c "
import sys, re, json
from datetime import datetime
html = sys.stdin.read()
m = re.search(r'<script id=\"__NEXT_DATA__\" type=\"application/json\">(.*?)</script>', html)
if not m:
    print('ERROR: no SSR data')
    sys.exit(1)
pp = json.loads(m.group(1))['props']['pageProps']
u = pp.get('user', {})
us = pp.get('userStats', {})
rating = us.get('ratings', {}).get('reviews', 'N/A')
c = us.get('counters', {})
reg = u.get('registerDate', 0)
reg_str = datetime.fromtimestamp(reg/1000).strftime('%Y-%m') if reg else '?'
ship = pp.get('shippingCounter', {})
ship_n = ship.get('succeededCount', 0) if isinstance(ship, dict) else ship
print(f\"Rating: {rating}/100\")
print(f\"Reviews: {c.get('reviews', 0)}\")
print(f\"Sold: {c.get('sold', 0)}\")
print(f\"Shipments: {ship_n}\")
print(f\"Since: {reg_str}\")
print(f\"Top seller: {u.get('isTopProfile', False)}\")
print(f\"Location: {u.get('location', {}).get('city', '?')}, {u.get('location', {}).get('countryCode', '?')}\")
"
```

**What to check:**
- Rating 90+ and 20+ reviews = reliable
- Check shipment count — sellers with many shipments handle logistics well
- Recent registration + expensive items = potential scam risk
- Cross-reference seller location with item description

### Get Item Details

SSR scraping — no special headers needed, returns the richest data:

```bash
curl -s 'https://es.wallapop.com/item/ITEM_SLUG' | python3 -c "
import sys, re, json
html = sys.stdin.read()
m = re.search(r'<script id=\"__NEXT_DATA__\" type=\"application/json\">(.*?)</script>', html)
pp = json.loads(m.group(1))['props']['pageProps']
item = pp['item']
# title and description are now {original, translated} objects
title = item['title']['original'] if isinstance(item.get('title'), dict) else item.get('title')
desc = item['description']['original'] if isinstance(item.get('description'), dict) else item.get('description')
# price is now {cash: {amount, currency}, financed}
price = item.get('price', {})
if isinstance(price, dict) and 'cash' in price:
    price = price['cash']
print(json.dumps({'title': title, 'description': desc, 'price': price, 'condition': item.get('condition'), 'seller': pp['itemSeller'], 'delivery': pp['itemDeliveryInfo']}, indent=2, ensure_ascii=False))
"
```

Accept both slugs and full URLs. If given a URL, extract the slug from after `/item/`.

### Get User Profile

```bash
curl -s 'https://es.wallapop.com/user/USER_SLUG' | python3 -c "
import sys, re, json
html = sys.stdin.read()
m = re.search(r'<script id=\"__NEXT_DATA__\" type=\"application/json\">(.*?)</script>', html)
pp = json.loads(m.group(1))['props']['pageProps']
print(json.dumps({'user': pp['user'], 'stats': pp['userStats'], 'items': pp.get('publishedItems')}, indent=2, ensure_ascii=False))
"
```

### List Categories

```bash
curl -s 'https://es.wallapop.com/' | python3 -c "
import sys, re, json
html = sys.stdin.read()
m = re.search(r'<script id=\"__NEXT_DATA__\" type=\"application/json\">(.*?)</script>', html)
cats = json.loads(m.group(1))['props']['pageProps']['categories']
for c in cats:
    print('%6d | %s (%d subcats)' % (c['categoryId'], c['title'], len(c.get('subcategories', []))))
    for s in c.get('subcategories', []):
        print('       %6d |   %s' % (s['categoryId'], s['title']))
"
```

### Get Search Filters

```bash
curl -s 'https://api.wallapop.com/api/v3/search/filters/regular-filters?keywords=QUERY&category_id=CAT_ID&order_by=most_relevance&source=search_box' "${H[@]}"
```

Also available: `/api/v3/search/filters/brand` and `/api/v3/search/filters/model` with same params.

## Error Handling

- **403 Forbidden** — Headers missing or WAF blocked. Check all 4 required headers are present. If still failing, try a fresh `User-Agent` string (CloudFront may have blocked the current one).
- **429 Too Many Requests** — Rate limited. Back off with exponential delay (start 5s, double each retry, max 3 retries).
- **SSR returns no `__NEXT_DATA__`** — Page may be behind a captcha, or Wallapop changed the HTML structure. Check if the response contains a captcha challenge. If so, the IP is flagged — wait or change network.
- **Empty search results** — Try without `category_id` first. If using one, verify it's correct (the API silently remaps some IDs).
- **`meta.next_page` missing** — Last page of results. Not an error.

## Rules

- Always include all 4 required headers on API calls. Missing any one causes 403.
- Search is always two-step: `components` (for search_id) then `section` (for items).
- `section_type` must be `organic_search_results` (not `search_results`).
- `category_id` is optional — omit it for broad searches, use only when narrowing to a specific known category. If you do pass it in Step 1, the API may remap it — use the returned value in Step 2.
- SSR scraping (curl HTML + parse `__NEXT_DATA__`) works without special headers and returns richer data than the API. Prefer it for item details and user profiles.
- Price filtering is not a server-side param on the section endpoint — filter client-side after fetching.
- Default to Valencia coordinates if user doesn't specify location.
- Present results as a clean table or numbered list, not raw JSON, unless user asks for JSON.
- After a deep search — always save results to `cache/YYYY-MM-DD/`.
- Before a new search — load the cache and skip already-known slugs and sellers.
- **`reserved` field gotcha:** can be `bool` (`"reserved": true`) OR object (`"reserved": {"flag": true}`). Always check both: `r = item.get('reserved', False); reserved = r.get('flag', False) if isinstance(r, dict) else bool(r)`.

## Pitfalls

- **Items from Italy/Portugal in Spanish search** — Wallapop shows cross-border items. They appear in searches with Spanish coordinates but shipping may not work or cost extra. Check seller location.
- **"No envío" in description but `shippable=true` in API** — the API shipping flags (`item_is_shippable`, `user_allows_shipping`) are unreliable. Always read the item description via SSR scraping before trusting shipping availability.
- **Slug contains outdated specs** — the `web_slug` is generated at listing time and never updated. E.g. slug says "32gb" but seller edited description to "16GB". Always verify specs from item detail page, not from the slug.
- **`category_id` is optional** — omit it by default for broad discovery. Only add it when you specifically need to narrow results to a known category. Cross-category noise is easy to filter client-side.

## Common Category IDs

| ID | Name |
|----|------|
| 100 | Coches |
| 14000 | Motos |
| 12465 | Moda y accesorios |
| 200 | Inmobiliaria |
| 16000 | Moviles y Telefonia |
| 15000 | Informatica |
| 12900 | Consolas y Videojuegos |
| 12467 | Hogar y jardin |
| 13100 | Electrodomesticos |

Full API reference, data models, and category list: see [references/wallapop-api-reference.md](references/wallapop-api-reference.md)
