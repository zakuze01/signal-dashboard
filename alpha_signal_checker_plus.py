# -*- coding: utf-8 -*-
"""
Trình Phân Tích Tín Hiệu Crypto
--------------------
Pipeline tối ưu để chấm điểm XU HƯỚNG MUA/BÁN sử dụng các nguồn dữ liệu ưu tiên:
- Tâm lý Mạng Xã Hội (LunarCrush) - Quan trọng (+20% tín hiệu)
- Phân Tích Tin Tức (CryptoPanic/NewsAPI) - Quan trọng (+25% tín hiệu)  
- Lịch Sử Hợp Đồng Tương Lai - Quan trọng (+30% tín hiệu)
- Chỉ Số Kinh Tế Vĩ Mô - Quan trọng (+20% tín hiệu)

Dữ liệu được lấy từ file JSON đầu vào với thông tin coin.
"""

import os
import json
import argparse
from dataclasses import dataclass, asdict, field
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta

CẤU_HÌNH = {
    "LUNARCRUSH_API_KEY": os.getenv("LUNARCRUSH_API_KEY", ""),
    "LUNARCRUSH_BASE": "https://lunarcrush.com/api3/",
    "CRYPTOPANIC_TOKEN": os.getenv("CRYPTOPANIC_TOKEN", ""),
    "CRYPTOPANIC_BASE": "https://cryptopanic.com/api/v1/",
    "NEWSAPI_KEY": os.getenv("NEWSAPI_KEY", ""),
    "NEWSAPI_BASE": "https://newsapi.org/v2/everything",
    "FRED_API_KEY": os.getenv("FRED_API_KEY", ""),
    "FRED_BASE": "https://api.stlouisfed.org/fred/series/observations",
    "OUTPUT_JSON": "./ket_qua_tin_hieu_chi_tiet.json",
}

@dataclass
class TâmLýMạngXãHội:
    lượt_nhắc_twitter: int = 0
    tâm_lý_twitter: float = 0.0
    bài_đăng_reddit: int = 0
    tâm_lý_reddit: float = 0.0
    thay_đổi_tâm_lý_24h: float = 0.0
    tâm_lý_influencer: float = 0.0
    điểm_galaxy: float = 0.0
    xếp_hạng_alt: int = 0
    lượng_tương_tác_xã_hội: int = 0
    mức_độ_tương_tác: float = 0.0

@dataclass
class TácĐộngTinTức:
    tin_nóng: List[Dict[str, Any]] = field(default_factory=list)
    lượng_tin_24h: int = 0
    tâm_lý_tin_tức_trung_bình: float = 0.0
    số_tin_tích_cực: int = 0
    số_tin_tiêu_cực: int = 0
    số_tin_trung_tính: int = 0
    tin_tác_động_cao: int = 0

@dataclass
class DữLiệuHợpĐồngTươngLai:
    mã: str
    dòng_tiền_ròng_24h: float = 0.0
    dòng_tiền_ròng_7ngày: float = 0.0
    dòng_tiền_ròng_30ngày: float = 0.0
    tiền_gửi_24h: float = 0.0
    tiền_rút_24h: float = 0.0
    tâm_lý_thị_trường: str = "TRUNG_LẬP"
    khối_lượng_cân_bằng: float = 0.0
    # Các chỉ số phái sinh
    xu_hướng_dòng_tiền: str = "TRUNG_LẬP"
    đà_dòng_tiền: float = 0.0

@dataclass
class ChỉSốKinhTếVĩMô:
    vix_hiện_tại: float = 0.0
    xu_hướng_vix: str = "TRUNG_LẬP"
    dxy_hiện_tại: float = 0.0
    xu_hướng_dxy: str = "TRUNG_LẬP"
    lợi_suất_trái_phiếu_mỹ_10năm: float = 0.0
    xu_hướng_lợi_suất: str = "TRUNG_LẬP"
    thay_đổi_sp500: float = 0.0
    thay_đổi_nasdaq: float = 0.0
    mức_độ_chấp_nhận_rủi_ro: str = "TRUNG_LẬP"
    tương_quan_crypto: float = 0.0

