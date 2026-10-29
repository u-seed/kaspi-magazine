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
link = "/p/honor-x7e-6-gb-128-gb-goluboi-podarok-177245442/?c=750000000"
html = None
for pre in ("/shop", ""):
    try:
        html = get(BASE + pre + link, "text/html,application/xhtml+xml"); log("OK prefix '%s' %d bytes" % (pre, len(html))); break
    except Exception as e:
        log("prefix '%s' FAIL %s" % (pre, e))
if html:
    open("sample-product.html", "w").write(html)
    for kw in ["Емкость аккумулятора", "Модель процессора", "Процессор", "specification", "ld\\+json", "BACKEND.components"]:
        ms = list(re.finditer(kw, html))
        log("[%s] %d matches" % (kw, len(ms)))
        for m in ms[:2]:
            log("   ..." + html[max(0, m.start()-150):m.start()+400].replace("\n", " "))
# json endpoints for specs
sku = "177245442"
for name, u in [("galleryData", BASE + "/yml/offer-view/offers/" + sku), ("specs", BASE + "/shop/p/x-" + sku + "/?c=750000000&ajax=1")]:
    try:
        b = get(u); log("%s: %d bytes %s" % (name, len(b), b[:400].replace("\n", " ")))
    except Exception as e:
        log("%s FAIL %s" % (name, e))
