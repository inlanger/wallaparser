# Wallapop API Structure

> Collected by analyzing the es.wallapop.com frontend (Next.js SSR/CSR app)
> Date: 2026-02-12

---

## 1. Domains and Base URLs

| Domain | Purpose |
|--------|---------|
| `api.wallapop.com` | Main API (v3) |
| `es.wallapop.com` | Web frontend + Next.js BFF API routes |
| `feature-flag.wallapop.com` | Feature flags |
| `tracking.wallapop.com` | Analytics/tracking (RudderStack) |
| `web-static.wallapop.com` | Static assets (icons, SVG) |
| `cdn.wallapop.com` | Product image CDN |
| `cdn-web-home-images.wallapop.com` | Homepage image CDN |
| `about.wallapop.com` | About, legal documents |
| `ayuda.wallapop.com` | Help center (ES) |
| `ajuda.wallapop.com` | Help center (PT) |
| `assistenza.wallapop.com` | Help center (IT) |

---

## 2. API Endpoints

### 2.1 Wallapop Core API (`api.wallapop.com`)

#### Search
| Method | Endpoint | Parameters | Description |
|--------|----------|------------|-------------|
| GET | `/api/v3/search/components` | `keywords`, `category_id`, `source` | Main search — returns search result components |
| GET | `/api/v3/search/section` | `keywords`, `source`, `category_id`, `search_id`, `order_by`, `latitude`, `longitude`, `section_type` | Search result sections (pagination, lazy load) |
| GET | `/api/v3/search/filters/regular-filters` | `keywords`, `source`, `category_id`, `order_by` | Available search filters |
| GET | `/api/v3/search/filters/brand` | `category_id`, `keywords`, `order_by` | Brand filters |
| GET | `/api/v3/search/filters/model` | `category_id`, `keywords`, `order_by` | Model filters |
| GET | `/api/v3/suggesters/nonlocated` | — | Autocomplete/search suggestions |

#### Item Detail
| Method | Endpoint | Parameters | Description |
|--------|----------|------------|-------------|
| GET | `/api/v3/item-detail/components` | `item_id` | Full item info (SSR + CSR) |
| GET | `/api/v3/items/{id}` | — | Specific item data |
| GET | `/api/v3/recommendations/{id}` | — | Item-based recommendations |
| GET | `/api/v3/stock/{id}` | — | Stock info |

#### Users
| Method | Endpoint | Parameters | Description |
|--------|----------|------------|-------------|
| GET | `/api/v3/users/{id}` | — | User profile |
| GET | `/api/v3/user/type` | — | Current user type |
| GET | `/api/v3/user/bottom-bar` | — | Bottom bar configuration |
| GET | `/api/v3/user-consents` | — | User consents |

#### Auth/Access
| Method | Endpoint | Parameters | Description |
|--------|----------|------------|-------------|
| POST | `/api/v3/access/login` | — | Login (username/password) |
| POST | `/api/v3/access/email` | — | Email login |
| POST | `/api/v3/access/google` | — | OAuth via Google |
| POST | `/api/v3/access/facebook` | — | OAuth via Facebook |
| POST | `/api/v3/access/authorize` | — | Authorization |
| POST | `/api/v3/access/refresh` | — | Token refresh |
| POST | `/api/v3/mfa/validate` | — | MFA validation |
| POST | `/api/v3/mfa/resend-authorization` | — | Resend MFA code |

#### Categories and Navigation
| Method | Endpoint | Parameters | Description |
|--------|----------|------------|-------------|
| GET | `/api/v3/categories` | `context` | Category list |
| GET | `/api/v3/navigation/categories` | — | Navigation categories |

#### Ads and Personalization
| Method | Endpoint | Parameters | Description |
|--------|----------|------------|-------------|
| GET | `/api/v3/ads/configuration/user/{id}` | — | Ad configuration for user |
| GET | `/api/v3/personalization/experiment` | `initiative` | A/B experiments |

#### Notifications and Messaging
| Method | Endpoint | Parameters | Description |
|--------|----------|------------|-------------|
| GET | `/api/v3/instant-messaging/messages/unread` | — | Unread messages |

