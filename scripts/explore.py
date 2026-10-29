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
def tryget(name, url):
    try:
        b = get(url)
        log("%s: %d bytes: %s" % (name, len(b), b[:700].replace("\n", " ")))
        return b
    except Exception as e:
        log("%s FAIL %s" % (name, e))
tail = "&ui=d&i=-1&c=750000000"
# does text search work at all?
b = tryget("text=honor", BASE + "/yml/product-view/pl/results?page=0&q=%3Acategory%3ASmartphones&text=honor&sort=relevance&qs=" + tail)
if b:
    d = json.loads(b); log("  text=honor brands: %s" % [(x["brand"], x["unitPrice"]) for x in d["data"]])
# facets
tryget("filters", BASE + "/yml/product-view/pl/filters?q=%3Acategory%3ASmartphones&text=&sort=relevance&qs=" + tail)
tryget("filters2", BASE + "/yml/product-view/pl/filters?text=&sort=true&qs=&q=%3Acategory%3ASmartphones" + tail)
# category page with q in url: look for facet names in html
html = get(BASE + "/shop/c/smartphones/all/?q=%3Acategory%3ASmartphones", "text/html")
open("sample-category.html", "w").write(html)
log("category html %d bytes" % len(html))
for kw in ["manufacturer", "Manufacturer", "price", "facets", "filters"]:
    ms = list(re.finditer(kw, html))
    log("[%s] %d matches" % (kw, len(ms)))
    for m in ms[:2]:
        log("   ..." + html[max(0, m.start()-100):m.start()+250].replace("\n", " "))