@dataclass
class KếtQuảTínHiệu:
    mã: str
    điểm_mua: float
    điểm_bán: float
    điểm_ròng: float
    hệ_số_kích_thước_vị_thế: float
    độ_tin_cậy: str
    tín_hiệu_chính: str
    cảnh_báo: List[str] = field(default_factory=list)
    tín_hiệu: List[str] = field(default_factory=list)
    thành_phần: Dict[str, Any] = field(default_factory=dict)

def _yêu_cầu_an_toàn(url: str, tham_số: Dict[str, Any] = None, headers: Dict[str, str] = None, thời_gian_chờ: int = 10) -> Optional[Dict[str, Any]]:
    """Yêu cầu API an toàn với xử lý lỗi"""
    try:
        import requests
        phản_hồi = requests.get(url, params=tham_số, headers=headers, timeout=thời_gian_chờ)
        if phản_hồi.status_code == 200:
            return phản_hồi.json()
        return None
    except Exception as e:
        print(f"Lỗi yêu cầu API: {e}")
        return None

# ========== TRÌNH LẤY DỮ LIỆU NÂNG CAO ==========

def lấy_tâm_lý_mạng_xã_hội(mã: str) -> TâmLýMạngXãHội:
    """Lấy dữ liệu tâm lý mạng xã hội từ LunarCrush với các chỉ số nâng cao"""
    tâm_lý = TâmLýMạngXãHội()
    
    if not CẤU_HÌNH["LUNARCRUSH_API_KEY"]:
        # Dữ liệu mẫu để minh họa
        tâm_lý.lượt_nhắc_twitter = 1500
        tâm_lý.tâm_lý_twitter = 0.65
        tâm_lý.bài_đăng_reddit = 320
        tâm_lý.tâm_lý_reddit = 0.58
        tâm_lý.thay_đổi_tâm_lý_24h = 0.12
        tâm_lý.tâm_lý_influencer = 0.72
        tâm_lý.điểm_galaxy = 68.5
        tâm_lý.xếp_hạng_alt = 45
        tâm_lý.lượng_tương_tác_xã_hội = 1820
        tâm_lý.mức_độ_tương_tác = 0.85
        return tâm_lý
    
    # TODO: Triển khai các lệnh gọi API LunarCrush thực tế
    return tâm_lý

def lấy_tác_động_tin_tức(mã: str) -> TácĐộngTinTức:
    """Lấy tác động tin tức với phân tích tâm lý"""
    tin_tức = TácĐộngTinTức()
    
    if not CẤU_HÌNH["CRYPTOPANIC_TOKEN"] and not CẤU_HÌNH["NEWSAPI_KEY"]:
        # Dữ liệu mẫu để minh họa
        tin_tức.lượng_tin_24h = 25
        tin_tức.tâm_lý_tin_tức_trung_bình = 0.42
        tin_tức.số_tin_tích_cực = 8
        tin_tức.số_tin_tiêu_cực = 5
        tin_tức.số_tin_trung_tính = 12
        tin_tức.tin_tác_động_cao = 3
        
        # Tin nóng mẫu
        tin_tức.tin_nóng = [
            {"tiêu_đề": f"Đối tác lớn được công bố cho {mã}", "tâm_lý": 0.8, "tác_động": 8},
            {"tiêu_đề": f"Lo ngại quy định cho {mã}", "tâm_lý": -0.6, "tác_động": 7},
        ]
        return tin_tức
    
    # TODO: Triển khai tích hợp CryptoPanic/NewsAPI
    return tin_tức

