import json, re, sys, urllib.request, urllib.parse
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
BASE = "https://kaspi.kz"
def get(url, accept="application/json, text/*", ref=BASE + "/shop/c/smartphones/all/"):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": accept, "Accept-Language": "ru-RU,ru;q=0.9", "Referer": ref})
    with urllib.request.urlopen(req, timeout=40) as r:
        return r.status, r.read().decode("utf-8", "replace")
def lst(page, q):
    u = BASE + "/yml/product-view/pl/results?page=%d&q=%s&text=&sort=relevance&qs=&ui=d&i=-1&c=750000000" % (page, urllib.parse.quote(q))
    return get(u)
out = []
q0 = ":category:Smartphones:availableInZones:Magnum_ZONE1"
st, body = lst(0, q0)
d = json.loads(body)
out.append("top keys: %s" % list(d.keys()))
for k, v in d.items():
    if k != "data":
        out.append("%s = %s" % (k, json.dumps(v, ensure_ascii=False)[:300]))
out.append("items on page: %d" % len(d["data"]))
out.append("item keys: %s" % list(d["data"][0].keys()))
out.append("first item: %s" % json.dumps(d["data"][0], ensure_ascii=False)[:900])
json.dump(d, open("sample-list.json", "w"), ensure_ascii=False)
# price filter attempts
for q in [q0 + ":price:150000-350000", q0 + ":price:150000-350000:manufacturer:Honor"]:
    try:
        st, b = lst(0, q); dd = json.loads(b)
        prices = [x["unitPrice"] for x in dd["data"]]
        out.append("q=%s -> %d items, prices %s" % (q[-60:], len(dd["data"]), prices[:12]))
        out.append("  other keys: %s" % {k: (v if not isinstance(v, (list, dict)) else '...') for k, v in dd.items() if k != 'data'})
    except Exception as e:
        out.append("q=%s FAIL %s" % (q[-60:], e))
# a non-apple item page
item = next(x for x in d["data"] if x.get("brand") not in ("Apple", "Samsung"))
url = BASE + item["shopLink"]
out.append("detail url: " + url)
st, html = get(url, accept="text/html,application/xhtml+xml")
open("sample-product.html", "w").write(html)
out.append("product html %d bytes" % len(html))
for kw in ["Емкость аккумулятора", "аккумулятор", "Процессор", "specification", "ld+json"]:
    for m in list(re.finditer(kw, html))[:2]:
        out.append("[%s] ...%s..." % (kw, html[max(0, m.start()-120):m.start()+260].replace("\n", " ")))
open("explore-result.txt", "w").write("\n".join(out))
