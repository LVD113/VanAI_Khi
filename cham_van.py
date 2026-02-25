import google.generativeai as genai
import os

# Thay cái mã API Key thật của bạn vào giữa dấu ngoặc kép này
API_KEY = "DÁN_MÃ_KEY_CỦA_BẠN_VÀO_ĐÂY"

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def main():
    print("\n" + "="*40)
    print("   AI CHẤM VĂN & HỌC HỎI CỦA ALEXANDER")
    print("="*40)
    
    # Nhập văn mẫu
    print("\n[BƯỚC 1] Nhập bài VĂN MẪU (để AI học phong cách):")
    van_mau = input(">> Dán vào đây rồi nhấn Enter: ")
    
    # Nhập bài cần chấm
    print("\n[BƯỚC 2] Nhập BÀI VIẾT CỦA BẠN (để AI chấm điểm):")
    bai_viet = input(">> Dán vào đây rồi nhấn Enter: ")

    prompt = f"""
    Bạn là một chuyên gia ngôn ngữ. Hãy học phong cách từ bài mẫu này: '{van_mau}'
    Sau đó chấm điểm bài viết này: '{bai_viet}'
    
    Yêu cầu:
    1. Chỉ ra các lỗi chính tả, ngữ pháp.
    2. Nhận xét bố cục so với bài mẫu.
    3. Chỉnh sửa lại các câu văn chưa hay theo phong cách bài mẫu.
    """

    print("\n--- Đang phân tích... Vui lòng đợi trong giây lát ---")
    try:
        response = model.generate_content(prompt)
        print("\n" + "*"*20 + " KẾT QUẢ " + "*"*20)
        print(response.text)
        print("*"*49)
    except Exception as e:
        print(f"Có lỗi xảy ra: {e}")

if __name__ == "__main__":
    main()