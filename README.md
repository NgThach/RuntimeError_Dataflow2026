# 🛡️ NASA AI-Ops Control Center (DataFlow 2026)

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.31.0-FF4B4B)
![Plotly](https://img.shields.io/badge/Plotly-Graphing-3F4F75)
![Status](https://img.shields.io/badge/Status-Prototype-green)

> **Dự án mô phỏng hệ thống Auto-scaling thông minh sử dụng AI (LightGBM) để tối ưu hóa tài nguyên đám mây và giảm thiểu rủi ro vận hành.**

---

## 📖 Giới thiệu (Overview)

Trong kỷ nguyên Cloud Computing, việc cân bằng giữa **Hiệu năng (Performance)** và **Chi phí (Cost)** là bài toán nan giải.
* **Static Provisioning (Cấp phát tĩnh):** Gây lãng phí tài nguyên khổng lồ vào giờ thấp điểm.
* **Reactive Scaling (Scaling phản ứng):** Chậm trễ, dẫn đến sập hệ thống (Downtime) khi có traffic tăng đột biến (Spike).

**NASA AI-Ops Control Center** giải quyết vấn đề này bằng cách tiếp cận **Proactive (Chủ động)**: Sử dụng AI để dự báo lưu lượng và chuẩn bị tài nguyên trước khi sự cố xảy ra.

---

## 🚀 Tính năng nổi bật (Key Features)

### 1. 🧠 AI Forecasting Core
* Sử dụng thuật toán **LightGBM** để dự báo Traffic (Request & Bytes) theo chuỗi thời gian.
* Độ chính xác cao với **MAPE ~5%** (Mức "Xuất sắc" theo thang đo Lewis).
* Hỗ trợ đa khung thời gian: 1 phút, 5 phút, 15 phút.

### 2. 🛡️ Hybrid Scaling Strategy
* Kết hợp linh hoạt giữa **Request-based** và **Bytes-based**.
* Tích hợp cơ chế **Safety Buffer** (Vùng đệm an toàn) để chống lại các đợt DDoS hoặc Flash Crowd.
* Cơ chế **Cooldown** thông minh giúp chống hiện tượng Flapping (Bật/Tắt server liên tục).

### 3. 💰 ROI & Economics Analysis
* So sánh trực quan chi phí giữa phương án Thuê bao truyền thống và AI-Ops.
* Tính toán số tiền tiết kiệm được thực tế dựa trên **Unit Cost** (Đơn giá/giờ).

### 4. 🎮 Interactive Simulator
* Giao diện **Streamlit** trực quan, cho phép chạy mô phỏng "Live" quá trình Scaling.
* Biểu đồ động hiển thị tương quan giữa: `Load` (Tải thực) vs `Capacity` (Năng lực hệ thống).

---

## 📂 Cấu trúc dự án (Project Structure)

```bash
RuntimeError_Dataflow2026/
├── app.py                  # Source code chính (Streamlit App)
├── autoscale_config.yaml   # File cấu hình tham số (Threshold, Cost, Cooldown)
├── requirements.txt        # Danh sách thư viện phụ thuộc
├── data/
│   └── output/             # Chứa dữ liệu dự báo & logs (CSV/JSON)
│       ├── forecast_5m.csv
│       ├── metrics_5m.json
│       ├── scale_hybrid_5m.csv
│       └── ...
└── README.md               # Tài liệu hướng dẫn
```
⚙️ Cài đặt & Chạy Demo (Installation)

Bước 1: Clone dự án

```bash
git clone [https://github.com/NgThach/RuntimeError_Dataflow2026.git](https://github.com/NgThach/RuntimeError_Dataflow2026.git)
cd RuntimeError_Dataflow2026
```

Bước 2: Cài đặt thư viện

Yêu cầu Python 3.8 trở lên.

```bash
pip install -r requirements.txt
```
Bước 3: Chạy ứng dụng

```Bash
streamlit run app.py
```
Truy cập vào đường dẫn http://localhost:8501 trên trình duyệt.

🎛️ Hướng dẫn cấu hình (Configuration)
Bạn có thể thay đổi hành vi của hệ thống Auto-scaling bằng cách chỉnh sửa file autoscale_config.yaml:

YAML
global_parameters:
  TARGET_UTIL: 0.6          # Mức tải mục tiêu (60%). 40% còn lại là vùng đệm an toàn.
  SCALE_IN_COOLDOWN: 15     # Thời gian chờ trước khi tắt server (phút).
  UNIT_COST_PER_HOUR: 0.5   # Đơn giá thuê server ($/giờ).
Lưu ý: Sau khi sửa file config, hãy Refresh lại trang web để cập nhật.

📊 Giải thích kỹ thuật (Methodology)
Tại sao lại thừa tài nguyên (Vùng xanh)?

Chúng tôi áp dụng nguyên lý "Intended Waste for Reliability".

Chúng tôi đặt Target Utilization = 60%.

Nghĩa là hệ thống luôn dư thừa 40% năng lực xử lý.

Mục đích: Để hấp thụ các đợt tấn công bất ngờ (Spike) ngay lập tức trong khi chờ server mới khởi động (thường mất 1-2 phút).

Đánh giá độ chính xác (MAPE)

Mô hình đạt MAPE (Mean Absolute Percentage Error) ở mức ~5.xx%.

< 10%: Rất tốt (Highly Accurate).

10-20%: Tốt (Good).

> 50%: Không nên sử dụng.

👥 Tác giả (Authors)
Team: Runtime Error

Cuộc thi: DataFlow 2026

Liên hệ: [Thêm thông tin liên hệ của bạn tại đây]

Built with ❤️ using Streamlit & Python.