#### Search Alerts
| Method | Endpoint | Parameters | Description |
|--------|----------|------------|-------------|
| GET | `/api/v3/searchalerts/savedsearch` | — | Saved searches |
| GET | `/api/v3/searchalerts/savedsearch/exists` | `category_id`, `keywords`, `order_by` | Check if saved search exists |

#### Legacy API (v1)
| Method | Endpoint | Description |
|--------|----------|-------------|
| — | `/api/v1/access` | Authentication (legacy) |
| — | `/api/v1/application` | Application info |

### 2.2 Feature Flags (`feature-flag.wallapop.com`)
| Method | Endpoint | Parameters | Description |
|--------|----------|------------|-------------|
| GET | `/api/v3/featureflag` | `featureFlags` | Get feature flags |

### 2.3 Next.js BFF Routes (`es.wallapop.com`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/auth/session` | Current user session |
| POST | `/api/auth/signin` | Sign in |
| POST | `/api/auth/delete-session` | Sign out (delete session) |
| GET | `/api/auth/go-to-signout` | Redirect to sign out |
| GET | `/api/delivery/dispute` | Delivery dispute info |
| GET | `/api/delivery/timeline` | Delivery timeline |
| GET | `/api/health` | Healthcheck |
| GET | `/api/identity/v2/envelope` | Identity |
| GET | `/api/identity/v2/envelope/refresh` | Identity refresh |
| GET | `/api/robots` | Robots configuration |
| GET | `/api/static-redirect` | Static redirects |
| GET | `/api/m/{path}` | Mobile deep link proxy |

### 2.4 Tracking (`tracking.wallapop.com`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/v1/batch` | Batch event submission |
| GET | `/v1/identities/resolve` | Resolve user identifier |
| GET | `/sourceConfig/` | Source configuration |

---

## 3. Data Models

### 3.1 Item
```json
{
  "id": "string",
  "title": {
    "original": "string",
    "translated": "string | null"
  },
  "description": {
    "original": "string",
    "translated": "string | null"
  },
  "characteristics": "string",
  "taxonomies": [
    {
      "id": "string",
      "name": "string",
      "icon": "string",
      "link": "string"
    }
  ],
  "type": "consumerGoods | car | motorbike | realEstate",
  "userId": "string",
  "slug": "string",
  "shareUrl": "string",
  "modifiedDate": "number (timestamp ms)",
  "images": [
    {
      "id": "string",
      "averageColor": "string (hex)",
      "urls": {
        "small": "string (URL)",
        "medium": "string (URL)",
        "big": "string (URL)"
      }
    }
  ],
  "price": {
    "cash": {
      "amount": "number",
      "currency": "string (EUR)"
    },
    "financed": "object | null"
  },
  "retailPrice": "object | null",
  "location": {
    "latitude": "number",
    "longitude": "number",
    "approximated": "boolean",
    "countryCode": "string (ES)",
    "city": "string",
    "postalCode": "string"
  },
  "flags": {
    "reserved": "boolean",
    "bumped": "boolean",
    "sold": "boolean",
    "expired": "boolean",
    "favorited": "boolean",
    "onHold": "boolean",
    "bumpType": "string | null"
  },
  "shipping": {
    "isItemShippable": "boolean",
    "isShippingAllowedByUser": "boolean"
  },
  "views": "number",
  "favorites": "number",
  "isBulky": "boolean",
  "measures": "object | null",
  "brand": "string | null",
  "model": "string | null",
  "isbn": "string | null",
  "condition": "string | null",
  "hashtags": "string[] | null",
  "isRefurbished": "boolean",
  "isTopProfile": "boolean",
  "stock": "object | null",
  "characteristicsDetails": [
    {
      "attribute": "string",
      "value": "string"
    }
  ],
  "goodsAndFashionInfo": {
    "upToKg": "object | null",
    "size": "object | null",
    "color": {
      "iconText": "string",
      "text": "string",
      "title": "string",
      "value": "string"
    }
  },
  "carInfo": {
    "km": { "iconText": "string", "text": "string", "title": "string", "value": "string" },
    "year": { "iconText": "string", "text": "string", "title": "string", "value": "string" },
    "version": { "iconText": "string", "text": "string", "title": "string", "value": "string" },
    "gearBox": { "iconText": "string", "text": "string", "title": "string", "value": "string" },
    "engine": { "iconText": "string", "text": "string", "title": "string", "value": "string" },
    "color": { "iconText": "string", "text": "string", "title": "string", "value": "string" },
    "horsePower": { "iconText": "string", "text": "string", "title": "string", "value": "string" },
    "bodyType": { "iconText": "string", "text": "string", "title": "string", "value": "string" },
    "doors": { "iconText": "string", "text": "string", "title": "string", "value": "string" },
    "warranty": { "iconText": "string", "text": "string", "title": "string", "value": "string" },
    "seats": { "iconText": "string", "text": "string", "title": "string", "value": "string" }
  },
  "realEstateInfo": "object | null"
}
```