def phân_tích_dữ_liệu_hợp_đồng_tương_lai(dữ_liệu_đầu_vào: List[Dict]) -> Dict[str, DữLiệuHợpĐồngTươngLai]:
    """Phân tích dữ liệu hợp đồng tương lai từ JSON đầu vào"""
    bản_đồ_hợp_đồng = {}
    
    for mục in dữ_liệu_đầu_vào:
        mã = trích_xuất_mã_từ_cặp(mục.get("p", ""))
        if not mã:
            continue
            
        dữ_liệu_hợp_đồng = DữLiệuHợpĐồngTươngLai(mã=mã)
        
        # Phân tích dữ liệu dòng tiền
        dữ_liệu_sm = mục.get("sm", {})
        dữ_liệu_hợp_đồng.dòng_tiền_ròng_24h = dữ_liệu_sm.get("24h", 0)
        dữ_liệu_hợp_đồng.dòng_tiền_ròng_7ngày = dữ_liệu_sm.get("7d", 0)
        dữ_liệu_hợp_đồng.dòng_tiền_ròng_30ngày = dữ_liệu_sm.get("30d", 0)
        
        # Phân tích dữ liệu tiền gửi/rút
        dữ_liệu_cin = mục.get("cin", {})
        dữ_liệu_cout = mục.get("cout", {})
        dữ_liệu_hợp_đồng.tiền_gửi_24h = dữ_liệu_cin.get("24h", 0)
        dữ_liệu_hợp_đồng.tiền_rút_24h = dữ_liệu_cout.get("24h", 0)
        
        # Phân tích tâm lý thị trường
        dữ_liệu_st = mục.get("st", {})
        dữ_liệu_hợp_đồng.tâm_lý_thị_trường = dữ_liệu_st.get("24h", "TRUNG_LẬP").upper()
        
        # Phân tích khối lượng cân bằng
        dữ_liệu_bv = mục.get("bv", {})
        dữ_liệu_hợp_đồng.khối_lượng_cân_bằng = dữ_liệu_bv.get("24h", 0)
        
        # Tính toán các chỉ số phái sinh
        dữ_liệu_hợp_đồng.đà_dòng_tiền = tính_đà_dòng_tiền(dữ_liệu_hợp_đồng)
        dữ_liệu_hợp_đồng.xu_hướng_dòng_tiền = xác_định_xu_hướng_dòng_tiền(dữ_liệu_hợp_đồng)
        
        bản_đồ_hợp_đồng[mã] = dữ_liệu_hợp_đồng
    
    return bản_đồ_hợp_đồng

def trích_xuất_mã_từ_cặp(chuỗi_cặp: str) -> str:
    """Trích xuất mã gốc từ chuỗi cặp như 'OHM-USDT-PERP@ethereum'"""
    if not chuỗi_cặp:
        return ""
    
    # Loại bỏ mọi thứ sau @
    cặp_gốc = chuỗi_cặp.split('@')[0]
    
    # Loại bỏ hậu tố -USDT-PERP hoặc tương tự
    for hậu_tố in ['-USDT-PERP', '-PERP', '-USDT']:
        if cặp_gốc.endswith(hậu_tố):
            return cặp_gốc[:-len(hậu_tố)]
    
    return cặp_gốc

def tính_đà_dòng_tiền(dữ_liệu_hợp_đồng: DữLiệuHợpĐồngTươngLai) -> float:
    """Tính điểm đà dòng tiền"""
    if dữ_liệu_hợp_đồng.dòng_tiền_ròng_7ngày == 0:
        return 0.0
    
    # So sánh dòng tiền 24h với dòng tiền trung bình hàng ngày 7 ngày
    trung_bình_hàng_ngày_7ngày = dữ_liệu_hợp_đồng.dòng_tiền_ròng_7ngày / 7
    if trung_bình_hàng_ngày_7ngày == 0:
        return 0.0
    
    đà = (dữ_liệu_hợp_đồng.dòng_tiền_ròng_24h / trung_bình_hàng_ngày_7ngày) - 1
    return round(đà, 3)

def xác_định_xu_hướng_dòng_tiền(dữ_liệu_hợp_đồng: DữLiệuHợpĐồngTươngLai) -> str:
    """Xác định xu hướng dòng tiền dựa trên nhiều khung thời gian"""
    if dữ_liệu_hợp_đồng.dòng_tiền_ròng_24h > 0 and dữ_liệu_hợp_đồng.đà_dòng_tiền > 0.1:
        return "DÒNG_VÀO_MẠNH"
    elif dữ_liệu_hợp_đồng.dòng_tiền_ròng_24h > 0:
        return "DÒNG_VÀO"
    elif dữ_liệu_hợp_đồng.dòng_tiền_ròng_24h < 0 and dữ_liệu_hợp_đồng.đà_dòng_tiền < -0.1:
        return "DÒNG_RA_MẠNH"
    elif dữ_liệu_hợp_đồng.dòng_tiền_ròng_24h < 0:
        return "DÒNG_RA"
    else:
        return "TRUNG_LẬP"

