import json, urllib.request, urllib.parse
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
BASE = "https://kaspi.kz"
out = []
def log(s):
    out.append(s); open("explore-result.txt", "w").write("\n".join(out))
def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json, text/*", "Accept-Language": "ru-RU,ru;q=0.9", "Referer": BASE + "/shop/c/smartphones/all/"})
    with urllib.request.urlopen(req, timeout=40) as r:
        return r.read().decode("utf-8", "replace")
tail = "&ui=d&i=-1&c=750000000"
d = json.loads(get(BASE + "/yml/product-view/pl/filters?q=%3Acategory%3ASmartphones&text=&sort=relevance&qs=" + tail))["data"]
log("data keys: %s" % list(d.keys()))
for k, v in d.items():
    if k != "cards":
        log("%s: %s" % (k, json.dumps(v, ensure_ascii=False)[:1500]))
log("cards: %d" % len(d["cards"]))
