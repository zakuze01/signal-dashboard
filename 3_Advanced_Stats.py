
import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(page_title="Thống kê nâng cao", layout="wide")
st.title("📊 Thống kê nâng cao & Tương quan")

if "kq_df" not in st.session_state:
    st.warning("⚠️ Vui lòng chạy phân tích ở trang Tổng quan trước.")
    st.stop()

df = st.session_state["kq_df"]

st.markdown("## 🔗 Ma trận tương quan (Correlation Matrix)")

cols_corr = ["điểm_mua", "điểm_bán", "điểm_ròng", "hệ_số_kích_thước_vị_thế"]
corr_matrix = df[cols_corr].corr()

fig, ax = plt.subplots(figsize=(6, 4))
sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", fmt=".2f", ax=ax)
st.pyplot(fig)

st.markdown("## 📉 Phân phối điểm ròng")

fig2, ax2 = plt.subplots()
sns.histplot(df["điểm_ròng"], bins=20, kde=True, ax=ax2)
ax2.set_title("Phân phối điểm ròng")
st.pyplot(fig2)

st.markdown("## 📈 Biểu đồ phân tán: Điểm ròng vs Kích thước vị thế")
fig3, ax3 = plt.subplots()
sns.scatterplot(data=df, x="điểm_ròng", y="hệ_số_kích_thước_vị_thế", hue="tín_hiệu_chính", ax=ax3)
ax3.set_title("Scatter: Điểm ròng vs Vị thế")
st.pyplot(fig3)