def lấy_chỉ_số_kinh_tế_vĩ_mô() -> ChỉSốKinhTếVĩMô:
    """Lấy chỉ số kinh tế vĩ mô"""
    vĩ_mô = ChỉSốKinhTếVĩMô()
    
    if not CẤU_HÌNH["FRED_API_KEY"]:
        # Dữ liệu mẫu để minh họa
        vĩ_mô.vix_hiện_tại = 18.5
        vĩ_mô.xu_hướng_vix = "GIẢM"
        vĩ_mô.dxy_hiện_tại = 103.2
        vĩ_mô.xu_hướng_dxy = "TRUNG_LẬP"
        vĩ_mô.lợi_suất_trái_phiếu_mỹ_10năm = 4.25
        vĩ_mô.xu_hướng_lợi_suất = "TĂNG"
        vĩ_mô.thay_đổi_sp500 = 0.8
        vĩ_mô.thay_đổi_nasdaq = 1.2
        vĩ_mô.mức_độ_chấp_nhận_rủi_ro = "TRUNG_BÌNH"
        vĩ_mô.tương_quan_crypto = 0.65
        return vĩ_mô
    
    # TODO: Triển khai tích hợp API FRED
    return vĩ_mô

# ========== BỘ CHẤM ĐIỂM NÂNG CAO ==========

def chấm_điểm_tâm_lý_mạng_xã_hội(tâm_lý: TâmLýMạngXãHội) -> Tuple[float, float, List[str], List[str]]:
    """Chấm điểm tâm lý mạng xã hội với trọng số tác động 20%"""
    điểm_mua, điểm_bán = 0.0, 0.0
    tín_hiệu, cảnh_báo = [], []
    
    # Trọng số điểm Galaxy (0-100, cao hơn là tốt hơn)
    if tâm_lý.điểm_galaxy >= 70:
        điểm_mua += 1.5
        tín_hiệu.append("Điểm Galaxy cao → tương tác cộng đồng mạnh")
    elif tâm_lý.điểm_galaxy <= 30:
        điểm_bán += 1.0
        cảnh_báo.append("Điểm Galaxy thấp → hiện diện mạng xã hội yếu")
    
    # Trọng số xếp hạng Alt (thấp hơn là tốt hơn)
    if tâm_lý.xếp_hạng_alt <= 50:
        điểm_mua += 1.0
        tín_hiệu.append(f"AltRank tốt #{tâm_lý.xếp_hạng_alt} → tài sản đang hot")
    elif tâm_lý.xếp_hạng_alt >= 200:
        điểm_bán += 0.5
        cảnh_báo.append(f"AltRank kém #{tâm_lý.xếp_hạng_alt} → ít tương tác xã hội")
    
    # Đà tâm lý
    if tâm_lý.thay_đổi_tâm_lý_24h > 0.15:
        điểm_mua += 1.0
        tín_hiệu.append("Cải thiện tâm lý nhanh → đà đang hình thành")
    elif tâm_lý.thay_đổi_tâm_lý_24h < -0.15:
        điểm_bán += 1.0
        cảnh_báo.append("Tâm lý đang xấu đi → khuyến cáo thận trọng")
    
    # Điểm tổng hợp mạng xã hội
    tổng_hợp_mạng_xã_hội = (
        tâm_lý.tâm_lý_twitter * 0.4 +
        tâm_lý.tâm_lý_reddit * 0.3 +
        tâm_lý.tâm_lý_influencer * 0.3
    )
    
    if tổng_hợp_mạng_xã_hội > 0.6:
        điểm_mua += 1.5
    elif tổng_hợp_mạng_xã_hội < 0.4:
        điểm_bán += 1.0
    
    return điểm_mua, điểm_bán, tín_hiệu, cảnh_báo

