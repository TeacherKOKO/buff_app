from flask import Flask, render_template_string, request
from collections import Counter

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>バフ計算ツール</title>
    <style>
        body { font-family: sans-serif; line-height: 1.6; padding: 20px; background: #eef8ff; }
        ul { list-style: none; padding: 0; }
        li { margin-bottom: 5px; }
        .win { color: green; }
        .lose { color: red; }
        pre { white-space: pre-wrap; background: #fff; padding: 10px; border-radius: 5px; }
        .scroll-box { max-height: 300px; overflow-y: auto; border: 1px solid #ccc; background: #fff; padding: 10px; border-radius: 8px; }
    </style>
</head>
<body>
    <h1>バフ比較計算ツール</h1>
    <form method="post">
        <h2>味方の兵の数</h2>
        <ul>
            {% for i in range(9) %}
            <li>{{ unit_labels[i] }}: <input type="number" name="u{{i+1}}" min="0"></li>
            {% endfor %}
        </ul>

        <h2>敵の兵の数</h2>
        <ul>
            {% for i in range(9) %}
            <li>{{ unit_labels[i] }}: <input type="number" name="v{{i+1}}" min="0"></li>
            {% endfor %}
        </ul>

        <h2>味方のバフ</h2>
        <ul>
            {% for i in range(12) %}
            <li>{{ buff_labels[i] }}: <input type="number" name="{{ buff_vars[i] }}" step="0.1" min="0"></li>
            {% endfor %}
        </ul>

        <h2>敵のバフ</h2>
        <ul>
            {% for i in range(12, 24) %}
            <li>{{ buff_labels[i-12] }}: <input type="number" name="{{ buff_vars[i] }}" step="0.1" min="0"></li>
            {% endfor %}
        </ul>

        <button type="submit">計算</button>
    </form>

    {% if results %}
        <h2>結果表示</h2>
        <div class="scroll-box">
            <ul>
            {% for i in range(36) %}
                <li class="{{ 'win' if results['w'][i] > results['x'][i] else 'lose' }}">
                    味方: {{ results['w'][i] | round(1) }} vs 敵: {{ results['x'][i] | round(1) }}
                </li>
            {% endfor %}
            </ul>
        </div>
        <h3>判定:</h3>
        <pre>{{ results['message'] }}</pre>
    {% endif %}
</body>
</html>
"""

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
    try:
        val = int(request.form.get(key, 0))
        return max(0, val)
    except:
        return 0

def make_buffs(base, unit_counts):
    buffs = []
    for i in range(3):
        for j in range(4):
            index = i * 4 + j
            buff_value = base[j]
            unit_count = unit_counts[i]
            result = (buff_value / 100) * unit_count
            buffs.append(result)
    return buffs

@app.route("/", methods=["GET", "POST"])
def index():
    results = None
    if request.method == "POST":
        u = [extract_int(request, f'u{i+1}') for i in range(9)]
        v = [extract_int(request, f'v{i+1}') for i in range(9)]
        buffs = [extract_float(request, key) for key in buff_vars]

        # 味方
        a = buffs[0:4]
        b = buffs[4:8]
        c = buffs[8:12]
        # 敵
        d = buffs[12:16]
        e = buffs[16:20]
        f_ = buffs[20:24]

        a_buff = make_buffs(a, u[0:3])
        b_buff = make_buffs(b, u[3:6])
        c_buff = make_buffs(c, u[6:9])
        d_buff = make_buffs(d, v[0:3])
        e_buff = make_buffs(e, v[3:6])
        f_buff = make_buffs(f_, v[6:9])

        w = a_buff + b_buff + c_buff
        x = d_buff + e_buff + f_buff

        total_w = sum(w)
        total_x = sum(x)

        if total_w > total_x:
            message = "問題なし！素晴らしい育成だ！"
        else:
            buff_areas = (
                ["盾兵体力", "盾兵攻撃力", "盾兵防御力", "盾兵殺傷力"] * 3 +
                ["槍兵体力", "槍兵攻撃力", "槍兵防御力", "槍兵殺傷力"] * 3 +
                ["弓兵体力", "弓兵攻撃力", "弓兵防御力", "弓兵殺傷力"] * 3
            )
            weak_buffs = [buff_areas[i] for i in range(36) if w[i] < x[i]]
            counts = Counter(weak_buffs)
            message = "敗北しています。\n以下のバフを強化すると勝てるかも：\n"
            for key, val in counts.most_common():
                message += f"{key}（{val}回）\n"

        results = {'w': w, 'x': x, 'message': message}

    return render_template_string(HTML_TEMPLATE,
                                  unit_labels=unit_labels,
                                  buff_labels=buff_labels,
                                  buff_vars=buff_vars,
                                  results=results)

if __name__ == '__main__':
    app.run(debug=True)