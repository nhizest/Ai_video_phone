import streamlit as st
from google import genai
from google.genai import types
import requests
import time

# --- CẤU HÌNH GIAO DIỆN STREAMLIT ---
st.set_page_config(page_title="Trình Tạo Video AI Hoàn Chỉnh", page_icon="🎬", layout="centered")
st.title("🎬 Trình Tạo Video AI Bằng Câu Lệnh")
st.write("Ứng dụng tự động viết kịch bản bằng Gemini 2.5 và sinh video thông qua Luma API.")

# --- KHU VỰC CÀI ĐẶT API KEYS ---
with st.sidebar:
    st.header("🔑 Cấu hình API Key")
    gemini_key = st.text_input("1. Nhập Google Gemini API Key:", type="password")
    luma_key = st.text_input("2. Nhập Luma AI API Key:", type="password", help="Lấy tại bảng điều khiển tài khoản Luma Dream Machine API")
    st.markdown("[Lấy Gemini Key miễn phí tại Google AI Studio](https://google.com)")

# --- GIAO DIỆN CHÍNH ---
prompt_input = st.text_area(
    "Bạn muốn làm video về chủ đề gì? (Nhập tiếng Việt thoải mái):",
    placeholder="Kể một câu chuyện ngắn về chú mèo phi hành gia bay vào vũ trụ..."
)

# --- XỬ LÝ KHI BẤM NÚT TẠO VIDEO ---
if st.button("🚀 Bắt đầu tạo Video"):
    if not gemini_key or not luma_key:
        st.error("Vui lòng điền đầy đủ cả 2 API Key ở thanh bên (Sidebar)!")
    elif not prompt_input:
        st.warning("Vui lòng nhập ý tưởng/chủ đề cho video!")
    else:
        try:
            # --- BƯỚC 1: DÙNG GEMINI THẾ HỆ MỚI ĐỂ TỐI ƯU PROMPT TIẾNG ANH ---
            with st.spinner("🧠 1. Gemini đang tối ưu hóa ý tưởng thành Prompt video chuyên nghiệp..."):
                # Khởi tạo client theo SDK `google-genai` mới nhất
                client = genai.Client(api_key=gemini_key)
                
                system_prompt = (
                    f"Dựa vào ý tưởng này: '{prompt_input}', hãy viết một đoạn prompt ngắn (khoảng 30-50 từ) bằng tiếng Anh "
                    f"để đưa vào AI tạo video (như Luma/Runway). Prompt cần tập trung vào mô tả bối cảnh, hành động nhân vật, "
                    f"góc máy (cinematic, 4k, hyper-realistic, v.v.). CHỈ TRẢ VỀ ĐOẠN PROMPT TIẾNG ANH, không giải thích gì thêm."
                )
                
                # Sử dụng mô hình đời mới gemini-2.5-flash cực nhanh
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=system_prompt,
                )
                optimized_prompt = response.text.strip()
                
                st.success("Tối ưu prompt thành công!")
                st.info(f"**Prompt tiếng Anh gửi sang AI Video:** {optimized_prompt}")

            # --- BƯỚC 2: GỬI LỆNH SANG LUMA API ĐỂ TẠO VIDEO ---
            with st.spinner("🎥 2. Đang gửi yêu cầu và render Video (Có thể mất 1-2 phút)..."):
                luma_url = "https://lumalabs.ai"
                headers = {
                    "Authorization": f"Bearer {luma_key}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "prompt": optimized_prompt,
                    "aspect_ratio": "16:9",
                    "loop": False
                }
                
                # Gọi API tạo lệnh sinh video
                post_response = requests.post(luma_url, headers=headers, json=payload)
                
                # SỬA LỖI TẠI ĐÂY: Kiểm tra mã phản hồi thành công (201 Created) đúng cú pháp
                if post_response.status_code == 201:
                    generation_data = post_response.json()
                    task_id = generation_data.get("id")
                    
                    # --- BƯỚC 3: KIỂM TRA TRẠNG THÁI RENDER (POLLING) ---
                    status_url = f"https://lumalabs.ai/{task_id}"
                    
                    status_placeholder = st.empty()
                    progress_bar = st.progress(0)
                    
                    for percent_complete in range(1, 101):
                        get_response = requests.get(status_url, headers=headers)
                        result = get_response.json()
                        state = result.get("state")
                        
                        if state == "completed":
                            video_url = result.get("assets", {}).get("video")
                            progress_bar.progress(100)
                            status_placeholder.success("🎉 Video đã tạo xong!")
                            # Hiển thị video trực tiếp trên giao diện Streamlit để người dùng xem và tải về
                            st.video(video_url)
                            break
                        elif state == "failed":
                            st.error(f"Lỗi render video từ phía hệ thống Luma AI: {result.get('failure_reason')}")
                            break
                        else:
                            # Trạng thái đang xử lý (queued / processing / dreaming)
                            status_placeholder.text(f"⏳ Trạng thái: {state.upper()}... Đang xử lý khung hình...")
                            # Giả lập thanh tiến trình tăng dần
                            progress_bar.progress(min(percent_complete * 2, 95))
                            time.sleep(4)  # Đợi 4 giây trước khi kiểm tra lại
                else:
                    st.error(f"Không thể kết nối API Luma. Mã lỗi: {post_response.status_code} - {post_response.text}")

        except Exception as e:
            st.error(f"Có lỗi hệ thống phát sinh: {e}")