def chấm_điểm_tác_động_tin_tức(tin_tức: TácĐộngTinTức) -> Tuple[float, float, List[str], List[str]]:
    """Chấm điểm tác động tin tức với trọng số tác động 25%"""
    điểm_mua, điểm_bán = 0.0, 0.0
    tín_hiệu, cảnh_báo = [], []
    
    # Chấm điểm tâm lý tin tức
    if tin_tức.tâm_lý_tin_tức_trung_bình > 0.6:
        điểm_mua += 2.0
        tín_hiệu.append("Tâm lý tin tức tích cực mạnh → chất xúc tác tăng giá")
    elif tin_tức.tâm_lý_tin_tức_trung_bình < 0.3:
        điểm_bán += 1.5
        cảnh_báo.append("Tâm lý tin tức tiêu cực → áp lực giảm giá")
    
    # Phân tích tin tác động cao
    if tin_tức.tin_tác_động_cao >= 2:
        if tin_tức.số_tin_tích_cực > tin_tức.số_tin_tiêu_cực:
            điểm_mua += 1.5
            tín_hiệu.append("Nhiều sự kiện tin tức tích cực tác động cao")
        else:
            điểm_bán += 1.0
            cảnh_báo.append("Nhiều sự kiện tin tức tiêu cực tác động cao")
    
    # Phân tích lượng tin
    if tin_tức.lượng_tin_24h > 50:
        điểm_mua += 0.5  # Sự chú ý cao thường tích cực cho crypto
        tín_hiệu.append("Lượng tin cao → tăng sự chú ý của thị trường")
    
    # Tác động ngay lập tức của tin nóng
    for tin_nóng in tin_tức.tin_nóng[:3]:  # 3 tin nóng hàng đầu
        tác_động = tin_nóng.get("tác_động", 0)
        tâm_lý = tin_nóng.get("tâm_lý", 0)
        
        if tác_động >= 7 and tâm_lý > 0.5:
            điểm_mua += 1.0
        elif tác_động >= 7 and tâm_lý < -0.3:
            điểm_bán += 1.0
    
    return điểm_mua, điểm_bán, tín_hiệu, cảnh_báo

def chấm_điểm_dữ_liệu_hợp_đồng_tương_lai(hợp_đồng: DữLiệuHợpĐồngTươngLai) -> Tuple[float, float, List[str], List[str]]:
    """Chấm điểm dữ liệu hợp đồng tương lai với trọng số tác động 30%"""
    điểm_mua, điểm_bán = 0.0, 0.0
    tín_hiệu, cảnh_báo = [], []
    
    # Phân tích xu hướng dòng tiền
    if hợp_đồng.xu_hướng_dòng_tiền == "DÒNG_VÀO_MẠNH":
        điểm_mua += 2.5
        tín_hiệu.append("Xu hướng dòng vào mạnh → vốn đang vào thị trường")
    elif hợp_đồng.xu_hướng_dòng_tiền == "DÒNG_VÀO":
        điểm_mua += 1.5
        tín_hiệu.append("Dòng vào tích cực → dòng vốn tăng giá")
    elif hợp_đồng.xu_hướng_dòng_tiền == "DÒNG_RA_MẠNH":
        điểm_bán += 2.0
        cảnh_báo.append("Dòng ra mạnh → vốn rời khỏi thị trường")
    elif hợp_đồng.xu_hướng_dòng_tiền == "DÒNG_RA":
        điểm_bán += 1.0
        cảnh_báo.append("Dòng ra tiêu cực → dòng vốn giảm giá")
    
    # Phân tích đà dòng tiền
    if hợp_đồng.đà_dòng_tiền > 0.2:
        điểm_mua += 1.0
        tín_hiệu.append("Dòng vào tăng tốc → đà đang hình thành")
    elif hợp_đồng.đà_dòng_tiền < -0.2:
        điểm_bán += 1.0
        cảnh_báo.append("Dòng ra tăng tốc → đà đang xấu đi")
    
    # Sự phù hợp với tâm lý thị trường
    if hợp_đồng.tâm_lý_thị_trường == "BULL" and hợp_đồng.xu_hướng_dòng_tiền in ["DÒNG_VÀO", "DÒNG_VÀO_MẠNH"]:
        điểm_mua += 1.0
        tín_hiệu.append("Tâm lý tăng giá + dòng vào → xác nhận mạnh")
    elif hợp_đồng.tâm_lý_thị_trường == "BEAR" and hợp_đồng.xu_hướng_dòng_tiền in ["DÒNG_RA", "DÒNG_RA_MẠNH"]:
        điểm_bán += 1.0
        cảnh_báo.append("Tâm lý giảm giá + dòng ra → xác nhận mạnh")
    
    # Ý nghĩa khối lượng cân bằng
    if hợp_đồng.khối_lượng_cân_bằng > 1000000:  # Khối lượng cân bằng trên $1M
        if hợp_đồng.dòng_tiền_ròng_24h > 0:
            điểm_mua += 0.5
        else:
            điểm_bán += 0.5
    
    return điểm_mua, điểm_bán, tín_hiệu, cảnh_báo

