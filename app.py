import streamlit as st
import google.generativeai as genai
from gtts import gTTS
from moviepy.editor import ImageClip, AudioFileClip
import os

# 1. Cấu hình giao diện hiển thị trên điện thoại
st.set_page_config(page_title="AI Video Generator", layout="centered")
st.title("📱 Trình Tạo Video AI Bằng Câu Lệnh")

# Nhập API Key bảo mật
api_key = st.text_input("Nhập Google Gemini API Key:", type="password")

if api_key:
    # Cấu hình API cũ nhưng cực kỳ ổn định
    genai.configure(api_key=api_key)
    
    # Ô nhập câu lệnh (Prompt)
    user_prompt = st.text_area("Bạn muốn làm video về chủ đề gì?", "Kể một câu chuyện ngắn về chú mèo bay vào vũ trụ")

    if st.button("🚀 Bắt đầu tạo Video"):
        with st.spinner("AI đang xử lý... Vui lòng đợi trong giây lát!"):
            try:
                # BƯỚC 1: Sử dụng mô hình quốc dân gemini-pro để tạo lời thoại
                model = genai.GenerativeModel('gemini-pro')
                text_response = model.generate_content(
                    f"Viết 1 câu lời thoại ngắn (dưới 20 từ) bằng tiếng Việt cho chủ đề: {user_prompt}. Chỉ trả về câu lời thoại, không kèm theo chữ khác."
                )
                voice_text = text_response.text
                st.write(f"📝 **Lời thoại AI:** {voice_text}")

                # BƯỚC 2: Chuyển văn bản thành giọng đọc
                tts = gTTS(text=voice_text, lang='vi')
                audio_path = "voice.mp3"
                tts.save(audio_path)

                # BƯỚC 3: Tạo hình ảnh minh họa sạch
                # Vì Imagen API yêu cầu tài khoản trả phí, ta dùng một ảnh mặc định chất lượng cao 9:16 để đảm bảo code render luôn thành công
                image_path = "background.jpg"
                if not os.path.exists(image_path):
                    import requests
                    # Tải một ảnh nền vũ trụ tuyệt đẹp tỷ lệ dọc dọc chuẩn TikTok
                    img_url = "https://unsplash.com"
                    img_data = requests.get(img_url).content
                    with open(image_path, 'wb') as handler:
                        handler.write(img_data)

                # BƯỚC 4: Dùng MoviePy ghép âm thanh vào ảnh
                audio_clip = AudioFileClip(audio_path)
                video_clip = ImageClip(image_path).set_duration(audio_clip.duration)
                video_clip = video_clip.set_audio(audio_clip)
                
                output_video_path = "final_ai_video.mp4"
                video_clip.write_videofile(output_video_path, fps=24, codec="libx264", audio_codec="aac")

                # BƯỚC 5: Hiển thị video kết quả
                st.success("🎉 Video của bạn đã sẵn sàng!")
                st.video(output_video_path)
                
                # Nút bấm tải về máy
                with open(output_video_path, "rb") as file:
                    st.download_button(
                        label="📥 Tải video về điện thoại",
                        data=file,
                        file_name="ai_video.mp4",
                        mime="video/mp4"
                    )

                # Dọn dẹp bộ nhớ tạm
                audio_clip.close()
                video_clip.close()
                os.remove(audio_path)

            except Exception as e:
                st.error(f"Có lỗi xảy ra: {e}")
else:
    st.info("Vui lòng nhập API Key để kích hoạt phần mềm.")