### 3.2 Item SEO
```json
{
  "pageTitle": "string",
  "pageH1": "string",
  "breadCrumbs": "array",
  "metas": "object",
  "mobileBubble": "object",
  "crossSellingBubbles": "array",
  "location": "object"
}
```

### 3.3 Item Delivery Info
```json
{
  "callToAction": "string (f2f | buy | ...)",
  "offerCallToAction": "string",
  "deliveryOptions": "array",
  "deliveryTime": "object | null",
  "shippingAllowed": "boolean",
  "isBulkyBannerEnabled": "boolean",
  "deliverySaleConditions": "object | null",
  "installmentPaymentMethods": "array | null",
  "bundleActions": "object | null",
  "isExternalCarrier": "boolean"
}
```

### 3.4 User / Seller
```json
{
  "id": "string",
  "microName": "string",
  "type": "string (normal | pro)",
  "webSlug": "string",
  "featured": "boolean",
  "registerDate": "number (timestamp)",
  "avatarImage": {
    "urls": {
      "small": "string (URL)",
      "medium": "string (URL)",
      "big": "string (URL)"
    }
  },
  "location": {
    "city": "string",
    "zip": "string",
    "approxRadius": "number",
    "countryCode": "string",
    "country": "string",
    "region2": "string",
    "title": "string",
    "latitude": "number",
    "longitude": "number",
    "approximatedLocation": "boolean",
    "fullAddress": "string | null"
  },
  "urlShare": "string (URL)",
  "extraInfoPro": "object | null",
  "badgeType": "string | null",
  "isVacationModeEnabled": "boolean",
  "listingProtected": "boolean",
  "isTopProfile": "boolean",
  "sellerType": "string | null",
  "officialStoreUrl": "string | null",
  "stats": {
    "ratings": {
      "reviews": "number (0-100 score)"
    },
    "counters": {
      "publish": "number",
      "buys": "number",
      "sells": "number",
      "favorites": "number",
      "views": "number",
      "profileFavoritedReceived": "number",
      "profileFavorited": "number",
      "reviews": "number",
      "sold": "number",
      "reportsReceived": "number",
      "onHold": "number",
      "featured": "number",
      "shippingCounter": "number"
    }
  }
}
```

### 3.5 User Profile Page (additional fields)
```json
{
  "user": "User (see above)",
  "publishedItems": {
    "meta": "object (pagination)",
    "data": "Item[]"
  },
  "userStats": {
    "ratings": { "reviews": "number" },
    "counters": { "...": "number" }
  },
  "userType": { "type": "string (unknown | normal | pro)" },
  "shippingCounter": { "succeededCount": "number" },
  "userCover": "object | null",
  "isBundleAllowed": "boolean"
}
```

### 3.6 Category
```json
{
  "title": "string",
  "categoryId": "number",
  "url": "string (URL)",
  "icon": "string",
  "subcategories": [
    {
      "title": "string",
      "categoryId": "number"
    }
  ]
}
```

