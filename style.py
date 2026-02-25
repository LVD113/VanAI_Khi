import streamlit as st

def apply_purple_bubble_bg(): 
    # Phần 1: Tạo cấu trúc HTML cho các bong bóng
    bubbles_html = """
    <div class="bubble-container">
        <ul class="bubbles">
            <li></li><li></li><li></li><li></li><li></li>
            <li></li><li></li><li></li><li></li><li></li>
        </ul>
    </div>
    """
    st.markdown(bubbles_html, unsafe_allow_html=True)

def apply_custom_style():
    st.markdown("""
    <style> 
    /* --- HIỆU ỨNG BONG BÓNG BAY (BUBBLES ANIMATION) --- */
    .bubble-container {
        position: fixed;
        top: 0; left: 0;
        width: 100%; height: 100%;
        z-index: -1; /* Đẩy ra lớp sau cùng để không đè lên chữ */
        overflow: hidden;
        pointer-events: none; /* Không cản trở click chuột */
    }
    
    .bubbles {
        position: absolute;
        top: 0; left: 0;
        width: 100%; height: 100%;
        padding: 0; margin: 0;
    }
    
    .bubbles li {
        position: absolute;
        list-style: none;
        display: block;
        width: 40px; height: 40px;
        /* Bong bóng bằng kính mờ màu tím */
        background-color: rgba(125, 70, 152, 0.15); 
        backdrop-filter: blur(4px);
        border: 1px solid rgba(255, 255, 255, 0.4);
        bottom: -150px;
        animation: floatUp 25s infinite linear;
        border-radius: 50%; 
    }

    /* Kích thước và tốc độ ngẫu nhiên cho 10 bong bóng */
    .bubbles li:nth-child(1) { left: 10%; width: 80px; height: 80px; animation-delay: 0s; }
    .bubbles li:nth-child(2) { left: 20%; width: 30px; height: 30px; animation-delay: 2s; animation-duration: 17s; }
    .bubbles li:nth-child(3) { left: 25%; width: 50px; height: 50px; animation-delay: 4s; }
    .bubbles li:nth-child(4) { left: 40%; width: 60px; height: 60px; animation-delay: 0s; animation-duration: 22s; }
    .bubbles li:nth-child(5) { left: 70%; width: 40px; height: 40px; animation-delay: 3s; }
    .bubbles li:nth-child(6) { left: 80%; width: 100px; height: 100px; animation-delay: 3s; }
    .bubbles li:nth-child(7) { left: 32%; width: 120px; height: 120px; animation-delay: 7s; }
    .bubbles li:nth-child(8) { left: 55%; width: 25px; height: 25px; animation-delay: 15s; animation-duration: 40s; }
    .bubbles li:nth-child(9) { left: 25%; width: 15px; height: 15px; animation-delay: 2s; animation-duration: 35s; }
    .bubbles li:nth-child(10){ left: 90%; width: 70px; height: 70px; animation-delay: 11s; }

    @keyframes floatUp {
        0% { transform: translateY(0) rotate(0deg); opacity: 1; border-radius: 50%; }
        100% { transform: translateY(-1000px) rotate(720deg); opacity: 0; border-radius: 40%; }
    }

    /* --- NỀN GIAO DIỆN (BACKGROUND GRADIENT) --- */
    /* Nền Ombre tím hướng xuống */
    .stApp, [data-testid="stAppViewContainer"] {
        background: linear-gradient(180deg, #E8DEF0 0%, #D4C4E1 50%, #F8F4F9 100%) !important;
        background-attachment: fixed !important;
        background-size: cover !important;
    }

    /* Sidebar trong suốt mờ */
    [data-testid="stSidebar"] {
        background: rgba(232, 222, 240, 0.6) !important;
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(161, 102, 171, 0.3); 
    }
    
    [data-testid="stHeader"] {
        background-color: transparent !important;
    }
    
    /* --- 1. CORE & ANIMATIONS --- */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    :root {
        --primary: #7D4698;
        --bg-soft: #F8F4F9;
        --shadow-md: 0 8px 32px 0 rgba(89, 49, 107, 0.15); /* Bóng đổ cho kính */
        --shadow-lg: 0 8px 32px 0 rgba(89, 49, 107, 0.3);
    }

    @keyframes slideUpFade {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .stApp { font-family: 'Inter', sans-serif; }

    /* --- 2. CUSTOM SCROLLBAR --- */
    ::-webkit-scrollbar { width: 8px; height: 8px; }
    ::-webkit-scrollbar-track { background: rgba(248, 244, 249, 0.5); border-radius: 4px; }
    ::-webkit-scrollbar-thumb { background: #A166AB; border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: #7D4698; }

    /* --- 3. PAPER CONTAINER (HIỆU ỨNG GLASSMORPHISM) --- */
    .paper-card {
        background: rgba(255, 255, 255, 0.45); /* Lớp nền trắng bán trong suốt */
        backdrop-filter: blur(16px); /* Làm mờ (Glassmorphism) */
        -webkit-backdrop-filter: blur(16px);
        border-radius: 16px;
        padding: 24px;
        box-shadow: var(--shadow-md);
        border: 1px solid rgba(255, 255, 255, 0.6); /* Viền trắng hắt sáng nhẹ */
        height: 550px; 
        overflow-y: auto;
        line-height: 1.8;
        font-size: 16px;
        color: #334155;
        transition: all 0.3s ease;
        animation: slideUpFade 0.6s ease-out forwards; 
    }

    .paper-card:hover {
        box-shadow: var(--shadow-lg);
        border-color: #A166AB; /* Viền tím nhạt khi hover */
    }
    
    .card-header {
        font-size: 1.1rem;
        font-weight: 700;
        color: #59316B;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        gap: 8px;
        border-bottom: 2px solid rgba(161, 102, 171, 0.3); /* Đường gạch mờ */
        padding-bottom: 12px;
    }

    /* --- 4. HIGHLIGHT STYLES --- */
    .highlight-error {
        background-color: rgba(254, 226, 226, 0.8);
        color: #dc2626;
        padding: 2px 6px;
        border-radius: 6px;
        font-weight: 600;
        cursor: help;
        border-bottom: 2px solid #ef4444;
        transition: all 0.2s;
    }
    
    .highlight-error:hover {
        background-color: #fca5a5; transform: scale(1.05);
    }

    .highlight-success {
        background-color: rgba(248, 244, 249, 0.7); 
        color: #7D4698; 
        padding: 2px 6px;
        border-radius: 6px;
        font-weight: 600;
        border-bottom: 2px solid #59316B; 
        transition: all 0.2s;
    }
    
    .highlight-success:hover {
        background-color: #E8DEF0; transform: translateY(-1px);
    }

    /* --- 5. UI ELEMENTS --- */
    /* Ô nhập liệu kính */
    .stTextArea textarea {
        background: rgba(255, 255, 255, 0.5) !important; /* Kính mờ */
        border-radius: 12px !important;
        border: 1px solid #A166AB !important;
        box-shadow: none !important;
        font-size: 16px !important;
        padding: 16px !important;
    }
    .stTextArea textarea:focus {
        background: rgba(255, 255, 255, 0.8) !important;
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 3px rgba(125, 70, 152, 0.2) !important;
    }

    /* Nút bấm (Button) - Gradient tím mềm mại */
    .stButton > button {
        background: linear-gradient(90deg, #A166AB, #7D4698) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        padding: 0.5rem 1.2rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 10px rgba(89, 49, 107, 0.2) !important;
    }
    .stButton > button:hover {
        background: linear-gradient(90deg, #7D4698, #59316B) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 15px rgba(89, 49, 107, 0.4) !important;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
    }
    </style>
    """, unsafe_allow_html=True)