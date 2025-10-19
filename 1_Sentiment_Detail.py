
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Chi tiết Sentiment", layout="wide")
st.title("🧠 Chi tiết Tâm lý & Tin tức")

if "kq_df" not in st.session_state:
    st.warning("⚠️ Vui lòng chạy phân tích ở trang Tổng quan trước.")
    st.stop()

df = st.session_state["kq_df"]
mã_chi_tiết = st.selectbox("🔍 Chọn mã coin để xem chi tiết:", df["mã"].tolist())

chi_tiết = df[df["mã"] == mã_chi_tiết].iloc[0]
thành_phần = chi_tiết["thành_phần"]

mạng_xã_hội = thành_phần["mạng_xã_hội"]
tin_tức = thành_phần["tin_tức"]

st.markdown("### 💬 Tâm lý mạng xã hội (LunarCrush)")
st.write(f"**Điểm Galaxy**: {mạng_xã_hội['điểm_galaxy']}")
st.write(f"**AltRank**: #{mạng_xã_hội['xếp_hạng_alt']}")
st.write(f"**Tâm lý Twitter**: {mạng_xã_hội['tâm_lý_twitter']}")
st.write(f"**Tâm lý Reddit**: {mạng_xã_hội['tâm_lý_reddit']}")
st.write(f"**Tâm lý Influencer**: {mạng_xã_hội['tâm_lý_influencer']}")
st.write(f"**Tổng tương tác xã hội**: {mạng_xã_hội['lượng_tương_tác_xã_hội']}")

st.markdown("### 📰 Tin tức (NewsAPI / CryptoPanic)")
st.write(f"**Số tin tích cực**: {tin_tức['số_tin_tích_cực']}")
st.write(f"**Số tin tiêu cực**: {tin_tức['số_tin_tiêu_cực']}")
st.write(f"**Tâm lý trung bình**: {tin_tức['tâm_lý_tin_tức_trung_bình']}")

if len(tin_tức["tin_nóng"]) > 0:
    st.markdown("**🧨 Tin nóng nổi bật:**")
    for tin in tin_tức["tin_nóng"][:3]:
        st.write(f"➡️ {tin['tiêu_đề']} (Tâm lý: {tin['tâm_lý']}, Tác động: {tin['tác_động']})")