def chấm_điểm_môi_trường_vĩ_mô(vĩ_mô: ChỉSốKinhTếVĩMô) -> Tuple[float, float, float, List[str]]:
    """Chấm điểm môi trường vĩ mô với trọng số tác động 20%"""
    điểm_mua, điểm_bán = 0.0, 0.0
    hệ_số_kích_thước = 1.0
    cảnh_báo = []
    
    # Phân tích VIX (chỉ số sợ hãi)
    if vĩ_mô.vix_hiện_tại > 25 and vĩ_mô.xu_hướng_vix == "TĂNG":
        điểm_bán += 1.5
        hệ_số_kích_thước *= 0.7
        cảnh_báo.append("VIX cao & đang tăng → môi trường rủi ro")
    elif vĩ_mô.vix_hiện_tại < 15 and vĩ_mô.xu_hướng_vix == "GIẢM":
        điểm_mua += 1.0
        tín_hiệu.append("VIX thấp & đang giảm → môi trường chấp nhận rủi ro")
    
    # Phân tích DXY (sức mạnh đồng USD)
    if vĩ_mô.dxy_hiện_tại > 105 and vĩ_mô.xu_hướng_dxy == "TĂNG":
        điểm_bán += 1.5
        hệ_số_kích_thước *= 0.8
        cảnh_báo.append("USD mạnh & đang tăng → đầu gió ngược crypto")
    elif vĩ_mô.dxy_hiện_tại < 100 and vĩ_mô.xu_hướng_dxy == "GIẢM":
        điểm_mua += 1.0
        tín_hiệu.append("USD yếu & đang giảm → đầu gió thuận crypto")
    
    # Phân tích lợi suất
    if vĩ_mô.lợi_suất_trái_phiếu_mỹ_10năm > 4.5 and vĩ_mô.xu_hướng_lợi_suất == "TĂNG":
        điểm_bán += 1.0
        cảnh_báo.append("Lợi suất cao & đang tăng → áp lực cạnh tranh")
    
    # Tương quan thị trường chứng khoán
    if vĩ_mô.thay_đổi_sp500 > 1.0 and vĩ_mô.thay_đổi_nasdaq > 1.5:
        điểm_mua += 1.0
        tín_hiệu.append("Hiệu suất cổ phiếu mạnh → tương quan tích cực")
    elif vĩ_mô.thay_đổi_sp500 < -1.0 and vĩ_mô.thay_đổi_nasdaq < -1.5:
        điểm_bán += 0.5
        cảnh_báo.append("Hiệu suất cổ phiếu yếu → tương quan tiêu cực")
    
    # Điều chỉnh chế độ rủi ro
    if vĩ_mô.mức_độ_chấp_nhận_rủi_ro == "CAO":
        hệ_số_kích_thước *= 1.2
    elif vĩ_mô.mức_độ_chấp_nhận_rủi_ro == "THẤP":
        hệ_số_kích_thước *= 0.8
    
    return điểm_mua, điểm_bán, hệ_số_kích_thước, cảnh_báo

# ========== PIPELINE PHÂN TÍCH CHÍNH ==========

