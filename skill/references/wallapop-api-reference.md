# Wallapop API Structure

> Собрано путём анализа фронтенда es.wallapop.com (Next.js SSR/CSR приложение)
> Дата: 2026-02-12

---

## 1. Домены и базовые URL

| Домен | Назначение |
|-------|-----------|
| `api.wallapop.com` | Основной API (v3) |
| `es.wallapop.com` | Веб-фронтенд + Next.js BFF API routes |
| `feature-flag.wallapop.com` | Feature flags |
| `tracking.wallapop.com` | Аналитика/трекинг (RudderStack) |
| `web-static.wallapop.com` | Статика (иконки, SVG) |
| `cdn.wallapop.com` | CDN изображений товаров |
| `cdn-web-home-images.wallapop.com` | CDN изображений для домашней страницы |
| `about.wallapop.com` | О компании, юр. документы |
| `ayuda.wallapop.com` | Справочный центр (ES) |
| `ajuda.wallapop.com` | Справочный центр (PT) |
| `assistenza.wallapop.com` | Справочный центр (IT) |

---

## 2. API Endpoints

### 2.1 Wallapop Core API (`api.wallapop.com`)

#### Поиск (Search)
| Метод | Эндпоинт | Параметры | Описание |
|-------|----------|-----------|----------|
| GET | `/api/v3/search/components` | `keywords`, `category_id`, `source` | Основной поиск — возвращает компоненты поисковой выдачи |
| GET | `/api/v3/search/section` | `keywords`, `source`, `category_id`, `search_id`, `order_by`, `latitude`, `longitude`, `section_type` | Секции результатов поиска (пагинация, подгрузка) |
| GET | `/api/v3/search/filters/regular-filters` | `keywords`, `source`, `category_id`, `order_by` | Доступные фильтры для поиска |
| GET | `/api/v3/search/filters/brand` | `category_id`, `keywords`, `order_by` | Фильтры по брендам |
| GET | `/api/v3/search/filters/model` | `category_id`, `keywords`, `order_by` | Фильтры по моделям |
| GET | `/api/v3/suggesters/nonlocated` | — | Автокомплит/подсказки поиска |

#### Детали товара (Item Detail)
| Метод | Эндпоинт | Параметры | Описание |
|-------|----------|-----------|----------|
| GET | `/api/v3/item-detail/components` | `item_id` | Полная информация о товаре (SSR + CSR) |
| GET | `/api/v3/items/{id}` | — | Данные конкретного товара |
| GET | `/api/v3/recommendations/{id}` | — | Рекомендации на основе товара |
| GET | `/api/v3/stock/{id}` | — | Информация о наличии |

#### Пользователи (Users)
| Метод | Эндпоинт | Параметры | Описание |
|-------|----------|-----------|----------|
| GET | `/api/v3/users/{id}` | — | Профиль пользователя |
| GET | `/api/v3/user/type` | — | Тип текущего пользователя |
| GET | `/api/v3/user/bottom-bar` | — | Конфигурация нижней панели |
| GET | `/api/v3/user-consents` | — | Согласия пользователя |

#### Авторизация (Auth/Access)
| Метод | Эндпоинт | Параметры | Описание |
|-------|----------|-----------|----------|
| POST | `/api/v3/access/login` | — | Вход (логин/пароль) |
| POST | `/api/v3/access/email` | — | Вход по email |
| POST | `/api/v3/access/google` | — | OAuth через Google |
| POST | `/api/v3/access/facebook` | — | OAuth через Facebook |
| POST | `/api/v3/access/authorize` | — | Авторизация |
| POST | `/api/v3/access/refresh` | — | Обновление токена |
| POST | `/api/v3/mfa/validate` | — | Валидация MFA |
| POST | `/api/v3/mfa/resend-authorization` | — | Повторная отправка MFA кода |

#### Категории и навигация
| Метод | Эндпоинт | Параметры | Описание |
|-------|----------|-----------|----------|
| GET | `/api/v3/categories` | `context` | Список категорий |
| GET | `/api/v3/navigation/categories` | — | Категории для навигации |

