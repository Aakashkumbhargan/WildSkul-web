from __future__ import annotations
# from curses import window
from flask import Flask, flash, json, redirect, render_template, jsonify, request, session, url_for
from collections import defaultdict
import os, json, requests
from flask import current_app as app
from paytmchecksum import PaytmChecksum


app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-change-me")  # set a strong key in prod

# ---- Demo product catalog (could be replaced with DB later) ----
PRODUCTS = [
    {
        "id": "voyager-28",
        "title": "Voyager 28” Hardcase Spinner",
        "category": "Luggage & Carrying Bags",
        "price": 7999,
        "mrp": 10999,
        "rating": 4.6,
        "date": "2026-01-15",
        "popularity": 98,
        "image": "assets/Bagpack_1_1.jpg",
        "desc": "Lightweight polycarbonate shell, TSA lock, 360° wheels."
    },
    {
        "id": "transit-pro-duffel",
        "title": "Transit Pro Weekender Duffel",
        "category": "Luggage & Carrying Bags",
        "price": 3499,
        "mrp": 4299,
        "rating": 4.3,
        "date": "2025-12-28",
        "popularity": 86,
        "image": "assets/La_handbag_2.jpg",
        "desc": "Water-resistant canvas, shoe compartment, trolley sleeve."
    },
    {
        "id": "heritage-trunk",
        "title": "Heritage Steel Travel Trunk",
        "category": "Trunks",
        "price": 9499,
        "mrp": 12499,
        "rating": 4.5,
        "date": "2025-11-10",
        "popularity": 74,
        "image": "assets/La_belt_4.jpg",
        "desc": "Powder-coated finish, reinforced corners, lockable latches."
    },
    {
        "id": "muse-crossbody",
        "title": "Muse Leather Crossbody Purse",
        "category": "Purses",
        "price": 2899,
        "mrp": 3499,
        "rating": 4.2,
        "date": "2026-01-02",
        "popularity": 77,
        "image": "assets/La_purse_2.jpg",
        "desc": "Pebbled leather, adjustable strap, magnetic flap closure."
    },
    {
        "id": "gridtech-15-backpack",
        "title": "GridTech 15.6” Laptop Backpack",
        "category": "Laptop Bags",
        "price": 2499,
        "mrp": 3199,
        "rating": 4.4,
        "date": "2026-01-20",
        "popularity": 90,
        "image": "assets/La_laptop_bag_1.jpg",
        "desc": "Padded sleeve, USB passthrough, anti-theft pocket."
    },
    {
        "id": "metro-messenger",
        "title": "Metro Messenger Bag",
        "category": "Laptop Bags",
        "price": 2199,
        "mrp": 2799,
        "rating": 4.1,
        "date": "2025-12-05",
        "popularity": 65,
        "image": "assets/La_laptop_bag_3.jpg",
        "desc": "Slim profile, quick-access front panel, water-repellent."
    },
    {
        "id": "rfid-bifold",
        "title": "RFID Bifold Wallet",
        "category": "Wallets",
        "price": 1299,
        "mrp": 1599,
        "rating": 4.0,
        "date": "2025-10-26",
        "popularity": 61,
        "image": "assets/La_wallet_3.jpg",
        "desc": "RFID protection, 8 card slots, currency divider."
    },
    {
        "id": "slim-card-holder",
        "title": "Slim Card Holder",
        "category": "Wallets",
        "price": 699,
        "mrp": 899,
        "rating": 4.2,
        "date": "2025-09-12",
        "popularity": 59,
        "image": "assets/La_wallet_5.jpg",
        "desc": "Minimal profile, quick-pull slot, premium stitching."
    },
]

CATEGORIES = sorted({p["category"] for p in PRODUCTS})

def get_product(pid: str) -> dict | None:
    return next((p for p in PRODUCTS if p["id"] == pid), None)

def init_cart():
    if "cart" not in session:
        session["cart"] = {}  # {product_id: qty}
    return session["cart"]

