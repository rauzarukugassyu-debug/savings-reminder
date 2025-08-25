# savings_app.py
import streamlit as st
from datetime import date

st.set_page_config(page_title="節約リマインダー", page_icon="💰", layout="centered")

# ===== 初期値（あなた用にプリセット）=====
BIRTH_YEAR_DEFAULT = 1994
TARGET_AGE_DEFAULT = 60
RATE_DEFAULT = 0.07
START_DATE_DEFAULT = date(2025, 8, 25)  # 開始日に合わせて変更OK
DAILY_SAVING_DEFAULT = 1000             # 1日の節約額（円）

st.title("💰 節約リマインダー")

with st.expander("設定（必要なら変更）", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        birth_year = st.number_input("生年（西暦）", value=BIRTH_YEAR_DEFAULT, step=1)
        target_age = st.number_input("目標年齢", value=TARGET_AGE_DEFAULT, min_value=1, step=1)
        rate = st.number_input("想定年利（小数）", value=RATE_DEFAULT, help="例: 7% → 0.07")
    with col2:
        start_date = st.date_input("節約開始日", value=START_DATE_DEFAULT)
        daily_saving = st.number_input("1日の節約額（円）", value=DAILY_SAVING_DEFAULT, step=100)

# ===== 計算 =====
today = date.today()
days = max((today - start_date).days + 1, 0)  # マイナス防止
principal = daily_saving * days               # 今日までの累計元本

current_age = today.year - int(birth_year)
remain_years = max(int(target_age) - current_age, 0)  # マイナス防止

# 将来価値（複利）
future_value = principal * ((1 + rate) ** remain_years) if remain_years > 0 else float(principal)

# ===== 表示 =====
st.subheader(f"今日で **{days} 日目**")
st.metric("累計節約額（元本）", f"{principal:,.0f} 円")
st.metric(f"{int(target_age)}歳（{int(birth_year)+int(target_age)}年）時点の価値", f"{future_value:,.0f} 円", help="想定年利で複利運用した場合")

# 参考：将来目線を複数年齢で
st.write("—")
st.write("将来の自分にもっとズーム：")
cols = st.columns(3)
for i, tgt in enumerate([40, 50, 60]):
    yrs = max(tgt - current_age, 0)
    fv = principal * ((1 + rate) ** yrs) if yrs > 0 else float(principal)
    with cols[i]:
        st.caption(f"{tgt}歳時点")
        st.write(f"**{fv:,.0f} 円**")

st.info("ホーム画面に追加して“毎朝タップ→数字が増えてる！”を確認すると継続しやすいよ。")
