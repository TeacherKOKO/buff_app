from flask import Flask, render_template, request
import json
import os

app = Flask(__name__)

# ステータス定義
base_stats = {
    "T8": {
        "盾": {"攻撃": 8, "防御": 11, "殺傷": 8, "体力": 13},
        "槍": {"攻撃": 11, "防御": 9, "殺傷": 12, "体力": 9},
        "弓": {"攻撃": 12, "防御": 8, "殺傷": 13, "体力": 8}
    },
    "T9": {
        "盾": {"攻撃": 9, "防御": 12, "殺傷": 9, "体力": 14},
        "槍": {"攻撃": 12, "防御": 10, "殺傷": 13, "体力": 10},
        "弓": {"攻撃": 13, "防御": 9, "殺傷": 14, "体力": 9}
    },
    "T10": {
        "盾": {"攻撃": 10, "防御": 13, "殺傷": 10, "体力": 14},
        "槍": {"攻撃": 13, "防御": 11, "殺傷": 14, "体力": 11},
        "弓": {"攻撃": 14, "防御": 10, "殺傷": 15, "体力": 10}
    }
}

DATA_FILE = "saved_results.json"

def calc_total(form, is_enemy=False):
    prefix = 'v' if is_enemy else 'u'
    total = 0
    buffs = {
        "攻撃": float(form.get(f"{prefix}_攻撃", 0) or 0),
        "防御": float(form.get(f"{prefix}_防御", 0) or 0),
        "殺傷": float(form.get(f"{prefix}_殺傷", 0) or 0),
        "体力": float(form.get(f"{prefix}_体力", 0) or 0),
    }

    for tier in ["T8", "T9", "T10"]:
        for unit in ["盾", "槍", "弓"]:
            key = f"{prefix}_{tier}_{unit}"
            num = int(form.get(key, "0").replace(",", "") or 0)
            for stat in ["攻撃", "防御", "殺傷", "体力"]:
                base = base_stats[tier][unit][stat]
                buffed = (buffs[stat] / 100) * base
                total += num * buffed
    return total

@app.route("/", methods=["GET", "POST"])
def index():
    results = None
    loaded_data = {}
    saved_names = []
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            saved_names = list(json.load(f).keys())

    if request.method == "POST":
        action = request.form.get("action")
        if action == "save":
            name = request.form.get("save_name")
            if name:
                if os.path.exists(DATA_FILE):
                    with open(DATA_FILE, "r", encoding="utf-8") as f:
                        all_data = json.load(f)
                else:
                    all_data = {}
                all_data[name] = request.form.to_dict()
                with open(DATA_FILE, "w", encoding="utf-8") as f:
                    json.dump(all_data, f, ensure_ascii=False, indent=2)
                saved_names = list(all_data.keys())
        elif action == "load":
            load_name = request.form.get("load_name")
            if load_name and os.path.exists(DATA_FILE):
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    all_data = json.load(f)
                loaded_data = all_data.get(load_name, {})
        elif action == "delete":
            del_name = request.form.get("load_name")
            if del_name and os.path.exists(DATA_FILE):
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    all_data = json.load(f)
                all_data.pop(del_name, None)
                with open(DATA_FILE, "w", encoding="utf-8") as f:
                    json.dump(all_data, f, ensure_ascii=False, indent=2)
                saved_names = list(all_data.keys())
        else:
            total_w = calc_total(request.form, is_enemy=False)
            total_x = calc_total(request.form, is_enemy=True)
            win_message = "勝利！" if total_w > total_x else "敗北…"
            results = {
                "total_w": total_w,
                "total_x": total_x,
                "message": win_message
            }

    return render_template("index.html",
                           loaded_data=loaded_data,
                           results=results,
                           saved_names=saved_names)

if __name__ == "__main__":
    app.run(debug=True)