def cart_items_detail():
    """Return detailed cart items + totals from session cart."""
    cart = session.get("cart", {})
    items = []
    subtotal = 0
    count = 0
    for pid, qty in cart.items():
        prod = get_product(pid)
        if not prod: 
            continue
        line_total = prod["price"] * qty
        subtotal += line_total
        count += qty
        items.append({
            "id": pid,
            "title": prod["title"],
            "category": prod["category"],
            "price": prod["price"],
            "qty": qty,
            "image": url_for("static", filename=prod["image"]),
            "line_total": line_total
        })
    return {"items": items, "subtotal": subtotal, "count": count}

# ----------------- Pages -----------------
@app.route("/")
def home():
    # Pre-resolve image URLs for server-rendered page
    products = []
    for p in PRODUCTS:
        p2 = dict(p)
        p2["image_url"] = url_for("static", filename=p["image"])
        products.append(p2)
    return render_template("index.html", products=products, categories=CATEGORIES)

@app.route("/checkout")
def checkout():
    pid = request.args.get("id")
    # If pid is present, you can pre-select that item or show cart contents.
    # detail = cart_detail()  # your existing function
    return render_template("checkout.html", selected_id=pid)


 

# ----------------- APIs -----------------
@app.get("/api/categories")
def api_categories():
    return jsonify(CATEGORIES)

@app.get("/api/products")
def api_products():
    # Optional filters via query params
    q = (request.args.get("q") or "").lower()
    category = request.args.get("category")
    sort = request.args.get("sort", "popular")
    min_price = request.args.get("minPrice", type=int)
    max_price = request.args.get("maxPrice", type=int)
    rating_gte = request.args.get("ratingGte", type=float)

    data = PRODUCTS[:]
    if q:
        data = [p for p in data if q in p["title"].lower() or q in p["category"].lower()]
    if category and category != "All":
        data = [p for p in data if p["category"] == category]
    if min_price is not None:
        data = [p for p in data if p["price"] >= min_price]
    if max_price is not None:
        data = [p for p in data if p["price"] <= max_price]
    if rating_gte:
        data = [p for p in data if p["rating"] >= rating_gte]

    if sort == "popular":
        data.sort(key=lambda p: (p.get("popularity", 0), -p["price"]), reverse=True)
    elif sort == "price_asc":
        data.sort(key=lambda p: p["price"])
    elif sort == "price_desc":
        data.sort(key=lambda p: p["price"], reverse=True)
    elif sort == "rating":
        data.sort(key=lambda p: p["rating"], reverse=True)
    elif sort == "newest":
        data.sort(key=lambda p: p["date"], reverse=True)

    # Resolve images to /static path for API users
    for p in data:
        p["image_url"] = url_for("static", filename=p["image"])
    return jsonify(data)

@app.get("/api/cart")
def api_cart_get():
    return jsonify(cart_items_detail())

@app.post("/api/cart/add")
def api_cart_add():
    data = request.get_json(force=True)
    pid = data.get("id")
    qty = int(data.get("qty", 1))
    if qty < 1:
        qty = 1
    prod = get_product(pid)
    if not prod:
        return jsonify({"error": "Invalid product id"}), 404
    cart = init_cart()
    cart[pid] = cart.get(pid, 0) + qty
    session["cart"] = cart
    return jsonify(cart_items_detail())

@app.post("/api/cart/update")
def api_cart_update():
    data = request.get_json(force=True)
    pid = data.get("id")
    qty = int(data.get("qty", 1))
    prod = get_product(pid)
    if not prod:
        return jsonify({"error": "Invalid product id"}), 404
    cart = init_cart()
    if qty <= 0:
        cart.pop(pid, None)
    else:
        cart[pid] = qty
    session["cart"] = cart
    return jsonify(cart_items_detail())

@app.delete("/api/cart/remove/<pid>")
def api_cart_remove(pid):
    cart = init_cart()
    cart.pop(pid, None)
    session["cart"] = cart
    return jsonify(cart_items_detail())

@app.delete("/api/cart/clear")
def api_cart_clear():
    session["cart"] = {}
    return jsonify(cart_items_detail())

