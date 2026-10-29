import json, re, urllib.request, urllib.parse
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
BASE = "https://kaspi.kz"
out = []
def log(s):
    out.append(s); open("explore-result.txt", "w").write("\n".join(out))
def get(url, accept="application/json, text/*"):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": accept, "Accept-Language": "ru-RU,ru;q=0.9", "Referer": BASE + "/shop/c/smartphones/all/"})
    with urllib.request.urlopen(req, timeout=40) as r:
        return r.read().decode("utf-8", "replace")
tail = "&ui=d&i=-1&c=750000000"
def flt(q, sort="relevance", page=0):
    return json.loads(get(BASE + "/yml/product-view/pl/filters?q=%s&text=&sort=%s&qs=&page=%d" % (urllib.parse.quote(q), sort, page) + tail))["data"]
d = flt(":category:Smartphones")
for f in d["filters"]:
    rows = f.get("rows") or []
    log("FILTER %s | %s | type=%s | rows=%d | e.g. %s" % (f["id"], f["title"], f["type"], len(rows), [r["id"] for r in rows[:3]]))
    if re.search("аккум|батар|battery|процессор|Производитель|brand", f["title"] + f["id"], re.I):
        log("   ALL ROWS: %s" % [(r["id"], r["count"]) for r in rows][:60])
# test price bucket + sort
q = ":category:Smartphones:price:150 000 - 199 999 т"
for sort in ("price-asc",):
    for pg in (0, 1):
        dd = flt(q, sort, pg)
        log("q=%s sort=%s page=%d total=%s prices=%s" % (q, sort, pg, dd["total"], [(c["brand"], c["unitPrice"]) for c in dd["cards"]]))
# detail page of first card
c = dd["cards"][0]
url = BASE + c["shopLink"]
log("detail: " + url + " | " + c["title"])
html = get(url, "text/html,application/xhtml+xml")
open("sample-product.html", "w").write(html)
log("product html %d bytes" % len(html))
for kw in ["Емкость аккумулятора", "Модель процессора", "Процессор", "specification"]:
    ms = list(re.finditer(kw, html))
    log("[%s] %d matches" % (kw, len(ms)))
    for m in ms[:2]:
        log("   ..." + html[max(0, m.start()-150):m.start()+350].replace("\n", " "))
