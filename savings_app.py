# --- 1) 先頭付近のimportの直後に置く -----------------
from datetime import date

# 互換用ヘルパ（Streamlitのバージョン差を吸収）
def get_qp():
    try:
        return dict(st.query_params)
    except:
        return {k: v[0] if isinstance(v, list) else v
                for k, v in st.experimental_get_query_params().items()}

def set_qp(**kwargs):
    try:
        st.query_params.update(kwargs)
    except:
        st.experimental_set_query_params(**kwargs)

# --- 2) デフォルト値を「クエリがあれば上書き」する -----------------
qp = get_qp()

BIRTH_YEAR_DEFAULT = int(qp.get("birth", 1994))
TARGET_AGE_DEFAULT  = int(qp.get("age", 60))
RATE_DEFAULT        = float(qp.get("rate", 0.07))
DAILY_SAVING_DEFAULT= int(qp.get("daily", 1000))

# start=YYYY-MM-DD 形式で保存・復元
try:
    START_DATE_DEFAULT = date.fromisoformat(qp.get("start", "2025-08-25"))
except Exception:
    START_DATE_DEFAULT = date(2025, 8, 25)

# --- 3) UI生成（あなたの既存UIと統合でOK） -----------------
with st.expander("設定（必要なら変更）", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        birth_year  = st.number_input("生年（西暦）", value=BIRTH_YEAR_DEFAULT, step=1)
        target_age  = st.number_input("目標年齢", value=TARGET_AGE_DEFAULT, min_value=1, step=1)
        rate        = st.number_input("想定年利（小数）", value=RATE_DEFAULT, help="例: 7% → 0.07")
    with col2:
        start_date   = st.date_input("節約開始日", value=START_DATE_DEFAULT)
        daily_saving = st.number_input("1日の節約額（円）", value=DAILY_SAVING_DEFAULT, step=100)

# --- 4) 「保存」「リセット」ボタン -----------------
c_save, c_reset = st.columns(2)
with c_save:
    if st.button("🔒 設定を保存（URLに埋め込み）"):
        set_qp(
            birth=str(int(birth_year)),
            age=str(int(target_age)),
            rate=str(float(rate)),
            daily=str(int(daily_saving)),
            start=str(start_date.isoformat()),
        )
        st.success("設定をURLに保存しました。この状態で“共有→ホーム画面に追加”すると固定されます。")
with c_reset:
    if st.button("↩️ 保存URLをクリア"):
        set_qp()  # クエリを空に
        st.info("URLの設定をクリアしました。ページを再読み込みすると初期値に戻ります。")