### 3.7 Search Result Item (lighter model)
```json
{
  "id": "string",
  "user_id": "string",
  "title": "string",
  "description": "string",
  "category_id": "number",
  "price": { "amount": 0.0, "currency": "EUR" },
  "images": [{ "id": "string", "urls": { "small": "url", "medium": "url", "big": "url" } }],
  "reserved": "boolean",
  "location": { "city": "string", "postal_code": "string", "country_code": "string" },
  "shipping": {
    "item_is_shippable": "boolean",
    "user_allows_shipping": "boolean",
    "cost_configuration_id": "string | null"
  },
  "favorited": "boolean",
  "bump": "object | null",
  "web_slug": "string",
  "created_at": "timestamp",
  "modified_at": "timestamp",
  "taxonomy": "object",
  "is_favoriteable": "boolean",
  "is_refurbished": "boolean",
  "is_top_profile": "boolean",
  "has_warranty": "boolean"
}
```

---

## 4. Categories (full list)

| ID | Name | Icon | Subcategories |
|----|------|------|---------------|
| 100 | Coches | car | 0 |
| 14000 | Motos | motorbike | 0 |
| 12800 | Motor y accesorios | helmet | 5 |
| 12465 | Moda y accesorios | tshirt | 5 |
| 200 | Inmobiliaria | house | 0 |
| 12545 | Tecnología y electrónica | chip | 0 |
| 16000 | Móviles y Telefonía | cellphone | 0 |
| 15000 | Informática | computer | 0 |
| 12579 | Deporte y ocio | basketball | 16 |
| 17000 | Bicicletas | bike | 5 |
| 12900 | Consolas y Videojuegos | game_controller | 0 |
| 12467 | Hogar y jardín | sofa | 8 |
| 13100 | Electrodomésticos | washing_machine | 6 |
| 12463 | Cine, libros y música | open_book | 3 |
| 12461 | Niños y bebés | pram | 13 |
| 18000 | Coleccionismo | painting | 16 |
| 19000 | Construcción y reformas | bricks | 10 |
| 20000 | Industria y agricultura | sickle | 2 |
| 21000 | Empleo | briefcase | 2 |
| 13200 | Servicios | wrench | 8 |
| 24200 | (Tecnología y electrónica — alias) | robot | — |

---

## 5. Frontend Routes (Next.js Pages)

| Route | Description |
|-------|-------------|
| `/` | Home page |
| `/search` | Search (CSR) |
| `/search/favorites` | Favorited items |
| `/item/[itemSlug]` | Item page |
| `/user/[userSlug]/[[...tabSelected]]` | User profile |
| `/auth/signin` | Sign in |
| `/auth/signup` | Sign up |
| `/auth/signup/[token]` | Registration confirmation |
| `/auth/forgot-password` | Password recovery |
| `/auth/reset-password/[token]` | Password reset |
| `/auth/account-recovery/[token]` | Account recovery |
| `/auth/onboarding` | Onboarding |
| `/auth/signout` | Sign out |
| `/checkout/[id]` | Checkout |
| `/checkout/[id]/[step]` | Checkout steps |
| `/bundle-manager/[userId]` | Bundle management |
| `/new-subscription/[subscriptionType]/[[...step]]` | Subscription |
| `/wall` | Wall (feed) |
| `/discover-content` | Discovery content |
| `/recommended-videos/[videoId]` | Recommended videos |
| `/app/search` | Search (in-app) |
| `/sitemap` | Sitemap |
| `/sitemap/[regionSlug]` | Sitemap by region |
| `/wallapop-pro` | Wallapop Pro |
| `/wallapop-pro-cars` | Wallapop Pro for cars |
| `/wallapop-pro-contact` | Pro contact |
| `/envios-wallapop` | Wallapop delivery |
| `/[...seo-landing]` | SEO landing pages (catch-all) |
| `/legacy` | Legacy page |
| `/not-available` | Not available |
| `/error` | Error |

---

## 6. Search Parameters (Query Parameters)

Main parameters for `/search`:
- `keywords` — search keywords
- `category_id` — category ID
- `order_by` — sort order (`most_relevance`, `newest`, `price_low_to_high`, `price_high_to_low`)
- `latitude` / `longitude` — coordinates for geo search
- `source` — request source
- `search_id` — search session ID
- `section_type` — result section type

