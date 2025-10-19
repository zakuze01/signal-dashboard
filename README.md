
# 📊 Crypto Signal Dashboard (Streamlit)

Một dashboard mạnh mẽ dùng để phân tích tín hiệu MUA/BÁN cho thị trường crypto, sử dụng:
- Dữ liệu mạng xã hội (LunarCrush)
- Tin tức (NewsAPI, CryptoPanic)
- Chỉ số vĩ mô (FRED)
- Tâm lý thị trường (Fear & Greed Index)
- TVL DeFi (DefiLlama)
- Phân tích kỹ thuật và thống kê

## 🚀 Triển khai online (miễn phí)
Bạn có thể deploy trực tiếp bằng Streamlit Cloud:

1. Fork repo này hoặc tải source lên GitHub
2. Vào [https://streamlit.io/cloud](https://streamlit.io/cloud)
3. Bấm "New App", chọn file `Home.py`
4. Deploy và chia sẻ link công khai

## 📁 Cấu trúc dự án

```
.
├── Home.py                    # Trang chính - chạy phân tích
├── alpha_signal_checker_plus.py  # Core logic
├── requirements.txt           # Thư viện cần cài
├── pages/
│   ├── 1_Sentiment_Detail.py
│   ├── 2_Trade_Suggestions.py
│   └── 3_Advanced_Stats.py
```

## 🧪 Yêu cầu môi trường

- Python 3.8+
- Cài thư viện:
```bash
pip install -r requirements.txt
```

---

*Dự án demo bởi AI Code Generator*
