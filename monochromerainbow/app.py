from itertools import product
from flask import Flask, render_template, request, redirect, url_for, session


app = Flask(__name__)
app.secret_key = "supersecretkey"
products = [
        {"id":1,"name": "Akito Shinonome (Keychain)",   "type": "keychain", "price": 2.00,  "img": "assets/akito.jpg","reviews": []},
        {"id":2,"name": "KAITO (Keychain)",    "type": "keychain", "price": 2.00,  "img": "assets/kaito.png","reviews": []},
        {"id":3,"name": "Neuvilette (Keychain)",  "type": "keychain", "price": 2.00,  "img": "assets/neuv.png","reviews": []},
        {"id":4,"name": "Wind~Portrait (Full Art Piece)",    "type": "art",      "price": 10.50, "img": "assets/art.jpg","reviews": []},
        {"id":5,"name": "Bone~Girl (Full Art Piece)","type": "art",      "price": 12.50, "img": "assets/bonegirl.png","reviews": []},
        {"id":6,"name": "Illoyd (Chibi Art)",  "type": "art",      "price": 6.50,  "img": "assets/illoyd.png","reviews": []},
        {"id":7,"name": "Gyaru~Girl (Full Art Piece)", "type":"art", "price":9.50, "img": "assets/silly.png","reviews": []},  
        {"id":8,"name": "Lolita Necklace",  "type": "jewelry",  "price": 4.00,  "img": "assets/lolita.png","reviews": []},
        {"id":9,"name": "Punk Necklace",    "type": "jewelry",  "price": 4.00,  "img": "assets/metal.png","reviews": []},
        {"id":10,"name": "Kandi",   "type": "jewelry",  "price": 4.50,  "img": "assets/kandi.jpg","reviews": []},
         
    ]


# In-memory storage
users = {}  # {username: {"email": email, "password": password, "cart": [], "wishlist": []}}


@app.route("/")
def index():
    return render_template("keychan.html")




@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")


        if username in users and users[username]["password"] == password:
            session["user"] = username
            return redirect(url_for("products_page"))
        else:
            return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")




@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm = request.form.get("confirm")


        if password != confirm:
            return render_template("register.html", error="Passwords do not match!")


        if username in users:
            return render_template("register.html", error="Username already exists!")


        users[username] = {"email": email, "password": password, "cart": [], "wishlist": []}
        return redirect(url_for("login"))


    return render_template("register.html")








@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("index"))
def _require_login():
    username = session.get("user")
    if not username:
        return None
    return username


def _counts(username):
    cart_count = len(users[username]["cart"]) if username else 0
    wishlist_count = len(users[username]["wishlist"]) if username else 0
    return cart_count, wishlist_count




@app.route("/products")
def products_page():
    username = session.get("user")
    cart_count, wishlist_count = (0, 0)
    if username and username in users:
        cart_count, wishlist_count = _counts(username)


    
    return render_template(
        "shop.html",
        products=products,
        cart_count=cart_count,
        wishlist_count=wishlist_count
    )




@app.route("/cart")
def view_cart():
    username = _require_login()
    if not username:
        return redirect(url_for("login"))


    cart = users[username]["cart"]
    # multiply by quantity (default 1 if missing)
    total = sum(item["price"] * int(item.get("quantity", 1)) for item in cart)
    cart_count, wishlist_count = _counts(username)
    return render_template(
        "cart.html",
        cart=cart,
        total=total,
        cart_count=cart_count,
        wishlist_count=wishlist_count
    )




@app.route("/wishlist")
def view_wishlist():
    username = _require_login()
    if not username:
        return redirect(url_for("login"))


    wishlist = users[username]["wishlist"]
    cart_count, wishlist_count = _counts(username)
    return render_template(
        "wishlist.html",
        wishlist=wishlist,
        cart_count=cart_count,
        wishlist_count=wishlist_count
    )




@app.route("/add_to_cart", methods=["POST"])
def add_to_cart():
    username = _require_login()
    if not username:
        return redirect(url_for("login"))


    name = request.form.get("name")
    price = float(request.form.get("price", 0))
    img = request.form.get("img")
    quantity = int(request.form.get("quantity", 1))


    cart = users[username]["cart"]


    # If the item is already in cart, bump quantity instead of duplicating
    for item in cart:
        if item["name"] == name:
            item["quantity"] = int(item.get("quantity", 1)) + quantity
            break
    else:
        cart.append({"name": name, "price": price, "img": img, "quantity": quantity})


    return redirect(url_for("products_page"))




@app.route("/clear_cart")
def clear_cart():
    username = _require_login()
    if not username:
        return redirect(url_for("login"))
    users[username]["cart"] = []
    return redirect(url_for("view_cart"))




@app.route("/add_to_wishlist", methods=["POST"])
def add_to_wishlist():
    username = _require_login()
    if not username:
        return redirect(url_for("login"))


    name = request.form.get("name")
    img = request.form.get("img")
    price = float(request.form.get("price", 0))  # now we store price too


    wishlist = users[username]["wishlist"]
    if name not in [item["name"] for item in wishlist]:
        wishlist.append({"name": name, "img": img, "price": price})
    return redirect(url_for("products_page"))




@app.route("/remove_from_cart/<name>")
def remove_from_cart(name):
    username = _require_login()
    if not username:
        return redirect(url_for("login"))
    cart = users[username]["cart"]
    users[username]["cart"] = [item for item in cart if item["name"] != name]
    return redirect(url_for("view_cart"))




