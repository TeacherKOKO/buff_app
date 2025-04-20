from flask import Flask, render_template, request
from collections import Counter

app = Flask(__name__)

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
    try:
        val = float(request.form.get(key, 0))
        return max(0, val)
    except:
        return 0

def extract_int(request, key):
    val = request.form.get(key)
    if val and val.isdigit():
        return max(0, int(val))
    return 0

def make_buffs(base):
    return [
        1 + base[0]/100, 1 + base[1]/100, 1 + base[2]/100, 1 + base[3]/100,
        1 + base[0]/100, 1 + base[1]/100, 1 + base[2]/100, 1 + base[3]/100,
        1 + base[0]/100, 1 + base[1]/100, 1 + base[2]/100, 1 + base[3]/100
    ]

@app.route('/', methods=['GET', 'POST'])
def index():
    results = None
    if request.method == 'POST':
        u = [extract_int(request, f'u{i+1}') for i in range(9)]
        v = [extract_int(request, f'v{i+1}') for i in range(9)]
        buffs = [extract_float(request, key) for key in buff_vars]

        a = buffs[:4]
        b = buffs[4:8]
        c = buffs[8:12]
        d = buffs[12:16]
        e = buffs[16:20]
        f_ = buffs[20:24]

        a_buff = make_buffs(a)
        b_buff = make_buffs(b)
        c_buff = make_buffs(c)
        d_buff = make_buffs(d)
        e_buff = make_buffs(e)
        f_buff = make_buffs(f_)

        w = []
        x = []
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
            message = f"✅ 問題なし！素晴らしい育成だ！\n（味方: {round(total_w)} vs 敵: {round(total_x)}）"
        else:
            buff_areas = [
                "盾兵体力", "盾兵攻撃力", "盾兵防御力", "盾兵殺傷力",
                "盾兵体力", "盾兵攻撃力", "盾兵防御力", "盾兵殺傷力",
                "盾兵体力", "盾兵攻撃力", "盾兵防御力", "盾兵殺傷力",
                "槍兵体力", "槍兵攻撃力", "槍兵防御力", "槍兵殺傷力",
                "槍兵体力", "槍兵攻撃力", "槍兵防御力", "槍兵殺傷力",
                "槍兵体力", "槍兵攻撃力", "槍兵防御力", "槍兵殺傷力",
                "弓兵体力", "弓兵攻撃力", "弓兵防御力", "弓兵殺傷力",
                "弓兵体力", "弓兵攻撃力", "弓兵防御力", "弓兵殺傷力",
                "弓兵体力", "弓兵攻撃力", "弓兵防御力", "弓兵殺傷力",
            ]
            weak_buffs = [buff_areas[i] for i in range(36) if w[i] < x[i]]
            counts = Counter(weak_buffs)
            message = f"❌ 敗北しています（味方: {round(total_w)} vs 敵: {round(total_x)}）\n以下のバフを強化すると勝てるかも！！：\n"
            for key, val in counts.most_common():
                message += f"{key}（{val}回）\n"

        results = {'w': w, 'x': x, 'message': message, 'total_w': total_w, 'total_x': total_x}

    return render_template("index.html", unit_labels=unit_labels, buff_labels=buff_labels, buff_vars=buff_vars, results=results)

if __name__ == '__main__':
    app.run(debug=True)