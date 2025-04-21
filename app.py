from flask import Flask, render_template, request, redirect, url_for
import json
import os
from collections import Counter

app = Flask(__name__)
SAVE_FILE = 'saved_data.json'

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

def extract_number(val):
    try:
        return int(str(val).replace(',', '').strip())
    except:
        return 0

def extract_float(val):
    try:
        return float(str(val).replace(',', '').strip())
    except:
        return 0.0

def make_buffs(base):
    return [
        base[0]*11/100, base[1]*8/100, base[2]*8/100, base[3]*11/100,
        base[0]*14/100, base[1]*9/100, base[2]*9/100, base[3]*14/100,
        base[0]*15/100, base[1]*10/100, base[2]*10/100, base[3]*15/100
    ]

@app.route('/', methods=['GET', 'POST'])
def index():
    results = None
    saves = load_saves()

    if request.method == 'POST':
        u = [extract_number(request.form.get(f'u{i+1}')) for i in range(9)]
        v = [extract_number(request.form.get(f'v{i+1}')) for i in range(9)]
        buffs = [extract_float(request.form.get(k)) for k in buff_vars]

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
            message = "✅ 問題なし！素晴らしい育成だ！"
        else:
            areas = buff_labels * 3
            weak = [areas[i] for i in range(36) if w[i] < x[i]]
            counts = Counter(weak)
            message = "❌ 敗北しています。\n強化が必要なバフ：\n"
            message += '\n'.join(f"{k}（{v}回）" for k, v in counts.most_common())

        results = {'w': w, 'x': x, 'message': message, 'total_w': total_w, 'total_x': total_x}

    return render_template("index.html",
        unit_labels=unit_labels,
        buff_labels=buff_labels,
        buff_vars=buff_vars,
        results=results,
        saves=saves
    )

@app.route('/save', methods=['POST'])
def save():
    name = request.form.get("save_name", "").strip()
    if name:
        data = dict(request.form)
        saves = load_saves()
        saves[name] = data
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(saves, f, ensure_ascii=False, indent=2)
    return redirect(url_for('index'))

@app.route('/load/<name>')
def load(name):
    saves = load_saves()
    data = saves.get(name, {})
    return render_template("index.html",
        unit_labels=unit_labels,
        buff_labels=buff_labels,
        buff_vars=buff_vars,
        results=None,
        form_data=data,
        saves=saves
    )

@app.route('/delete/<name>')
def delete(name):
    saves = load_saves()
    if name in saves:
        del saves[name]
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(saves, f, ensure_ascii=False, indent=2)
    return redirect(url_for('index'))

def load_saves():
    if not os.path.exists(SAVE_FILE):
        return {}
    with open(SAVE_FILE, encoding="utf-8") as f:
        return json.load(f)

if __name__ == "__main__":
    app.run(debug=True)