
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Gợi ý giao dịch", layout="wide")
st.title("📈 Gợi ý giao dịch mạnh")

if "kq_df" not in st.session_state:
    st.warning("⚠️ Vui lòng chạy phân tích ở trang Tổng quan trước.")
    st.stop()

df = st.session_state["kq_df"]

mua_mạnh = df[(df["tín_hiệu_chính"] == "MUA") & (df["độ_tin_cậy"] == "CAO")]
bán_mạnh = df[(df["tín_hiệu_chính"] == "BÁN") & (df["độ_tin_cậy"] == "CAO")]

st.subheader("🔴 Tín hiệu MUA mạnh")
if mua_mạnh.empty:
    st.write("Không có đề xuất MUA mạnh.")
else:
    st.dataframe(mua_mạnh[["mã", "điểm_ròng", "hệ_số_kích_thước_vị_thế", "tín_hiệu_chính"]].sort_values("điểm_ròng", ascending=False))

st.subheader("🔵 Tín hiệu BÁN mạnh")
if bán_mạnh.empty:
    st.write("Không có đề xuất BÁN mạnh.")
else:
    st.dataframe(bán_mạnh[["mã", "điểm_ròng", "hệ_số_kích_thước_vị_thế", "tín_hiệu_chính"]].sort_values("điểm_ròng"))