#### Реклама и персонализация
| Метод | Эндпоинт | Параметры | Описание |
|-------|----------|-----------|----------|
| GET | `/api/v3/ads/configuration/user/{id}` | — | Конфигурация рекламы для пользователя |
| GET | `/api/v3/personalization/experiment` | `initiative` | A/B эксперименты |

#### Уведомления и мессенджер
| Метод | Эндпоинт | Параметры | Описание |
|-------|----------|-----------|----------|
| GET | `/api/v3/instant-messaging/messages/unread` | — | Непрочитанные сообщения |

#### Оповещения поиска
| Метод | Эндпоинт | Параметры | Описание |
|-------|----------|-----------|----------|
| GET | `/api/v3/searchalerts/savedsearch` | — | Сохранённые поиски |
| GET | `/api/v3/searchalerts/savedsearch/exists` | `category_id`, `keywords`, `order_by` | Проверка существования сохранённого поиска |

#### Legacy API (v1)
| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| — | `/api/v1/access` | Авторизация (legacy) |
| — | `/api/v1/application` | Информация о приложении |

### 2.2 Feature Flags (`feature-flag.wallapop.com`)
| Метод | Эндпоинт | Параметры | Описание |
|-------|----------|-----------|----------|
| GET | `/api/v3/featureflag` | `featureFlags` | Получение флагов фич |

### 2.3 Next.js BFF Routes (`es.wallapop.com`)
| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| GET | `/api/auth/session` | Сессия текущего пользователя |
| POST | `/api/auth/signin` | Вход |
| POST | `/api/auth/delete-session` | Выход (удаление сессии) |
| GET | `/api/auth/go-to-signout` | Редирект на выход |
| GET | `/api/delivery/dispute` | Информация о споре по доставке |
| GET | `/api/delivery/timeline` | Таймлайн доставки |
| GET | `/api/health` | Healthcheck |
| GET | `/api/identity/v2/envelope` | Идентификация |
| GET | `/api/identity/v2/envelope/refresh` | Обновление идентификации |
| GET | `/api/robots` | Robots конфигурация |
| GET | `/api/static-redirect` | Статические редиректы |
| GET | `/api/m/{path}` | Мобильный deep link прокси |

### 2.4 Tracking (`tracking.wallapop.com`)
| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| POST | `/v1/batch` | Batch отправка событий |
| GET | `/v1/identities/resolve` | Резолв идентификатора пользователя |
| GET | `/sourceConfig/` | Конфигурация источника |

---

## 3. Модели данных

### 3.1 Item (Товар)
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

### 3.5 User Profile Page (дополнительные поля)
```json
{
  "user": "User (см. выше)",
  "publishedItems": {
    "meta": "object (пагинация)",
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

## 4. Категории (полный список)

| ID | Название | Иконка | Подкатегорий |
|----|---------|--------|-------------|
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

## 5. Маршруты фронтенда (Next.js Pages)

| Маршрут | Описание |
|---------|----------|
| `/` | Главная страница |
| `/search` | Поиск (CSR) |
| `/search/favorites` | Избранные товары |
| `/item/[itemSlug]` | Страница товара |
| `/user/[userSlug]/[[...tabSelected]]` | Профиль пользователя |
| `/auth/signin` | Вход |
| `/auth/signup` | Регистрация |
| `/auth/signup/[token]` | Подтверждение регистрации |
| `/auth/forgot-password` | Восстановление пароля |
| `/auth/reset-password/[token]` | Сброс пароля |
| `/auth/account-recovery/[token]` | Восстановление аккаунта |
| `/auth/onboarding` | Онбординг |
| `/auth/signout` | Выход |
| `/checkout/[id]` | Оформление покупки |
| `/checkout/[id]/[step]` | Шаги оформления |
| `/bundle-manager/[userId]` | Управление бандлами |
| `/new-subscription/[subscriptionType]/[[...step]]` | Подписка |
| `/wall` | Стена (лента) |
| `/discover-content` | Контент для открытий |
| `/recommended-videos/[videoId]` | Рекомендованные видео |
| `/app/search` | Поиск (в приложении) |
| `/sitemap` | Карта сайта |
| `/sitemap/[regionSlug]` | Карта сайта по региону |
| `/wallapop-pro` | Wallapop Pro |
| `/wallapop-pro-cars` | Wallapop Pro для авто |
| `/wallapop-pro-contact` | Контакт Pro |
| `/envios-wallapop` | Доставка Wallapop |
| `/[...seo-landing]` | SEO лендинги (catch-all) |
| `/legacy` | Legacy страница |
| `/not-available` | Недоступно |
| `/error` | Ошибка |

---

## 6. Параметры поиска (Query Parameters)

Основные параметры для `/search`:
- `keywords` — ключевые слова
- `category_id` — ID категории
- `order_by` — сортировка (`most_relevance`, `newest`, `price_low_to_high`, `price_high_to_low`)
- `latitude` / `longitude` — координаты для геопоиска
- `source` — источник запроса
- `search_id` — ID поисковой сессии
- `section_type` — тип секции результатов

---

## 7. CDN и изображения

Изображения товаров хранятся на `cdn.wallapop.com/images/` в трёх размерах:
- `small` — миниатюра
- `medium` — средний размер
- `big` — полный размер

Формат URL: `https://cdn.wallapop.com/images/{bucket}/{path}`

