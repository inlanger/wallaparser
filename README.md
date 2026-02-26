# wallapop-mcp

MCP server for searching and scraping the Wallapop marketplace. Provides 6 tools that Claude Code (or any MCP client) can call directly — no more hand-crafting curl commands with headers.

Built with [FastMCP](https://github.com/modelcontextprotocol/python-sdk) + [httpx](https://www.python-httpx.org/).

## Tools

| Tool | Description |
|---|---|
| `wallapop_search` | Search items by keyword with city, sort, category, and price filters |
| `wallapop_search_next_page` | Paginate through search results using JWT token |
| `wallapop_item_details` | Full item specs via SSR scraping (description, condition, delivery, images) |
| `wallapop_seller_info` | Seller profile via SSR (rating, reviews, shipments, registration date) |
| `wallapop_batch_search` | Multi-keyword, multi-city search with automatic deduplication |
| `wallapop_categories` | List all marketplace categories and subcategories |

## Setup

### With Claude Code

```bash
claude mcp add wallapop -- \
  uv run --with "mcp[cli]" --with httpx \
  python /absolute/path/to/wallapop-mcp/server.py
```

Or add manually to `~/.claude.json` under your project:

```json
{
  "projects": {
    "/path/to/your/project": {
      "mcpServers": {
        "wallapop": {
          "type": "stdio",
          "command": "uv",
          "args": [
            "run", "--with", "mcp[cli]", "--with", "httpx",
            "python", "/absolute/path/to/wallapop-mcp/server.py"
          ]
        }
      }
    }
  }
}
```

### Verify it works

Start a new Claude Code session and try any tool — they'll appear as `mcp__wallapop__*`.

## Usage examples

### Basic search

Search for mini PCs in Valencia, sorted by price:

```
wallapop_search(keywords="mini pc i7", city="valencia", order_by="price_low_to_high")
```

Returns up to 40 items with slug, title, price, city, shipping info, and direct link.

### Search with price filter

```
wallapop_search(keywords="macbook pro", city="madrid", min_price=300, max_price=800)
```

Price filtering is done client-side — the API doesn't support it natively.

### Paginate results

Use `search_id` and `next_page` from the previous response:

```
wallapop_search_next_page(
    keywords="macbook pro",
    search_id="abc-123",
    next_page="eyJhbGciOi...",
    city="madrid"
)
```

Keep calling until `next_page` is `null`.

### Get item details

Accepts a slug or full URL:

```
wallapop_item_details(slug="intel-nuc-i7-1165g7-16gb-ram-mini-pc-1234343492")

wallapop_item_details(slug="https://es.wallapop.com/item/intel-nuc-i7-1165g7-16gb-ram-mini-pc-1234343492")
```

Returns title, full description, price, condition, seller info, delivery options, images, and characteristics.

### Check a seller

```
wallapop_seller_info(user_slug="sergiof-462579195")
```

Returns rating (0-100), review count, items sold, successful shipments, registration date, top seller status.

**Quick trust check:** rating 90+ with 20+ reviews = reliable. High shipment count = handles logistics well. Recent registration + expensive items = potential scam risk.

### Batch search across cities

Search multiple keywords across multiple cities — results are deduplicated by slug:

```
wallapop_batch_search(
    keywords=["mini pc i7", "nuc i7", "ordenador pequeño i7"],
    cities=["valencia", "madrid", "barcelona"],
    max_price=300,
    max_pages=2
)
```

This runs 3 keywords x 3 cities = 9 searches (with pagination up to 2 pages each), deduplicates, and returns unique items. Rate limited at 0.3s between requests.

### List categories

```
wallapop_categories()
```

Returns all categories with IDs and subcategories. Common ones:

| ID | Category |
|---|---|
| 15000 | Informática |
| 16000 | Móviles y Telefonía |
| 12900 | Consolas y Videojuegos |
| 12467 | Hogar y jardín |
| 13100 | Electrodomésticos |

Pass `category_id` to `wallapop_search` to narrow results.

## How it works

- **Search** is two-step: first `/api/v3/search/components` to get a `search_id`, then `/api/v3/search/section` to get items. The server handles this automatically.
- **Item details** and **seller info** use SSR scraping — fetching the HTML page and extracting `__NEXT_DATA__` JSON, which contains richer data than the API.
- **Error handling:** 403 → retries with rotated User-Agent; 429 → exponential backoff (5s, 10s, 20s); missing `__NEXT_DATA__` → reports captcha/block.
- **Reserved items** are automatically filtered out of search results.
- **Price** field has two formats in the API (`price.amount` and `price.cash.amount`) — both are handled.

## Project structure

```
wallapop-mcp/
├── server.py                              # MCP server (6 tools, ~540 lines)
├── pyproject.toml                         # Dependencies: mcp[cli], httpx
├── uv.lock
└── skill/
    ├── SKILL.md                           # Claude Code skill (API workflows, rules, pitfalls)
    └── references/
        └── wallapop-api-reference.md      # Full API reference (endpoints, data models)
```

## Supported cities

| City | Coordinates |
|---|---|
| Valencia (default) | 39.4699, -0.3763 |
| Madrid | 40.4168, -3.7038 |
| Barcelona | 41.39, 2.17 |

## Requirements

- Python >= 3.10
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- No API keys needed — Wallapop's search API is public