def phân_tích_mã(mã: str, dữ_liệu_hợp_đồng: Dict[str, DữLiệuHợpĐồngTươngLai], 
                  điểm_ròng_tối_thiểu: float = 2.0) -> KếtQuảTínHiệu:
    """Pipeline phân tích nâng cao cho một mã"""
    
    thành_phần = {}
    
    # Lấy tất cả nguồn dữ liệu
    mạng_xã_hội = lấy_tâm_lý_mạng_xã_hội(mã)
    tin_tức = lấy_tác_động_tin_tức(mã)
    hợp_đồng = dữ_liệu_hợp_đồng.get(mã, DữLiệuHợpĐồngTươngLai(mã=mã))
    vĩ_mô = lấy_chỉ_số_kinh_tế_vĩ_mô()
    
    thành_phần["mạng_xã_hội"] = asdict(mạng_xã_hội)
    thành_phần["tin_tức"] = asdict(tin_tức)
    thành_phần["hợp_đồng"] = asdict(hợp_đồng)
    thành_phần["vĩ_mô"] = asdict(vĩ_mô)
    
    # Khởi tạo chấm điểm
    tổng_điểm_mua, tổng_điểm_bán = 0.0, 0.0
    tất_cả_tín_hiệu, tất_cả_cảnh_báo = [], []
    hệ_số_kích_thước = 1.0
    
    # Áp dụng chấm điểm với trọng số ưu tiên
    # Mạng xã hội: 20%
    m_mua, m_bán, m_tín_hiệu, m_cảnh_báo = chấm_điểm_tâm_lý_mạng_xã_hội(mạng_xã_hội)
    tổng_điểm_mua += m_mua * 0.2
    tổng_điểm_bán += m_bán * 0.2
    tất_cả_tín_hiệu.extend(m_tín_hiệu)
    tất_cả_cảnh_báo.extend(m_cảnh_báo)
    
    # Tin tức: 25%
    t_mua, t_bán, t_tín_hiệu, t_cảnh_báo = chấm_điểm_tác_động_tin_tức(tin_tức)
    tổng_điểm_mua += t_mua * 0.25
    tổng_điểm_bán += t_bán * 0.25
    tất_cả_tín_hiệu.extend(t_tín_hiệu)
    tất_cả_cảnh_báo.extend(t_cảnh_báo)
    
    # Hợp đồng tương lai: 30%
    h_mua, h_bán, h_tín_hiệu, h_cảnh_báo = chấm_điểm_dữ_liệu_hợp_đồng_tương_lai(hợp_đồng)
    tổng_điểm_mua += h_mua * 0.3
    tổng_điểm_bán += h_bán * 0.3
    tất_cả_tín_hiệu.extend(h_tín_hiệu)
    tất_cả_cảnh_báo.extend(h_cảnh_báo)
    
    # Vĩ mô: 20% + điều chỉnh kích thước
    v_mua, v_bán, v_hệ_số, v_cảnh_báo = chấm_điểm_môi_trường_vĩ_mô(vĩ_mô)
    tổng_điểm_mua += v_mua * 0.2
    tổng_điểm_bán += v_bán * 0.2
    hệ_số_kích_thước *= v_hệ_số
    tất_cả_cảnh_báo.extend(v_cảnh_báo)
    
    # Tính điểm cuối cùng
    điểm_ròng = tổng_điểm_mua - tổng_điểm_bán
    hệ_số_vị_thế = max(0.1, min(2.0, hệ_số_kích_thước))
    
    # Xác định độ tin cậy và tín hiệu chính
    if abs(điểm_ròng) >= 3.0:
        độ_tin_cậy = "CAO"
    elif abs(điểm_ròng) >= 1.5:
        độ_tin_cậy = "TRUNG_BÌNH"
    else:
        độ_tin_cậy = "THẤP"
    
    if điểm_ròng >= điểm_ròng_tối_thiểu:
        tín_hiệu_chính = "MUA"
    elif điểm_ròng <= -điểm_ròng_tối_thiểu:
        tín_hiệu_chính = "BÁN"
    else:
        tín_hiệu_chính = "TRUNG_LẬP"
    
    return KếtQuảTínHiệu(
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
    )

