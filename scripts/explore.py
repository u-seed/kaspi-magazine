import json, re, urllib.request, urllib.parse, traceback
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
BASE = "https://kaspi.kz"
out = []
def log(s):
    out.append(s); open("explore-result.txt", "w").write("\n".join(out))
def get(url, accept="application/json, text/*"):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": accept, "Accept-Language": "ru-RU,ru;q=0.9", "Referer": BASE + "/shop/c/smartphones/all/"})
    with urllib.request.urlopen(req, timeout=40) as r:
        return r.read().decode("utf-8", "replace")
def lst(page, q, sort="relevance"):
    u = BASE + "/yml/product-view/pl/results?page=%d&q=%s&text=&sort=%s&qs=&ui=d&i=-1&c=750000000" % (page, urllib.parse.quote(q), sort)
    return json.loads(get(u))
q0 = ":category:Smartphones:availableInZones:Magnum_ZONE1"
tests = [
  ("price range", q0 + ":price:150000-350000", "relevance"),
  ("price range 2", q0 + ":price:150000-350000", "price"),
  ("manufacturer Honor", q0 + ":manufacturer:Honor", "relevance"),
  ("manufacturer Xiaomi", q0 + ":manufacturer:Xiaomi", "relevance"),
  ("manufacturer+price", q0 + ":manufacturer:Honor:price:150000-350000", "relevance"),
]
first_non_apple = None
for name, q, sort in tests:
    try:
        d = lst(0, q, sort)
        items = d["data"]
        log("%s: %d items, brands/prices %s" % (name, len(items), [(x["brand"], x["unitPrice"]) for x in items][:12]))
        for x in items:
            if x["brand"] not in ("Apple", "Samsung") and not first_non_apple:
                first_non_apple = x
    except Exception as e:
        log("%s FAIL %s" % (name, e))
# pages: how far does it go
try:
    d = lst(0, q0 + ":manufacturer:Honor")
    for p in (5, 20, 60):
        dd = lst(p, q0 + ":manufacturer:Honor")
        log("honor page %d -> %d items" % (p, len(dd["data"])))
except Exception as e:
    log("paging FAIL %s" % e)
if first_non_apple:
    url = BASE + first_non_apple["shopLink"]
    log("detail url: " + url)
    try:
        html = get(url, "text/html,application/xhtml+xml")
        open("sample-product.html", "w").write(html)
        log("product html %d bytes" % len(html))
        for kw in ["Емкость аккумулятора", "Процессор", "ld\\+json", "BACKEND"]:
            ms = list(re.finditer(kw, html))
            log("[%s] matches: %d" % (kw, len(ms)))
            for m in ms[:2]:
                log("   ..." + html[max(0, m.start()-100):m.start()+300].replace("\n", " "))
    except Exception as e:
        log("detail FAIL %s" % e)
else:
    log("no non-apple item found")
