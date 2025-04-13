from flask import Flask, render_template, request, redirect, url_for
import json
import os

app = Flask(__name__)
SAVE_FILE = "saved_results.json"

def load_saved_results():
    if not os.path.exists(SAVE_FILE):
        return {}
    with open(SAVE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_results(data):
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@app.route("/", methods=["GET", "POST", "HEAD"])
def index():
    saved_results = load_saved_results()

    if request.method == "HEAD":
        return "", 200

    if request.method == "POST":
        base_stat = float(request.form.get("base_stat", 0))
        buff_percent = float(request.form.get("buff_percent", 0))
        result = base_stat * (1 + buff_percent / 100)

        save_name = request.form.get("save_name")
        if save_name:
            saved_results[save_name] = {
                "base_stat": base_stat,
                "buff_percent": buff_percent,
                "result": result
            }
            save_results(saved_results)

        return render_template(
            "index.html",
            result=result,
            base_stat=base_stat,
            buff_percent=buff_percent,
            saved_results=saved_results
        )

    return render_template("index.html", saved_results=saved_results)

@app.route("/load/<name>")
def load_result(name):
    saved_results = load_saved_results()
    if name in saved_results:
        data = saved_results[name]
        return render_template(
            "index.html",
            result=data["result"],
            base_stat=data["base_stat"],
            buff_percent=data["buff_percent"],
            saved_results=saved_results
        )
    return redirect(url_for("index"))

@app.route("/delete/<name>")
def delete_result(name):
    saved_results = load_saved_results()
    if name in saved_results:
        del saved_results[name]
        save_results(saved_results)
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)