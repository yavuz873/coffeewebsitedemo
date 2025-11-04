from flask import Flask, render_template, request, redirect, url_for, flash
import csv, os

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = "dev-key"  # flash() için basit key
def load_products():
    csv_path = os.path.join("data", "products.csv")
    products = []
    with open(csv_path, newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            products.append({
                "title": row["title"],
                "price": float(row["price"]),
                "image_url": row["image_url"],
                "notes": row["notes"].split("|"),
                "slug": row["slug"],
                "subtitle": row["subtitle"],
            })
    return products

PRODUCTS = load_products()
# ---- Dosya yolları
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)
PRODUCTS_CSV = os.path.join(DATA_DIR, "products.csv")


# ---- Yardımcılar
def _to_int(val, default=0):
    try:
        return int(str(val).strip())
    except Exception:
        return default


def load_products():
    """
    products.csv -> [{id,int, name,str, origin,str, roast,str, process,str,
                      notes,list[str], price,int, image,str, subtitle,str}, ...]
    Not: notes alanı CSV'de 'Kakao|Bitter' şeklinde tutulur, burada listeye çevrilir.
    """
    items = []
    if not os.path.exists(PRODUCTS_CSV):
        return items

    with open(PRODUCTS_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            item = {
                "id": _to_int(row.get("id")),
                "name": (row.get("name") or "").strip(),
                "origin": (row.get("origin") or "").strip(),
                "roast": (row.get("roast") or "").strip(),
                "process": (row.get("process") or "").strip(),
                "notes": [n.strip() for n in (row.get("notes") or "").split("|") if n.strip()],
                "price": _to_int(row.get("price")),
                # Görselleri /static/img/... altında tutuyoruz
                "image": (row.get("image") or "").strip(),     # örn: /static/img/product1.webp
                "subtitle": (row.get("subtitle") or "").strip()
            }

            # ---- Ürünleri CSV'den yükle ----
            def load_products():
                products = []
                with open(PRODUCTS_CSV, newline='', encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        products.append({
                            "title": row["title"],
                            "price": float(row["price"]),
                            "image_url": row["image_url"],
                            "notes": row["notes"].split("|"),
                            "slug": row["slug"],
                            "subtitle": row["subtitle"]
                        })
                return products

            PRODUCTS = load_products()

            # id yoksa güvenli bir id üret (satır sayısı gibi) — prod’da DB gerekir
            if not item["id"]:
                item["id"] = len(items) + 1
            items.append(item)
    return items


def unique_sorted(values):
    return sorted(v for v in set(values) if v)


def build_filter_sets(items):
    """Dropdown’lar için benzersiz origin/roast listeleri."""
    origins = unique_sorted([x["origin"] for x in items])
    roasts = unique_sorted([x["roast"] for x in items])
    return origins, roasts


# ---- Rotalar
@app.route("/")
def index():
    """
    Ana sayfa: vitrin için ilk 3 ürünü gösteriyoruz.
    (Not: İstersen burada 'featured' kolonu ekleyip ona göre filtreleyebilirsin.)
    """
    products = load_products()
    featured = products[:3]
    return render_template("index.html", products=featured)


@app.route("/products")
def products():
    """
    Ürün liste sayfası + filtreleme + sıralama
    /products?origin=Ethiopia&roast=Orta&sort=price_desc
    """
    items = load_products()
    origins, roasts = build_filter_sets(items)

    origin = (request.args.get("origin") or "").strip()
    roast = (request.args.get("roast") or "").strip()
    sort = (request.args.get("sort") or "").strip()  # price_asc | price_desc | name_asc

    # Filtreler
    if origin:
        items = [x for x in items if x["origin"].lower() == origin.lower()]
    if roast:
        items = [x for x in items if x["roast"].lower() == roast.lower()]

    # Sıralama
    if sort == "price_asc":
        items = sorted(items, key=lambda x: x["price"])
    elif sort == "price_desc":
        items = sorted(items, key=lambda x: x["price"], reverse=True)
    elif sort == "name_asc":
        items = sorted(items, key=lambda x: x["name"].lower())

    return render_template(
        "products.html",
        products=items,
        origins=origins, roasts=roasts,
        selected_origin=origin, selected_roast=roast, selected_sort=sort
    )


@app.route("/product/<int:pid>")
def product_detail(pid):
    """
    Önceden PRODUCTS listesinde arıyorduk; şimdi CSV'den oku.
    """
    items = load_products()
    p = next((x for x in items if x["id"] == pid), None)
    if not p:
        # sende "tesekkurler.html" varsa orayı kullanıyordun; 404 daha doğru.
        return render_template("tesekkurler.html", msg="Ürün bulunamadı"), 404
    return render_template("product_detail.html", p=p)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/iletisim")
def iletisim():
    return render_template("iletisim.html")


if __name__ == "__main__":
    app.run(debug=True)
