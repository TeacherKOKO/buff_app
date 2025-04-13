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
    saved = load_saved_results()

    if request.method == "POST":
        # 削除リクエストの処理
        if 'delete' in request.form:
            name_to_delete = request.form.get('delete')
            delete_result(name_to_delete)
            return redirect(url_for('index'))

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
                w.append(u[i] * a_buff[i*4+j])
                x.append(v[i] * d_buff[i*4+j])
        for i in range(3, 6):
            for j in range(4):
                w.append(u[i] * b_buff[(i-3)*4+j])
                x.append(v[i] * e_buff[(i-3)*4+j])
        for i in range(6, 9):
            for j in range(4):
                w.append(u[i] * c_buff[(i-6)*4+j])
                x.append(v[i] * f_buff[(i-6)*4+j])

        total_w = sum(w)
        total_x = sum(x)

        if total_w > total_x:
            message = "✅ 勝利！バフは十分です！"
        else:
            areas = buff_labels * 3
            weak_buffs = [areas[i] for i in range(36) if w[i] < x[i]]
            counts = Counter(weak_buffs)
            message = "❌ 敗北...\n以下のバフを強化しましょう：\n"
            for key, val in counts.most_common():
                message += f"・{key}（{val}回）\n"

        results = {'w': w, 'x': x, 'message': message}

        if 'save' in request.form:
            name = request.form.get('result_name', '')
            save_result(name, results)
            return redirect(url_for('index'))

    return render_template(
        "index.html",
        results=results,
        saved_results=saved,
        unit_labels=unit_labels,
        buff_vars=buff_vars,
        indexed_buffs_1=list(enumerate(buff_labels)),
        indexed_buffs_2=list(enumerate(buff_labels))
    )

if __name__ == "__main__":
    app.run(debug=True)
