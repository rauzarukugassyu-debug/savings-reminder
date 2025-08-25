# savings_app.py
import streamlit as st
from datetime import date

st.set_page_config(page_title="節約リマインダー", page_icon="💰", layout="centered")

# ===== あなた向け初期値（必要なら下の値を自分用に直してからデプロイ）=====
BIRTH_YEAR_DEFAULT = 1994   # 生年
TARGET_AGE_DEFAULT = 60     # 目標年齢（例: 60）
RATE_DEFAULT = 0.07         # 想定年利（7% = 0.07）
START_DATE_DEFAULT = date(2025, 8, 25)  # 節約開始日（初日が別なら変更）
DAILY_SAVING_DEFAULT = 1000 # 1日の節約額（円）

# ===== ヘッダ =====
st.title("💰 節約リマインダー")

with st.expander("設定（必要に応じて変更）", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        birth_year = st.number_input("生年（西暦）", value=BIRTH_YEAR_DEFAULT, step=1)
        target_age = st.number_input("目標年齢", value=TARGET_AGE_DEFAULT, min_value=1, step=1)
        rate = st.number_input("想定年利（小数）", value=RATE_DEFAULT, help="例: 7% → 0.07")
    with col2:
        start_date = st.date_input("節約開始日", value=START_DATE_DEFAULT)
        daily_saving = st.number_input("1日の節約額（円）", value=DAILY_SAVING_DEFAULT, step=100)

# ===== 基本計算 =====
today = date.today()

# 何日目か（初日を1日目としてカウント、未来日なら0に丸め）
days = max((today - start_date).days + 1, 0)

# 今日までの累計元本（= 実際に捻出できた金額）
principal = daily_saving * days

# 現在年齢と60歳までの残り年数（負にならないよう丸め）
current_age = today.year - int(birth_year)
remain_years = max(int(target_age) - current_age, 0)

# ---- ① 現時点の累計元本を、60歳まで年利rで複利運用した場合（= これまでの成果の将来価値）----
def fv_lump_sum(pv: float, r: float, n_years: int) -> float:
    """一括投資の将来価値"""
    return pv * ((1 + r) ** n_years) if n_years > 0 else float(pv)

fv_from_principal = fv_lump_sum(principal, rate, remain_years)

# ---- ② ここから60歳まで、毎日いまの金額を積み上げ続けた場合の将来価値（= これからの努力の見込み）----
# 年間積立額A = 1日額×365、年数nに対する年金終価係数 FV = A * ((1+r)^n - 1) / r
def fv_annuity(annual: float, r: float, n_years: int) -> float:
    """年1回まとめて積み立てる近似（年金終価係数）"""
    if n_years <= 0:
        return 0.0
    return annual * (((1 + r) ** n_years) - 1) / r

annual_contrib = daily_saving * 365
fv_if_continue = fv_annuity(annual_contrib, rate, remain_years)

# ---- （参考）日次積立の“より厳密に近い”近似（表示はオプション）----
# 日次利率 r_d = (1+r)^(1/365) - 1、n_days = 365 * 年数
def fv_daily_contrib(daily: float, r_annual: float, n_years: int) -> float:
    """毎日一定額を積み立てる場合の近似（日次複利）"""
    if n_years <= 0:
        return 0.0
    r_d = (1 + r_annual) ** (1/365) - 1
    n_days = 365 * n_years
    return daily * (((1 + r_d) ** n_days) - 1) / r_d

fv_if_continue_daily = fv_daily_contrib(daily_saving, rate, remain_years)

# ===== 表示 =====
st.subheader(f"今日で **{days} 日目**")
m1, m2 = st.columns(2)
with m1:
    st.metric("累計節約額（元本）", f"{principal:,.0f} 円")
with m2:
    st.metric(f"{int(target_age)}歳（{int(birth_year)+int(target_age)}年）までの残り年数", f"{remain_years} 年")

st.markdown("### 将来価値（60歳時点の見込み）")

c1, c2 = st.columns(2)
with c1:
    st.caption("これまでの成果（今日までの元本）を運用した場合")
    st.success(f"累計元本の将来価値：**{fv_from_principal:,.0f} 円**")
with c2:
    st.caption("これからも毎日続けた場合の見込み（年1回積立の近似）")
    st.info(f"今後の積立の将来価値：**{fv_if_continue:,.0f} 円**")

st.write("—")
st.caption("補足：日次積立の近似（参考値。上の“年1回積立の近似”と概ね近いです）")
st.write(f"日次積立の将来価値（参考）：**{fv_if_continue_daily:,.0f} 円**")

# 未来を複数年齢でざっくり比較
st.write("—")
st.write("将来の自分を複数年齢でチェック（どれも“今日までの元本”のみを複利運用した場合の目安）：")
cols = st.columns(3)
for i, tgt in enumerate([40, 50, 60]):
    yrs = max(tgt - current_age, 0)
    fv = fv_lump_sum(principal, rate, yrs)
    with cols[i]:
        st.caption(f"{tgt}歳時点")
        st.write(f"**{fv:,.0f} 円**")

st.info(
    "解説：\n"
    "・左の“累計元本の将来価値”は、**これまで捻出できた額だけ**を60歳まで運用した場合の金額。\n"
    "・右の“今後の積立の将来価値”は、**今日と同じ日額を60歳まで毎日続ける**と仮定した場合の金額（年1回積立の近似）。\n"
    "・“日次積立の参考値”はより厳密に近い近似で、上の値と大差がないはずです。"
)