---

## 7. CDN and Images

Product images are stored at `cdn.wallapop.com/images/` in three sizes:
- `small` — thumbnail
- `medium` — medium size
- `big` — full size

URL format: `https://cdn.wallapop.com/images/{bucket}/{path}`

Homepage images: `https://cdn-web-home-images.wallapop.com/home-images-prod/`

Design system static assets: `https://web-static.wallapop.com/design-system/`

---

## 8. API Request Authentication (curl)

The following headers are required for API access via curl/programmatically:

```bash
curl -s 'https://api.wallapop.com/api/v3/...' \
  -H 'Accept: application/json, text/plain, */*' \
  -H 'Origin: https://es.wallapop.com' \
  -H 'Referer: https://es.wallapop.com/' \
  -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36' \
  -H 'X-DeviceOS: 0'
```

**Required headers:**
- `Origin: https://es.wallapop.com` — without it: 403 (CloudFront)
- `Referer: https://es.wallapop.com/` — without it: 403
- `X-DeviceOS: 0` — platform identifier (0 = web)
- `User-Agent` — standard browser string

**Authorization not required** for: search, item browsing, categories, filters.

---

## 9. Two-Step Search (Search Flow)

Search works in two steps:

### Step 1: Get search configuration
```
GET /api/v3/search/components?keywords=...&category_id=...&order_by=...&source=search_box
```
Returns:
- `components[]` — UI components (ads_banner, slider, search_results)
- `search_results.type_data.query_params.search_id` — **unique search session ID**
- `filters` — available filters
- `search_controls` — controls

### Step 2: Get results
```
GET /api/v3/search/section?keywords=...&category_id=...&order_by=...&search_id=<from step 1>&latitude=...&longitude=...&section_type=organic_search_results&source=deep_link
```
Returns:
- `data.section.items[]` — array of items (up to 40)
- `meta.next_page` — JWT token for the next page

### Pagination
To load the next page, pass `meta.next_page` as query parameter `next_page` to the same `/api/v3/search/section` endpoint with the same parameters. The value is a JWT token — URL-encode it. When `meta.next_page` is `null` or absent — no more pages.

### Search result item structure
```json
{
  "id": "string",
  "user_id": "string",
  "title": "string",
  "description": "string",
  "category_id": "number",
  "price": { "amount": 0.0, "currency": "EUR" },
  "images": [{ "id": "string", "urls": { "small": "url", "medium": "url", "big": "url" } }],
  "reserved": "boolean",
  "location": { "city": "string", "postal_code": "string", "country_code": "string" },
  "shipping": {
    "item_is_shippable": "boolean",
    "user_allows_shipping": "boolean",
    "cost_configuration_id": "string | null"
  },
  "favorited": "boolean",
  "bump": "object | null",
  "web_slug": "string",
  "created_at": "timestamp",
  "modified_at": "timestamp",
  "taxonomy": "object",
  "is_favoriteable": "boolean",
  "is_refurbished": "boolean",
  "is_top_profile": "boolean",
  "has_warranty": "boolean"
}
```

### Alternative method: SSR Scraping
To get full item data, parse `__NEXT_DATA__` from the HTML:
```bash
curl -s 'https://es.wallapop.com/item/<slug>' | python3 -c "
import sys, re, json
html = sys.stdin.read()
match = re.search(r'<script id=\"__NEXT_DATA__\" type=\"application/json\">(.*?)</script>', html)
data = json.loads(match.group(1))
item = data['props']['pageProps']['item']
print(json.dumps(item, indent=2))
"
```
Works without special headers and returns the full Item model.

---

## 10. Frontend Tech Stack

- **Framework:** Next.js (SSR + CSR)
- **State Management:** Jotai
- **I18n:** React Intl
- **Error Tracking:** Sentry
- **Analytics:** Amplitude, RudderStack (tracking.wallapop.com)
- **Feature Flags:** Custom service (feature-flag.wallapop.com)
- **Auth:** Custom system + Google/Facebook OAuth
- **Consent:** Didomi (CMP)
