# wallapop-mcp

MCP server + Claude Code skill for searching Wallapop marketplace.

## Setup

### 1. Add the MCP server

```bash
claude mcp add wallapop -- uv run --with "mcp[cli]" --with httpx python /absolute/path/to/server.py
```

### 2. Install the skill

Copy `skill/SKILL.md` to your Claude Code skills directory:

```bash
mkdir -p ~/.claude/skills/wallapop
cp skill/SKILL.md ~/.claude/skills/wallapop/SKILL.md
cp -r skill/references ~/.claude/skills/wallapop/references
```

The skill teaches Claude how to use the MCP tools, when to paginate, how to handle errors, and when to fall back to raw `curl` + `python3` for tasks the MCP doesn't cover.

## Tools available

| Tool | What it does |
|---|---|
| `mcp__wallapop__wallapop_search` | Search by keyword, city, sort, category, price |
| `mcp__wallapop__wallapop_search_next_page` | Paginate via JWT token |
| `mcp__wallapop__wallapop_item_details` | Full item data via SSR scraping |
| `mcp__wallapop__wallapop_seller_info` | Seller profile, rating, reviews |
| `mcp__wallapop__wallapop_batch_search` | Multi-keyword + multi-city with deduplication |
| `mcp__wallapop__wallapop_categories` | List all categories and subcategories |

## Usage style

The skill is tuned for **deep, exhaustive search** — multiple keyword variants, multiple cities, full pagination, SSR verification of finalists, seller trust checks. Not just a one-page search.

See `README.md` for full usage examples.
