from flask import Flask, render_template, request, redirect, url_for
from collections import Counter
import os
import json

app = Flask(__name__)

SAVE_FILE = "saved_results.json"

unit_labels = [
    "盾兵T8", "盾兵T9", "盾兵T10",
    "槍兵T8", "槍兵T9", "槍兵T10",
    "弓兵T8", "弓兵T9", "弓兵T10"
]

buff_labels = [
    "盾兵体力", "盾兵攻撃力", "盾兵防御力", "盾兵殺傷力",
    "槍兵体力", "槍兵攻撃力", "槍兵防御力", "槍兵殺傷力",
    "弓兵体力", "弓兵攻撃力", "弓兵防御力", "弓兵殺傷力"
]

buff_vars = [
    'a1', 'a2', 'a3', 'a4', 'b1', 'b2', 'b3', 'b4', 'c1', 'c2', 'c3', 'c4',
    'a5', 'a6', 'a7', 'a8', 'b5', 'b6', 'b7', 'b8', 'c5', 'c6', 'c7', 'c8'
]

def extract_float(request, key):
    val = request.form.get(key)
    try:
        f = float(val)
        return max(0, (f / 100) + 1 - 1)
    except:
        return 0

def extract_int(request, key):
    val = request.form.get(key)
    if val and val.isdigit():
        return max(0, int(val))
    return 0

def make_buffs(base):
    return [
        base[0]*11, base[1]*8, base[2]*11, base[3]*8,
        base[0]*14, base[1]*9, base[2]*12, base[3]*9,
        base[0]*15, base[1]*10, base[2]*13, base[3]*10
    ]

def load_saved_results():
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, 'r', encoding='utf-8') as f:
                data = f.read().strip()
                return json.loads(data) if data else {}
        except json.JSONDecodeError:
            return {}
    return {}

def save_result(name, result):
    results = load_saved_results()
    i = 1
    default_name = "結果"
    while name == "" or name in results:
        name = f"{default_name}{i}"
        i += 1
    results[name] = result
    with open(SAVE_FILE, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

def delete_result(name):
    results = load_saved_results()
    if name in results:
        del results[name]
        with open(SAVE_FILE, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)


@app.route("/", methods=["GET", "POST"])
def index():
    results = None
    winner = None
    saved = load_saved_results()  # ← ここで必ずロード

    if request.method == "POST":
        if "save_name" in request.form:
            # 保存処理
            save_name = request.form["save_name"]
            results = {
                "unit1": {key: float(request.form.get(f"unit1_{key}", 0)) for key in buff_vars},
                "unit2": {key: float(request.form.get(f"unit2_{key}", 0)) for key in buff_vars},
                "base_atk_1": float(request.form.get("base_atk_1", 0)),
                "base_atk_2": float(request.form.get("base_atk_2", 0))
            }
            saved[save_name] = results
            save_results(saved)

        elif "load_name" in request.form:
            # 読み込み処理
            load_name = request.form["load_name"]
            results = saved.get(load_name)

        elif "delete_name" in request.form:
            # 削除処理
            delete_name = request.form["delete_name"]
            if delete_name in saved:
                del saved[delete_name]
                save_results(saved)

        else:
            # 通常の計算処理
            results = {
                "unit1": {key: float(request.form.get(f"unit1_{key}", 0)) for key in buff_vars},
                "unit2": {key: float(request.form.get(f"unit2_{key}", 0)) for key in buff_vars},
                "base_atk_1": float(request.form.get("base_atk_1", 0)),
                "base_atk_2": float(request.form.get("base_atk_2", 0))
            }

        # 勝敗判定
        if results:
            atk1 = results["base_atk_1"] * (
                1 + results["unit1"]["atk_buff"] / 100
            ) * (1 + results["unit1"]["skill_buff"] / 100) * (1 + results["unit1"]["special_buff"] / 100)
            atk2 = results["base_atk_2"] * (
                1 + results["unit2"]["atk_buff"] / 100
            ) * (1 + results["unit2"]["skill_buff"] / 100) * (1 + results["unit2"]["special_buff"] / 100)

            if atk1 > atk2:
                winner = "unit1"
            elif atk2 > atk1:
                winner = "unit2"
            else:
                winner = "draw"

            results["final_atk_1"] = atk1
            results["final_atk_2"] = atk2

    return render_template(
        "index.html",
        results=results,
        winner=winner,
        saved_results=saved,
        unit_labels=unit_labels,
        buff_vars=buff_vars,
        indexed_buffs_1=list(enumerate(buff_labels)),
        indexed_buffs_2=list(enumerate(buff_labels))
    )

if __name__ == "__main__":
    app.run(debug=True)