if __name__ == "__main__":
    # Dev-friendly
    app.run(debug=True)




# Payment checkout

PAYTM_MID = os.getenv("PAYTM_MID")
PAYTM_KEY = os.getenv("PAYTM_MERCHANT_KEY")
PAYTM_WEBSITE = os.getenv("PAYTM_WEBSITE", "WEBSTAGING")
PAYTM_HOST = os.getenv("PAYTM_HOST", "https://securegw-stage.paytm.in")  # prod host differs

def cart_detail():
    cart = session.get("cart", {})
    items, subtotal = [], 0
    for pid, qty in cart.items():
        prod = get_product(pid)
        if not prod: continue
        q = max(int(qty), 1)
        line = prod["price"] * 100 * q  # paise
        items.append({"id": pid, "title": prod["title"], "qty": q, "unit_paise": prod["price"]*100, "line_paise": line})
        subtotal += line
    shipping = 0 if subtotal >= 99900 else 9900
    return {"items": items, "subtotal": subtotal, "shipping": shipping, "total": subtotal+shipping}


# 2) Initiate transaction route → returns txnToken

@app.post("/paytm/initiate")
def paytm_initiate():
    data = request.get_json(force=True)
    order_id = data["orderId"]
    amount = str(data["amount"])    # e.g., "1499.00"
    cust_id = data.get("custId", "CUST001")

    body = {
        "requestType": "Payment",
        "mid": PAYTM_MID,
        "websiteName": PAYTM_WEBSITE,
        "orderId": order_id,
        "callbackUrl": url_for("paytm_callback", _external=True),
        "txnAmount": {"value": amount, "currency": "INR"},
        "userInfo": {"custId": cust_id}
    }
    signature = PaytmChecksum.generateSignature(json.dumps(body), PAYTM_KEY)
    payload = {"body": body, "head": {"signature": signature}}

    url = f"{PAYTM_HOST}/theia/api/v1/initiateTransaction?mid={PAYTM_MID}&orderId={order_id}"
    resp = requests.post(url, json=payload, timeout=20)
    js = resp.json()

    # Expect: {"body":{"txnToken":"..."}, "head":{...}}
    if resp.ok and js.get("body", {}).get("txnToken"):
        return jsonify({"txnToken": js["body"]["txnToken"]})
    return jsonify({"error": js}), 400



@app.route("/paytm/callback", methods=["POST"])
def paytm_callback():
    # Paytm posts fields like: ORDERID, TXNAMOUNT, STATUS, CHECKSUMHASH, etc.
    form = request.form.to_dict()
    checksum = form.pop("CHECKSUMHASH", "")
    valid = PaytmChecksum.verifySignature(form, PAYTM_KEY, checksum)

    order_id = form.get("ORDERID")
    if not valid or not order_id:
        flash("Payment validation failed.")
        return redirect(url_for("checkout"))

    # Recommended: call Order Status API (server-to-server) before confirming
    status_url = f"{PAYTM_HOST}/v3/order/status"
    body = {"mid": PAYTM_MID, "orderId": order_id}
    head = {"signature": PaytmChecksum.generateSignature(json.dumps(body), PAYTM_KEY)}
    status_resp = requests.post(status_url, json={"body": body, "head": head}, timeout=20).json()
    # status_resp.body.resultInfo.resultStatus ∈ { "SUCCESS", "FAILURE", "PENDING" }
    # (naming can vary across doc pages; always check resultInfo) [3](https://www.paytmpayments.com/docs/jscheckout-verify-payment/)

    result = (status_resp.get("body", {}).get("resultInfo") or {})
    if result.get("resultStatus") in ("TXN_SUCCESS", "SUCCESS"):
        # mark order as paid in DB, clear cart, redirect success
        session["cart"] = {}
        return redirect(url_for("order_success", order_no=order_id))
    elif result.get("resultStatus") in ("PENDING",):
        flash("Payment pending. We’ll notify once confirmed.")
        return redirect(url_for("checkout"))
    else:
        flash("Payment failed or cancelled.")
        return redirect(url_for("checkout"))