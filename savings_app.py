# savings_app.py
# そのまま貼り付けて使えます（Streamlitのみで動作）

import streamlit as st
from datetime import date
import pandas as pd

st.set_page_config(page_title="節約リマインダー", page_icon="💰", layout="centered")

# -----------------------------
# URLパラメータ ヘルパ（新旧API対応）
# -----------------------------
def get_qp():
    # 新API (Streamlit ≥ 1.33)
    try:
        return dict(st.query_params)
    except Exception:
        pass
    # 旧API
    try:
        return {
            k: (v[0] if isinstance(v, list) else v)
            for k, v in st.experimental_get_query_params().items()
        }
    except Exception:
        return {}

def set_qp(**kwargs):
    # 新API
    try:
        st.query_params.update(kwargs)
        return
    except Exception:
        pass
    # 旧API
    try:
        st.experimental_set_query_params(**kwargs)
    except Exception:
        pass

# -----------------------------
# デフォルト値（URLパラメータがあれば上書き）
# -----------------------------
qp = get_qp()
BIRTH_YEAR_DEFAULT     = int(qp.get("birth", 1994))
TARGET_AGE_DEFAULT     = int(qp.get("age", 60))
RATE_DEFAULT           = float(qp.get("rate", 0.07))
DAILY_SAVING_DEFAULT   = int(qp.get("daily", 1000))
try:
    START_DATE_DEFAULT = date.fromisoformat(qp.get("start", "2025-08-25"))
except Exception:
    START_DATE_DEFAULT = date(2025, 8, 25)

# -----------------------------
# UI
# -----------------------------
st.title("💰 節約リマインダー")
st.caption("開始日からの累計節約額を、60歳時点の価値（複利）に換算して表示します。設定はURLに保存できます。")

with st.expander("設定（必要なら変更）", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        birth_year  = st.number_input("生年（西暦）", value=BIRTH_YEAR_DEFAULT, step=1)
        target_age  = st.number_input("目標年齢", value=TARGET_AGE_DEFAULT, min_value=1, step=1)
        rate        = st.number_input("想定年利（小数）", value=RATE_DEFAULT, help="例: 7% → 0.07")
    with col2:
        start_date   = st.date_input("節約開始日", value=START_DATE_DEFAULT)
        daily_saving = st.number_input("1日の節約額（円）", value=DAILY_SAVING_DEFAULT, step=100)

# -----------------------------
# 計算
# -----------------------------
today = date.today()
days = max((today - start_date).days + 1, 0)         # 何日目か（未来設定のマイナスは0に）
principal = int(daily_saving) * int(days)            # 累計元本

current_age = today.year - int(birth_year)
remain_years = max(int(target_age) - current_age, 0) # 60歳までの残り年数（0未満は0）

# 将来価値（複利）
future_value = principal * ((1 + float(rate)) ** remain_years) if remain_years > 0 else float(principal)

# -----------------------------
# 表示
# -----------------------------
st.subheader(f"今日で **{days} 日目**")
cols = st.columns(3)
with cols[0]:
    st.metric("累計元本", f"{principal:,.0f} 円")
with cols[1]:
    st.metric(f"{int(target_age)}歳（{int(birth_year)+int(target_age)}年）の価値", f"{future_value:,.0f} 円")
with cols[2]:
    multiple = (future_value / principal) if principal else 0
    st.metric("倍率", f"{multiple:,.2f} ×")

# 参考：40/50/60歳スナップショット
st.write("—")
snap_cols = st.columns(3)
for i, tgt in enumerate([40, 50, 60]):
    yrs = max(tgt - current_age, 0)
    fv = principal * ((1 + float(rate)) ** yrs) if yrs > 0 else float(principal)
    with snap_cols[i]:
        st.caption(f"{tgt}歳時点")
        st.write(f"**{fv:,.0f} 円**")

# 60歳までの推移グラフ（単純に“今の元本を据え置き運用した場合の参考曲線”）
years_seq = list(range(current_age, int(target_age) + 1))
values_seq = [principal * ((1 + float(rate)) ** max(y - current_age, 0)) for y in years_seq]
df = pd.DataFrame({"age": years_seq, "value": values_seq}).set_index("age")
st.line_chart(df)

# -----------------------------
# 保存（URLに埋め込む）
# -----------------------------
save_col, reset_col = st.columns(2)
with save_col:
    if st.button("🔒 設定を保存（URLに埋め込み）"):
        set_qp(
            birth=str(int(birth_year)),
            age=str(int(target_age)),
            rate=str(float(rate)),
            daily=str(int(daily_saving)),
            start=start_date.isoformat(),
        )
        st.success("設定をURLに保存しました。この状態でSafariの“共有 → ホーム画面に追加”を行うと固定で開けます。")
with reset_col:
    if st.button("↩️ 保存URLをクリア"):
        set_qp()  # クエリ無しへ
        st.info("URLの設定をクリアしました。再読み込みで初期値に戻ります。")
