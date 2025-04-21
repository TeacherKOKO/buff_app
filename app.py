from flask import Flask, render_template, request, jsonify
import json
import os

app = Flask(__name__)

unit_labels = ["盾", "槍", "弓", "騎", "器"]
buff_labels = ["攻撃", "防御", "殺傷", "体力"]

DATA_FILE = "saved_results.json"


@app.route("/", methods=["GET", "POST"])
def index():
    loaded_data = {}  # 追加：GET時の初期化
    return render_template(
        "index.html",
        unit_labels=unit_labels,
        buff_labels=buff_labels,
        loaded_data=loaded_data,
    )


@app.route("/save", methods=["POST"])
def save_result():
    data = request.json
    name = data.get("name")
    result = data.get("result")
    if not name or not result:
        return jsonify({"status": "error", "message": "保存データが不正です。"})

    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            all_data = json.load(f)
    else:
        all_data = {}

    all_data[name] = result

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)

    return jsonify({"status": "success"})


@app.route("/load/<name>")
def load_result(name):
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            all_data = json.load(f)
        result = all_data.get(name)
        if result:
            return jsonify({"status": "success", "result": result})
    return jsonify({"status": "error", "message": "データが見つかりません。"})


@app.route("/list")
def list_saved():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            all_data = json.load(f)
        return jsonify(list(all_data.keys()))
    return jsonify([])


@app.route("/delete/<name>", methods=["POST"])
def delete_result(name):
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            all_data = json.load(f)
        if name in all_data:
            del all_data[name]
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(all_data, f, ensure_ascii=False, indent=2)
            return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "削除できませんでした。"})


if __name__ == "__main__":
    app.run(debug=True)