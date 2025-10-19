
import streamlit as st
import pandas as pd
from alpha_signal_checker_plus import (
    lấy_tâm_lý_mạng_xã_hội,
    lấy_tác_động_tin_tức,
    lấy_chỉ_số_kinh_tế_vĩ_mô,
    chấm_điểm_tâm_lý_mạng_xã_hội,
    chấm_điểm_tác_động_tin_tức,
    chấm_điểm_môi_trường_vĩ_mô,
    chấm_điểm_fear_greed,
    chấm_điểm_tvl_defi,
    lấy_chỉ_số_fear_greed,
    lấy_tvl_tổng_defi,
    KếtQuảTínHiệu,
    asdict
)
import requests
from typing import List

st.set_page_config(page_title="Tổng Quan Tín Hiệu", layout="wide")
st.title("📊 Dashboard Tín Hiệu Crypto – Tổng Quan")

số_lượng = st.slider("🔢 Chọn số lượng coin top để phân tích:", 10, 500, 50, 10)
mức_điểm_ròng = st.slider("🎯 Điểm ròng tối thiểu:", 0.0, 5.0, 2.0, 0.1)

@st.cache_data(show_spinner=False)
def lấy_top_500_coin() -> List[str]:
    danh_sách = []
    for page in [1, 2]:
        url = "https://api.coingecko.com/api/v3/coins/markets"
        params = {
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": 250,
            "page": page,
        }
        try:
            resp = requests.get(url, params=params, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                danh_sách.extend([coin["symbol"].upper() for coin in data])
        except:
            pass
    return danh_sách

if st.button("🚀 Bắt đầu phân tích"):
    danh_sách_coin = lấy_top_500_coin()[:số_lượng]
    kết_quả = []

    vĩ_mô = lấy_chỉ_số_kinh_tế_vĩ_mô()
    fear_greed = lấy_chỉ_số_fear_greed()
    tvl_defi = lấy_tvl_tổng_defi()

    with st.spinner("🔍 Đang phân tích..."):
        for mã in danh_sách_coin:
            mạng_xã_hội = lấy_tâm_lý_mạng_xã_hội(mã)
            tin_tức = lấy_tác_động_tin_tức(mã)

            thành_phần = {
                "mạng_xã_hội": asdict(mạng_xã_hội),
                "tin_tức": asdict(tin_tức),
                "vĩ_mô": asdict(vĩ_mô),
            }

            tổng_điểm_mua, tổng_điểm_bán = 0.0, 0.0
            tất_cả_tín_hiệu, tất_cả_cảnh_báo = [], []
            hệ_số_kích_thước = 1.0

            m_mua, m_bán, m_tín_hiệu, m_cảnh_báo = chấm_điểm_tâm_lý_mạng_xã_hội(mạng_xã_hội)
            tổng_điểm_mua += m_mua * 0.2
            tổng_điểm_bán += m_bán * 0.2
            tất_cả_tín_hiệu.extend(m_tín_hiệu)
            tất_cả_cảnh_báo.extend(m_cảnh_báo)

            t_mua, t_bán, t_tín_hiệu, t_cảnh_báo = chấm_điểm_tác_động_tin_tức(tin_tức)
            tổng_điểm_mua += t_mua * 0.25
            tổng_điểm_bán += t_bán * 0.25
            tất_cả_tín_hiệu.extend(t_tín_hiệu)
            tất_cả_cảnh_báo.extend(t_cảnh_báo)

            v_mua, v_bán, v_hệ_số, v_cảnh_báo = chấm_điểm_môi_trường_vĩ_mô(vĩ_mô)
            tổng_điểm_mua += v_mua * 0.2
            tổng_điểm_bán += v_bán * 0.2
            hệ_số_kích_thước *= v_hệ_số
            tất_cả_cảnh_báo.extend(v_cảnh_báo)

            if fear_greed is not None:
                fg_mua, fg_ban, fg_tín_hiệu = chấm_điểm_fear_greed(fear_greed)
                tổng_điểm_mua += fg_mua * 0.05
                tổng_điểm_bán += fg_ban * 0.05
                tất_cả_tín_hiệu.extend(fg_tín_hiệu)

            if tvl_defi is not None:
                defi_mua, defi_ban, defi_tín_hiệu = chấm_điểm_tvl_defi(tvl_defi)
                tổng_điểm_mua += defi_mua * 0.05
                tổng_điểm_bán += defi_ban * 0.05
                tất_cả_tín_hiệu.extend(defi_tín_hiệu)

            điểm_ròng = tổng_điểm_mua - tổng_điểm_bán
            hệ_số_vị_thế = max(0.1, min(2.0, hệ_số_kích_thước))

            if abs(điểm_ròng) >= 3.0:
                độ_tin_cậy = "CAO"
            elif abs(điểm_ròng) >= 1.5:
                độ_tin_cậy = "TRUNG_BÌNH"
            else:
                độ_tin_cậy = "THẤP"

            if điểm_ròng >= mức_điểm_ròng:
                tín_hiệu_chính = "MUA"
            elif điểm_ròng <= -mức_điểm_ròng:
                tín_hiệu_chính = "BÁN"
            else:
                tín_hiệu_chính = "TRUNG_LẬP"

            kết_quả.append(KếtQuảTínHiệu(
                mã=mã,
                điểm_mua=round(tổng_điểm_mua, 2),
                điểm_bán=round(tổng_điểm_bán, 2),
                điểm_ròng=round(điểm_ròng, 2),
                hệ_số_kích_thước_vị_thế=round(hệ_số_vị_thế, 2),
                độ_tin_cậy=độ_tin_cậy,
                tín_hiệu_chính=tín_hiệu_chính,
                cảnh_báo=tất_cả_cảnh_báo,
                tín_hiệu=tất_cả_tín_hiệu,
                thành_phần=thành_phần
            ))

    df = pd.DataFrame([asdict(kq) for kq in kết_quả])
    st.session_state["kq_df"] = df
    st.success("✅ Hoàn tất! Vào các trang bên trái để xem chi tiết.")
