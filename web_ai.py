import streamlit as st
import utils # Gọi file xử lý dữ liệu
import time
# --- ĐƯA CÁC THƯ VIỆN NẶNG LÊN ĐÂY ĐỂ NẠP SẴN ---
import google.generativeai as genai
import pandas as pd
import os
import json
from gtts import gTTS

# Gọi file trang chủ ngay từ đầu luôn
import trang_chu

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(page_title="HỌC GIỎI VĂN LOGIN", page_icon="🔐", layout="wide")

# --- 2. QUẢN LÝ TRẠNG THÁI (SESSION) ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_name' not in st.session_state:
    st.session_state['user_name'] = ""

# --- 3. GIAO DIỆN ĐĂNG NHẬP ---
def login_page():
    st.markdown("""
    <style>
    /* 1. Ẩn sidebar ở trang đăng nhập */
    [data-testid="stSidebar"] {display: none;} 

    /* 2. Nền toàn trang: Trắng chủ đạo pha Ombre Tím nhạt có hiệu ứng chuyển động */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(-45deg, #ffffff, #F8F4F9, #E8DEF0, #F3E8FF);
        background-size: 400% 400%;
        animation: gradientBG 10s ease infinite;
    }
    
    /* Hiệu ứng nền chuyển động từ từ */
    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* --- PHẦN MỚI: TẠO BẢNG TRẮNG CHO CỘT GIỮA --- */
    /* Target trực tiếp vào cột thứ 2 trong giao diện 3 cột */
    [data-testid="column"]:nth-of-type(2) {
        background-color: rgba(255, 255, 255, 0.95); /* Nền trắng hơi trong suốt */
        padding: 40px !important; /* Khoảng cách từ viền vào trong */
        border-radius: 24px; /* Bo góc tròn trịa */
        box-shadow: 0 15px 35px rgba(89, 49, 107, 0.1); /* Đổ bóng tím nhạt */
        margin-top: 5vh; /* Đẩy xuống một chút cho cân đối */
    }
    
    /* 3. Chỉnh các form input (Chữ đen, nền trắng, viền tím khi click) */
    div[data-testid="stVerticalBlock"] > div {
        gap: 0px !important;
    }
    .stTextInput input {
        color: #000000 !important; /* Chữ màu đen */
        background-color: #fafafa !important; /* Đổi màu nền input hơi xám nhẹ để nổi trên bảng trắng */
        border: 2px solid #e2e8f0 !important;
        border-radius: 8px !important;
        height: 48px;
        transition: all 0.3s ease !important;
    }
    /* Hiệu ứng khi bấm vào ô nhập liệu */
    .stTextInput input:focus {
        border-color: #7D4698 !important;
        box-shadow: 0 0 10px rgba(125, 70, 152, 0.15) !important;
        background-color: #ffffff !important;
    }
    .stTextInput label {
        color: #111111 !important; /* Label chữ đen/xám đậm */
        font-weight: 700 !important;
        margin-top: 15px !important;
    }
    
    /* 4. Nút bấm - Ombre Tím thay vì Xanh */
    .stButton button {
        width: 100%;
        background: linear-gradient(45deg, #7D4698, #A166AB) !important;
        color: white !important;
        border-radius: 10px !important;
        padding: 14px !important;
        margin-top: 25px !important;
        border: none !important;
        font-weight: bold !important;
        font-size: 16px !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(125, 70, 152, 0.3) !important;
    }
    /* Hiệu ứng khi di chuột vào nút */
    .stButton button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 25px rgba(125, 70, 152, 0.4) !important;
        background: linear-gradient(45deg, #59316B, #7D4698) !important;
    }
    .stButton button:active {
        transform: translateY(1px) !important;
        box-shadow: 0 2px 10px rgba(125, 70, 152, 0.3) !important;
    }

    /* 5. Tiêu đề "Chấm Văn AI" - Thêm hiệu ứng bay lơ lửng (Floating) */
    .alexander-title {
        font-size: 60px; 
        font-weight: 900; 
        text-align: center; 
        margin-bottom: 30px; 
        letter-spacing: -2px;
        background: linear-gradient(180deg, #59316B, #A166AB); /* Gradient tím đậm xuống nhạt */
        -webkit-background-clip: text; 
        -webkit-text-fill-color: transparent;
        filter: drop-shadow(0px 4px 4px rgba(0,0,0,0.1));
        animation: floatTitle 3s ease-in-out infinite; /* Gọi hiệu ứng lơ lửng */
    }
    /* 5.1 Tiêu đề phụ (Subtitle) - Nhất quán font, hiệu ứng nhịp thở phát sáng */
    .alexander-subtitle {
        font-size: 16px; 
        font-weight: 600; 
        text-align: center; 
        color: #7D4698; /* Màu tím tone-sur-tone với tiêu đề chính */
        margin-top: -20px; /* Kéo sát lại gần tiêu đề chính đang bị margin-bottom */
        margin-bottom: 30px; 
        letter-spacing: 3px; /* Kéo dãn khoảng cách chữ cho sang trọng */
        text-transform: uppercase; /* In hoa toàn bộ */
        animation: pulseSubtitle 3s ease-in-out infinite; /* Cùng nhịp 3s với tiêu đề nổi */
    }
    
    /* Animation nhịp thở cho subtitle */
    @keyframes pulseSubtitle {
        0%, 100% { 
            opacity: 0.7; 
            transform: scale(1); 
            text-shadow: 0px 0px 0px rgba(125, 70, 152, 0);
        }
        50% { 
            opacity: 1; 
            transform: scale(1.02); /* Phóng to cực nhẹ */
            text-shadow: 0px 0px 12px rgba(125, 70, 152, 0.5); /* Phát sáng viền chữ */
        }
    }
    /* Animation lơ lửng cho tiêu đề */
    @keyframes floatTitle {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-8px); }
    }
    
    /* 6. Chỉnh màu cho Tabs (Đăng nhập / Đăng ký) */
    .stTabs [data-baseweb="tab"] p {
        color: #555555 !important;
        font-weight: 600;
        font-size: 1.1rem;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] p {
        color: #7D4698 !important; /* Tab đang chọn có chữ màu tím */
    }
    .stTabs [data-baseweb="tab-highlight"] {
        background-color: #7D4698 !important; /* Gạch dưới màu tím */
    }

    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1, 1.2, 1]) 
    
    with c2:
        # Tiêu đề chính
        st.markdown('<div class="alexander-title">HỌC GIỎI VĂN</div>', unsafe_allow_html=True)
        
        # Dòng chữ nhỏ (Subtitle) ngay bên dưới
        st.markdown('<div class="alexander-subtitle">Viết văn theo cách của bạn</div>', unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["Đăng Nhập", "Đăng Ký"])
        
        # --- TAB ĐĂNG NHẬP ---
        with tab1:
            username = st.text_input("Tài khoản", key="login_user")
            password = st.text_input("Mật khẩu", type="password", key="login_pass")
            
            if st.button("Đăng nhập ngay 🚀", use_container_width=True):
                is_valid, result = utils.authenticate(username, password)
                if is_valid:
                    st.session_state['logged_in'] = True
                    st.session_state['user_name'] = result 
                    
                    st.success("Đang vào hệ thống...")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(result)

        # --- TAB ĐĂNG KÝ ---
        with tab2:
            new_user = st.text_input("Tài khoản mới")
            new_pass = st.text_input("Mật khẩu mới", type="password")
            new_name = st.text_input("Tên hiển thị (VD: Admin)")
            
            if st.button("Tạo tài khoản ✨", use_container_width=True):
                if new_user and new_pass and new_name:
                    success, msg = utils.save_user(new_user, new_pass, new_name)
                    if success:
                        st.success(msg)
                        st.info("Vui lòng quay lại tab 'Đăng Nhập' để tiếp tục.")
                    else:
                        st.error(msg)
                else:
                    st.warning("Vui lòng điền đầy đủ thông tin.")


# --- 4. LOGIC ĐIỀU HƯỚNG CHÍNH ---
if not st.session_state['logged_in']:
    # Nếu chưa đăng nhập -> Hiện trang Đăng nhập
    login_page()
else:
    # Đã đăng nhập -> GỌI TRỰC TIẾP FILE TRANG_CHU
    try:
        import trang_chu  
        trang_chu.app()   
    except ImportError:
        st.error("Lỗi: Không tìm thấy file 'trang_chu.py'. Hãy chắc chắn 2 file nằm cùng thư mục.")
    except AttributeError:
        st.error("Lỗi: Trong file 'trang_chu.py' không có hàm 'def app():'. Hãy sửa lại code file trang chủ.")
