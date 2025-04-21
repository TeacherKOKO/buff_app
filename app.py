from flask import Flask, render_template, request, redirect, url_for
import json
import os
from collections import Counter

app = Flask(__name__)

SAVE_FILE = "saved_results.json"

unit_labels = [
    "盾兵T8", "盾兵T9", "盾兵T10",
    "槍兵T8", "槍兵T9", "槍兵T10",
    "弓兵T8", "弓兵T9", "弓兵T10"
]

buff_labels = [
    "盾兵攻撃力", "盾兵防御力", "盾兵殺傷力", "盾兵体力",
    "槍兵攻撃力", "槍兵防御力", "槍兵殺傷力", "槍兵体力",
    "弓兵攻撃力", "弓兵防御力", "弓兵殺傷力", "弓兵体力"
]

buff_vars = [
    'a1', 'a2', 'a3', 'a4', 'b1', 'b2', 'b3', 'b4', 'c1', 'c2', 'c3', 'c4',
    'a5', 'a6', 'a7', 'a8', 'b5', 'b6', 'b7', 'b8', 'c5', 'c6', 'c7', 'c8'
]

def extract_float(request, key):
    val = request.form.get(key, "").replace(",", "")
    try:
        return float(val)
    except:
        return 0.0

def extract_int(request, key):
    val = request.form.get(key, "").replace(",", "")
    try:
        return int(val)
    except:
        return 0

def make_buffs(base):
    return [
        base[0] + (base[0] * base[0] / 100),  # 盾兵攻撃力
        base[1] + (base[1] * base[1] / 100),  # 盾兵防御力
        base[2] + (base[2] * base[2] / 100),  # 盾兵殺傷力
        base[3] + (base[3] * base[3] / 100),  # 盾兵体力
        base[4] + (base[4] * base[4] / 100),  # 槍兵攻撃力
        base[5] + (base[5] * base[5] / 100),  # 槍兵防御力
        base[6] + (base[6] * base[6] / 100),  # 槍兵殺傷力
        base[7] + (base[7] * base[7] / 100),  # 槍兵体力
        base[8] + (base[8] * base[8] / 100),  # 弓兵攻撃力
        base[9] + (base[9] * base[9] / 100),  # 弓兵防御力
        base[10] + (base[10] * base[10] / 100),  # 弓兵殺傷力
        base[11] + (base[11] * base[11] / 100),  # 弓兵体力
    ]

@app.route("/", methods=["GET", "POST"])
def index():
    results = None
    saved_names = load_saved_names()
    if request.method == "POST":
        action = request.form.get("action")
        if action == "save":
            name = request.form.get("save_name")
            save_data(name, request.form)
            return redirect(url_for("index"))
        elif action == "load":
            name = request.form.get("load_name")
            data = load_data(name)
            return render_template("index.html", unit_labels=unit_labels,
                                   buff_labels=buff_labels, buff_vars=buff_vars,
                                   saved_names=saved_names, loaded_data=data)
        elif action == "delete":
            name = request.form.get("load_name")
            delete_data(name)
            return redirect(url_for("index"))
        else:
            u = [extract_int(request, f'u{i+1}') for i in range(9)]
            v = [extract_int(request, f'v{i+1}') for i in range(9)]
            buffs = [extract_float(request, key) for key in buff_vars]

            a, b, c = buffs[:4], buffs[4:8], buffs[8:12]
            d, e, f_ = buffs[12:16], buffs[16:20], buffs[20:24]

            a_buff = make_buffs(a)
            b_buff = make_buffs(b)
            c_buff = make_buffs(c)
            d_buff = make_buffs(d)
            e_buff = make_buffs(e)
            f_buff = make_buffs(f_)

            w, x = [], []
            for i in range(3):
                for j in range(4):
                    w.append(u[i] * a_buff[j])
                    x.append(v[i] * d_buff[j])
            for i in range(3, 6):
                for j in range(4):
                    w.append(u[i] * b_buff[j])
                    x.append(v[i] * e_buff[j])
            for i in range(6, 9):
                for j in range(4):
                    w.append(u[i] * c_buff[j])
                    x.append(v[i] * f_buff[j])

            total_w, total_x = sum(w), sum(x)

            if total_w > total_x:
                message = "✅ 勝利！"
            else:
                buff_areas = [
                    "盾兵攻撃力", "盾兵防御力", "盾兵殺傷力", "盾兵体力",
                    "槍兵攻撃力", "槍兵防御力", "槍兵殺傷力", "槍兵体力",
                    "弓兵攻撃力", "弓兵防御力", "弓兵殺傷力", "弓兵体力"
                ] * 3
                weak_buffs = [buff_areas[i] for i in range(36) if w[i] < x[i]]
                counts = Counter(weak_buffs)
                message = "❌ 敗北… 強化が必要なバフ:\n"
                for key, val in counts.most_common():
                    message += f"{key}（{val}回）\n"

            results = {'w': w, 'x': x, 'message': message, 'total_w': total_w, 'total_x': total_x}

    return render_template("index.html", unit_labels=unit_labels, buff_labels=buff_labels,
                           buff_vars=buff_vars, results=results, saved_names=saved_names)

def save_data(name, data):
    all_data = load_all_data()
    all_data[name] = dict(data)
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)

def load_data(name):
    all_data = load_all_data()
    return all_data.get(name, {})

def delete_data(name):
    all_data = load_all_data()
    if name in all_data:
        del all_data[name]
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)

def load_all_data():
    if not os.path.exists(SAVE_FILE):
        return {}
    with open(SAVE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def load_saved_names():
    return list(load_all_data().keys())

if __name__ == "__main__":
    app.run(debug=True)