Изображения главной страницы: `https://cdn-web-home-images.wallapop.com/home-images-prod/`

Статика дизайн-системы: `https://web-static.wallapop.com/design-system/`

---

## 8. Авторизация API-запросов (curl)

Для работы с API через curl/программно необходимы следующие хедеры:

```bash
curl -s 'https://api.wallapop.com/api/v3/...' \
  -H 'Accept: application/json, text/plain, */*' \
  -H 'Origin: https://es.wallapop.com' \
  -H 'Referer: https://es.wallapop.com/' \
  -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36' \
  -H 'X-DeviceOS: 0'
```

**Обязательные хедеры:**
- `Origin: https://es.wallapop.com` — без него 403 (CloudFront)
- `Referer: https://es.wallapop.com/` — без него 403
- `X-DeviceOS: 0` — идентификатор платформы (0 = web)
- `User-Agent` — стандартный браузерный

**Авторизация не требуется** для: поиска, просмотра товаров, категорий, фильтров.

---

## 9. Двухшаговый поиск (Search Flow)

Поиск работает в два этапа:

### Шаг 1: Получение конфигурации поиска
```
GET /api/v3/search/components?keywords=...&category_id=...&order_by=...&source=search_box
```
Возвращает:
- `components[]` — компоненты UI (ads_banner, slider, search_results)
- `search_results.type_data.query_params.search_id` — **уникальный ID сессии поиска**
- `filters` — доступные фильтры
- `search_controls` — элементы управления

### Шаг 2: Получение результатов
```
GET /api/v3/search/section?keywords=...&category_id=...&order_by=...&search_id=<из шага 1>&latitude=...&longitude=...&section_type=organic_search_results&source=deep_link
```
Возвращает:
- `data.section.items[]` — массив товаров (до 40 штук)
- `meta.next_page` — JWT-токен для следующей страницы

### Пагинация
Для загрузки следующей страницы передайте `meta.next_page` как query parameter `next_page` в тот же endpoint `/api/v3/search/section` с теми же параметрами. Значение — JWT-токен, его нужно URL-encode. Когда `meta.next_page` равен `null` или отсутствует — страницы закончились.

### Структура элемента поисковой выдачи
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

### Альтернативный метод: SSR Scraping
Для получения полных данных товара можно парсить `__NEXT_DATA__` из HTML:
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
Это работает без специальных хедеров и возвращает полную модель Item.

---

## 10. Технический стек фронтенда

- **Framework:** Next.js (SSR + CSR)
- **State Management:** Jotai
- **I18n:** React Intl
- **Error Tracking:** Sentry
- **Analytics:** Amplitude, RudderStack (tracking.wallapop.com)
- **Feature Flags:** Собственный сервис (feature-flag.wallapop.com)
- **Auth:** Собственная система + Google/Facebook OAuth
- **Consent:** Didomi (CMP)