def main():
    parser = argparse.ArgumentParser(description="Trình Phân Tích Tín Hiệu Crypto Nâng Cao")
    parser.add_argument("--file-đầu-vào", type=str, default="input_data_long.json", help="File JSON đầu vào với dữ liệu coin (mặc định: input_data_long.json)")
    parser.add_argument("--điểm-ròng-tối-thiểu", type=float, default=2.0, help="Điểm ròng tối thiểu cho tín hiệu")
    parser.add_argument("--file-đầu-ra", type=str, default=CẤU_HÌNH["OUTPUT_JSON"], help="File JSON đầu ra")
    
    args = parser.parse_args()
    
    # Tải dữ liệu đầu vào
    try:
        with open(args.file_đầu_vào, 'r', encoding='utf-8') as f:
            dữ_liệu_đầu_vào = json.load(f)
    except Exception as e:
        print(f"Lỗi tải file đầu vào: {e}")
        return
    
    # Phân tích dữ liệu hợp đồng tương lai
    dữ_liệu_hợp_đồng = phân_tích_dữ_liệu_hợp_đồng_tương_lai(dữ_liệu_đầu_vào)
    các_mã = list(dữ_liệu_hợp_đồng.keys())
    
    if not các_mã:
        print("Không tìm thấy mã hợp lệ trong dữ liệu đầu vào")
        return
    
    print("=" * 120)
    print(f"{'Mã':<12} {'Mua':>6} {'Bán':>6} {'Ròng':>6} {'Kích thước':>10} {'Tin cậy':>10} {'Tín hiệu':>10} | Tín hiệu hàng đầu")
    print("-" * 120)
    
    kết_quả = []
    for mã in các_mã:
        kết_quả_mã = phân_tích_mã(mã, dữ_liệu_hợp_đồng, args.điểm_ròng_tối_thiểu)
        kết_quả.append(kết_quả_mã)
        
        # Hiển thị tóm tắt
        tín_hiệu_hàng_đầu = kết_quả_mã.tín_hiệu[0] if kết_quả_mã.tín_hiệu else "Không có tín hiệu"
        print(f"{kết_quả_mã.mã:<12} {kết_quả_mã.điểm_mua:>6.2f} {kết_quả_mã.điểm_bán:>6.2f} {kết_quả_mã.điểm_ròng:>6.2f} "
              f"{kết_quả_mã.hệ_số_kích_thước_vị_thế:>10.2f} {kết_quả_mã.độ_tin_cậy:>10} {kết_quả_mã.tín_hiệu_chính:>10} | {tín_hiệu_hàng_đầu}")
    
    print("=" * 120)
    
    # Lưu kết quả chi tiết
    dữ_liệu_đầu_ra = [asdict(kq) for kq in kết_quả]
    with open(args.file_đầu_ra, 'w', encoding='utf-8') as f:
        json.dump(dữ_liệu_đầu_ra, f, ensure_ascii=False, indent=2)
    
    print(f"Kết quả chi tiết đã lưu vào: {args.file_đầu_ra}")
    
    # Tạo đề xuất giao dịch
    print("\n" + "=" * 70)
    print("ĐỀ XUẤT GIAO DỊCH")
    print("=" * 70)
    
    mua_mạnh = [kq for kq in kết_quả if kq.tín_hiệu_chính == "MUA" and kq.độ_tin_cậy == "CAO"]
    bán_mạnh = [kq for kq in kết_quả if kq.tín_hiệu_chính == "BÁN" and kq.độ_tin_cậy == "CAO"]
    
    if mua_mạnh:
        print(f"\n🔴 TÍN HIỆU MUA MẠNH ({len(mua_mạnh)}):")
        for đề_xuất in sorted(mua_mạnh, key=lambda x: x.điểm_ròng, reverse=True)[:5]:
            print(f"   {đề_xuất.mã}: Điểm ròng {đề_xuất.điểm_ròng:.2f}, Hệ số kích thước {đề_xuất.hệ_số_kích_thước_vị_thế:.2f}x")
    
    if bán_mạnh:
        print(f"\n🔵 TÍN HIỆU BÁN MẠNH ({len(bán_mạnh)}):")
        for đề_xuất in sorted(bán_mạnh, key=lambda x: x.điểm_ròng)[:5]:
            print(f"   {đề_xuất.mã}: Điểm ròng {đề_xuất.điểm_ròng:.2f}, Hệ số kích thước {đề_xuất.hệ_số_kích_thước_vị_thế:.2f}x")

if __name__ == "__main__":
    main()