@app.route("/remove_from_wishlist/<name>")
def remove_from_wishlist(name):
    username = _require_login()
    if not username:
        return redirect(url_for("login"))
    wishlist = users[username]["wishlist"]
    users[username]["wishlist"] = [item for item in wishlist if item["name"] != name]
    return redirect(url_for("view_wishlist"))




@app.route("/clear_wishlist")
def clear_wishlist():
    username = _require_login()
    if not username:
        return redirect(url_for("login"))
    users[username]["wishlist"] = []
    return redirect(url_for("view_wishlist"))




@app.route("/update_quantity", methods=["POST"])
def update_quantity():
    username = _require_login()
    if not username:
        return redirect(url_for("login"))


    name = request.form["name"]
    action = request.form["action"]


    cart = users[username]["cart"]
    for item in cart:
        if item["name"] == name:
            q = int(item.get("quantity", 1))
            if action == "increase":
                q += 1
            elif action == "decrease":
                q = max(1, q - 1)  # don't go below 1
            item["quantity"] = q
            break


    return redirect(url_for("view_cart"))





@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    username = _require_login()
    if not username:
        return redirect(url_for("login"))

    if request.method == "POST":
        # Collect form data
        first = request.form.get("Firstname")
        last = request.form.get("Lastname")
        address = request.form.get("Address")
        zipcode = request.form.get("ZipCode")
        city = request.form.get("City")
        state = request.form.get("State")

        # You could process / save order here
        order = {
            "user": username,
            "first": first,
            "last": last,
            "address": address,
            "zipcode": zipcode,
            "city": city,
            "state": state,
            "cart": users[username]["cart"].copy(),
            "total": sum(item["price"] * int(item.get("quantity", 1)) for item in users[username]["cart"])
        }

        # Clear cart after checkout (optional)
        users[username]["cart"] = []

        # Render confirmation page
        return render_template("order_confirm.html", order=order)

    # If GET request -> show checkout page
    return render_template("checkout.html")


@app.route("/thankyou")
def thank_you():
    return render_template("thankyou.html")

@app.route("/add_review/<int:pid>", methods=["POST"])
def add_review(pid):
    name = request.form["name"]
    text = request.form["text"]
    for p in products:
        if p["id"] == pid:
            p["reviews"].append({"name": name, "text": text})
            break
    return redirect(url_for("products_page"))



if __name__ == "__main__":
    app.run(debug=True)








# @app.route("/cart")
# def view_cart():
#     username = session.get("user")
#     if not username:
#         return redirect(url_for("login"))
#     user_cart = users[username]["cart"]
#     total = sum(item["price"] for item in user_cart)
#     return render_template("cart.html", cart=user_cart, total=total)




# @app.route("/wishlist")
# def view_wishlist():
#     username = session.get("user")
#     if not username:
#         return redirect(url_for("login"))
#     user_wishlist = users[username]["wishlist"]
#     return render_template("wishlist.html", wishlist=user_wishlist)




# @app.route("/add_to_cart", methods=["POST"])
# def add_to_cart():
#     username = session.get("user")
#     if not username:
#         return redirect(url_for("login"))


#     name = request.form.get("name")
#     price = float(request.form.get("price", 0))
#     img = request.form.get("img")
#     quantity=request.form.get("quantity",0)


#     users[username]["cart"].append({"name": name, "price": price, "img": img, "quantity":quantity})
#     return redirect(url_for("products_page"))


# @app.route("/clear_cart")
# def clear_cart():
#     username = session.get("user")
#     if not username:
#         return redirect(url_for("login"))
#     users[username]["cart"] = []
#     return redirect(url_for("view_cart"))






# @app.route("/add_to_wishlist", methods=["POST"])
# def add_to_wishlist():
#     username = session.get("user")
#     if not username:
#         return redirect(url_for("login"))


#     name = request.form.get("name")
#     img = request.form.get("img")


#     wishlist = users[username]["wishlist"]
#     if name not in [item["name"] for item in wishlist]:
#         wishlist.append({"name": name, "img": img})
#     return redirect(url_for("products_page"))




# @app.route("/remove_from_cart/<name>")
# def remove_from_cart(name):
#     username = session.get("user")
#     if not username:
#         return redirect(url_for("login"))
#     cart = users[username]["cart"]
#     users[username]["cart"] = [item for item in cart if item["name"] != name]
#     return redirect(url_for("view_cart"))




# @app.route("/remove_from_wishlist/<name>")
# def remove_from_wishlist(name):
#     username = session.get("user")
#     if not username:
#         return redirect(url_for("login"))
#     wishlist = users[username]["wishlist"]
#     users[username]["wishlist"] = [item for item in wishlist if item["name"] != name]
#     return redirect(url_for("view_wishlist"))


# @app.route("/clear_wishlist")
# def clear_wishlist():
#     username = session.get("user")
#     if not username:
#         return redirect(url_for("login"))
#     users[username]["wishlist"] = []
#     return redirect(url_for("view_wishlist"))




# @app.route("/update_quantity", methods=["POST"])
# def update_quantity():
#     name = request.form["name"]
#     action = request.form["action"]


#     for item in session["cart"]:
#         if item["name"] == name:
#             if action == "increase":
#                 item["quantity"] += 1
#             elif action == "decrease" and item["quantity"] > 1:
#                 item["quantity"] -= 1
#             break


#     session.modified = True
#     return redirect(url_for("view_cart"))




# if __name__ == "__main__":
#     app.run(debug=True)




