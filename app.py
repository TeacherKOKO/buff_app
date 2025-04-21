from flask import Flask, render_template, request, jsonify
import json
import os

app = Flask(__name__)

unit_labels = ["盾", "槍", "弓", "騎", "器"]
buff_labels = ["攻撃", "防御", "殺傷", "体力"]

# バフ変数の並び順：盾攻撃→盾防御→…→器体力（味方12）→盾攻撃→…→器体力（敵12）
buff_vars = [
    'wa', 'wd', 'wk', 'wh',  # 味方：盾
    'sa', 'sd', 'sk', 'sh',  # 味方：槍
    'ha', 'hd', 'hk', 'hh',  # 味方：弓
    'ea', 'ed', 'ek', 'eh',  # 味方：騎
    'fa', 'fd', 'fk', 'fh',  # 味方：器
    'ba', 'bd', 'bk', 'bh',  # 敵：盾
    'na', 'nd', 'nk', 'nh',  # 敵：槍
    'ma', 'md', 'mk', 'mh',  # 敵：弓
    'la', 'ld', 'lk', 'lh',  # 敵：騎
    'ka', 'kd', 'kk', 'kh'   # 敵：器
]

DATA_FILE = "saved_results.json"


@app.route("/", methods=["GET", "POST"])
def index():
    loaded_data = {}
    results = None
    saved_names = []

    if request.method == "POST":
        action = request.form.get("action")
        save_name = request.form.get("save_name", "").strip()

        # フォームデータを収集（数値変換も）
        form_data = {}
        for i in range(1, 6):
            form_data[f"u{i}"] = request.form.get(f"u{i}", "").replace(",", "")
            form_data[f"v{i}"] = request.form.get(f"v{i}", "").replace(",", "")
        for var in buff_vars:
            form_data[var] = request.form.get(var, "").replace(",", "")

        if action == "save" and save_name:
            # 保存処理
            if os.path.exists(DATA_FILE):
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    all_data = json.load(f)
            else:
                all_data = {}

            all_data[save_name] = form_data

            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(all_data, f, ensure_ascii=False, indent=2)

        elif action == "load":
            load_name = request.form.get("load_name")
            if load_name and os.path.exists(DATA_FILE):
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    all_data = json.load(f)
                loaded_data = all_data.get(load_name, {})

        elif action == "delete":
            delete_name = request.form.get("load_name")
            if delete_name and os.path.exists(DATA_FILE):
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    all_data = json.load(f)
                if delete_name in all_data:
                    del all_data[delete_name]
                    with open(DATA_FILE, "w", encoding="utf-8") as f:
                        json.dump(all_data, f, ensure_ascii=False, indent=2)

        else:
            # 計算処理
            try:
                u_vals = [int(request.form.get(f"u{i}", "0").replace(",", "") or 0) for i in range(1, 6)]
                v_vals = [int(request.form.get(f"v{i}", "0").replace(",", "") or 0) for i in range(1, 6)]
                w_buffs = [float(request.form.get(buff_vars[i], "0").replace(",", "") or 0) for i in range(20)]  # 味方バフ
                e_buffs = [float(request.form.get(buff_vars[i], "0").replace(",", "") or 0) for i in range(20, 40)]  # 敵バフ

                # バフ後ステータスを計算（元値 × (1 + バフ合計 / 100)）
                def calc_total(units, buffs):
                    total = 0
                    for i in range(5):  # 盾～器
                        attack = buffs[i * 4]
                        defense = buffs[i * 4 + 1]
                        kill = buffs[i * 4 + 2]
                        hp = buffs[i * 4 + 3]
                        unit_val = units[i]
                        buff_rate = (attack + defense + kill + hp) / 100
                        total += unit_val * (1 + buff_rate)
                    return total

                total_w = calc_total(u_vals, w_buffs)
                total_x = calc_total(v_vals, e_buffs)

                if total_w > total_x:
                    message = "✅ 勝利！味方の方が強力です。"
                elif total_w < total_x:
                    message = "❌ 敗北…敵の方が強力です。"
                else:
                    message = "⚔️ 引き分けです。"

                results = {
                    "total_w": total_w,
                    "total_x": total_x,
                    "message": message
                }

            except Exception as e:
                results = {"total_w": 0, "total_x": 0, "message": f"エラーが発生しました: {str(e)}"}

    # 保存名一覧の取得
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            all_data = json.load(f)
        saved_names = list(all_data.keys())

    return render_template(
        "index.html",
        unit_labels=unit_labels,
        buff_labels=buff_labels,
        buff_vars=buff_vars,
        loaded_data=loaded_data,
        results=results,
        saved_names=saved_names,
        request=request
    )


if __name__ == "__main__":
    app.run(debug=True)