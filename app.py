from flask import Flask, render_template, request

app = Flask(__name__, template_folder="templates", static_folder="static")

PRODUCTS = [
    {"id": 1, "name": "Espresso Blend", "origin": "Blend", "roast": "Koyu",
     "process": "Natural", "notes": "Kakao, bitter çikolata", "price": 249, "image": "img/product1.webp"},
    {"id": 2, "name": "Ethiopia Yirgacheffe", "origin": "Ethiopia", "roast": "Orta",
     "process": "Washed", "notes": "Çiçeksi, narenciye", "price": 289, "image": "img/product2.webp"},
    {"id": 3, "name": "Colombia Supremo", "origin": "Colombia", "roast": "Orta",
     "process": "Washed", "notes": "Karamel, fındık", "price": 269, "image": "img/product3.webp"},
    {"id": 4, "name": "Brazil Cerrado", "origin": "Brazil", "roast": "Açık",
     "process": "Natural", "notes": "Sütlü çikolata, badem", "price": 239, "image": "img/product4.webp"},
]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/products")
def products():
    origin = request.args.get("origin", "")
    roast  = request.args.get("roast", "")
    sort   = request.args.get("sort", "popular")

    items = PRODUCTS[:]
    if origin:
        items = [p for p in items if p["origin"].lower() == origin.lower()]
    if roast:
        items = [p for p in items if p["roast"].lower() == roast.lower()]

    if sort == "price_asc":
        items = sorted(items, key=lambda p: p["price"])
    elif sort == "price_desc":
        items = sorted(items, key=lambda p: p["price"], reverse=True)
    elif sort == "alpha":
        items = sorted(items, key=lambda p: p["name"])

    origins = sorted({p["origin"] for p in PRODUCTS})
    roasts  = sorted({p["roast"]  for p in PRODUCTS})

    return render_template(
        "products.html",
        products=items,
        origins=origins, roasts=roasts,
        selected_origin=origin, selected_roast=roast, selected_sort=sort
    )

@app.route("/product/<int:pid>")
def product_detail(pid):
    p = next((x for x in PRODUCTS if x["id"] == pid), None)
    if not p:
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
