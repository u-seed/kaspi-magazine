"""Одноразовый (ручной) парсинг смартфонов Kaspi: 150–350 тыс. ₸, батарея >= 6000 мАч,
без Apple/Samsung, из одинаковых моделей оставляем самую дешёвую. Результат -> data.json"""
import json, re, time, html as htmllib, urllib.request, urllib.parse, datetime
from concurrent.futures import ThreadPoolExecutor

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
BASE = "https://kaspi.kz"
PRICE_MIN, PRICE_MAX, BATT_MIN = 150000, 350000, 6000
EXCLUDE_BRANDS = {"apple", "samsung"}
log_lines = []

def log(s):
    print(s, flush=True); log_lines.append(s)
    open("parse-log.txt", "w").write("\n".join(log_lines))

def get(url, accept="application/json, text/*", tries=4):
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": accept,
                "Accept-Language": "ru-RU,ru;q=0.9", "Referer": BASE + "/shop/c/smartphones/all/"})
            with urllib.request.urlopen(req, timeout=40) as r:
                return r.read().decode("utf-8", "replace")
        except Exception as e:
            last = e; time.sleep(2 * (i + 1))
    raise last

def flt(q, sort="price-asc", page=0):
    u = BASE + "/yml/product-view/pl/filters?q=%s&text=&sort=%s&qs=&page=%d&ui=d&i=-1&c=750000000" % (urllib.parse.quote(q), sort, page)
    return json.loads(get(u))["data"]

# ---------- 1. список ----------
BATT = ":Smartphones*Battery capacity:более 6000 мАч"
buckets = [":price:150 000 - 199 999 т", ":price:200 000 - 499 999 т"]
raw, seen_ids = [], set()
for b in buckets:
    q = ":category:Smartphones" + BATT + b
    d0 = flt(q, page=0)
    total = d0["total"]
    log("запрос %s: total=%s, на странице %d" % (b, total, len(d0["cards"])))
    pages = (total + 11) // 12
    for p in range(pages):
        d = d0 if p == 0 else flt(q, page=p)
        cards = d["cards"]
        if not cards: break
        for c in cards:
            if c["id"] in seen_ids: continue
            seen_ids.add(c["id"])
            if c["unitPrice"] <= PRICE_MAX: raw.append(c)
        if cards[-1]["unitPrice"] > PRICE_MAX: break
        time.sleep(0.5)
    log("  собрано всего: %d" % len(raw))

raw = [c for c in raw if PRICE_MIN <= c["unitPrice"] <= PRICE_MAX and c["brand"].lower() not in EXCLUDE_BRANDS
       and not re.search(r"iphone|galaxy", c["title"], re.I)]
log("после цены и брендов: %d" % len(raw))

# ---------- 2. дедуп: одинаковая модель/память -> самая дешёвая ----------
fq = flt(":category:Smartphones")
colours = []
for f in fq["filters"]:
    if f["id"].endswith("Colour"):
        colours = [r["id"].split(":")[-1] for r in f["rows"]]
colours = sorted(set(colours + ["серый", "синий", "черный", "чёрный", "зеленый", "зелёный", "фиолетовый", "золотой", "серебристый",
                                 "розовый", "красный", "белый", "голубой", "оранжевый", "бежевый", "бирюзовый", "желтый"]), key=len, reverse=True)
def model_key(title):
    t = htmllib.unescape(title)
    t = re.sub(r"^Смартфон\s+", "", t)
    t = re.sub(r"\s*\+\s*подарок.*$", "", t, flags=re.I)
    t = t.strip().lower().replace("ё", "е")
    for _ in range(3):
        for c in colours:
            cc = c.lower().replace("ё", "е")
            if t.endswith(" " + cc):
                t = t[: -len(cc) - 1].strip()
    return re.sub(r"\s+", " ", t)
best = {}
for c in sorted(raw, key=lambda c: c["unitPrice"]):
    k = model_key(c["title"])
    if k not in best: best[k] = c
cands = list(best.values())
log("после дедупа (самая дешёвая из одинаковых): %d" % len(cands))

# ---------- 3. характеристики карточки ----------
SPEC_RE = re.compile(r'<h4 class="specifications-list__header">(.*?)</h4>|<dl key="[^"]*" class="specifications-list__spec"><dt[^>]*><span class="specifications-list__spec-term-text">(.*?)</span></dt><dd class="specifications-list__spec-definition">(.*?)</dd></dl>', re.S)
def clean(s): return re.sub(r"\s+", " ", htmllib.unescape(re.sub(r"<[^>]+>", "", s))).strip()
def specs_of(page_html):
    out, section = [], ""
    for m in SPEC_RE.finditer(page_html):
        if m.group(1) is not None: section = clean(m.group(1))
        else: out.append((section, clean(m.group(2)), clean(m.group(3))))
    return out
def num(s):
    m = re.search(r"(\d[\d\s]*(?:[.,]\d+)?)", s or "")
    return float(m.group(1).replace(" ", "").replace(",", ".")) if m else None

def fetch(c):
    url = BASE + "/shop" + c["shopLink"]
    try:
        sp = specs_of(get(url, "text/html,application/xhtml+xml"))
    except Exception as e:
        return c, None, str(e)
    time.sleep(0.3)
    return c, sp, None

items, failed = [], 0
with ThreadPoolExecutor(max_workers=4) as ex:
    for i, (c, sp, err) in enumerate(ex.map(fetch, cands)):
        if i % 50 == 0: log("карточки: %d / %d" % (i, len(cands)))
        if not sp: failed += 1; continue
        d = {n: v for _, n, v in sp}
        batt = num(d.get("Емкость аккумулятора"))
        if batt is None or batt < BATT_MIN: continue
        items.append({
            "id": c["id"], "title": htmllib.unescape(c["title"]), "brand": c["brand"], "price": c["unitPrice"],
            "rating": c.get("rating"), "url": BASE + "/shop" + c["shopLink"].split("?")[0],
            "image": (c.get("previewImages") or [{}])[0].get("medium"),
            "battery": int(batt), "processor": d.get("Процессор", ""), "ram": d.get("Размер оперативной памяти", ""),
            "storage": d.get("Размер встроенной памяти", d.get("Встроенная память", "")),
            "specs": [{"section": s, "name": n, "value": v} for s, n, v in sp],
        })
log("карточек не загрузилось: %d; итого после проверки батареи >= %d мАч: %d" % (failed, BATT_MIN, len(items)))
items.sort(key=lambda x: (-x["battery"], x["price"]))
json.dump({"generated": datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"), "count": len(items),
           "stats": {"scanned": len(raw), "unique_models": len(cands)}, "items": items},
          open("data.json", "w"), ensure_ascii=False)
log("готово: data.json")
