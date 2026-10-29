import json, urllib.request, urllib.parse
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
BASE = "https://kaspi.kz"
out = []
def log(s):
    out.append(s); open("test-result.txt", "w").write("\n".join(out))
def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json, text/*", "Accept-Language": "ru-RU,ru;q=0.9", "Referer": BASE + "/shop/c/smartphones/all/"})
    with urllib.request.urlopen(req, timeout=40) as r:
        return r.read().decode("utf-8", "replace")
tail = "&ui=d&i=-1&c=750000000"
q = ":category:Smartphones:Smartphones*Battery capacity:более 6000 мАч:price:200 000 - 499 999 т:manufacturerName:HONOR"
for ep in ("results", "filters"):
    for p in (0, 1, 2, 3, 10, 40):
        u = BASE + "/yml/product-view/pl/%s?page=%d&q=%s&text=&sort=price-asc&qs=" % (ep, p, urllib.parse.quote(q)) + tail
        try:
            d = json.loads(get(u))
            d = d["data"]; cards = d["cards"] if isinstance(d, dict) else d
            log("%s page %d: %d items, prices %s" % (ep, p, len(cards), [c["unitPrice"] for c in cards][:12]))
        except Exception as e:
            log("%s page %d FAIL %s" % (ep, p, e))
