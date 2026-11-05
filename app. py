import streamlit as st
from google import genai
from gtts import gTTS
from moviepy.editor import ImageClip, AudioFileClip
import os

# 1. Cấu hình giao diện hiển thị trên điện thoại
st.set_page_config(page_title="AI Video Generator", layout="centered")
st.title("📱 Trình Tạo Video AI Bằng Câu Lệnh")

# Nhập API Key bảo mật (Lấy miễn phí từ Google AI Studio)
api_key = st.text_input("Nhập Google Gemini API Key:", type="password")

if api_key:
    client = genai.Client(api_key=api_key)
    
    # Ô nhập câu lệnh (Prompt) thiết kế tối ưu cho bàn phím điện thoại
    user_prompt = st.text_area("Bạn muốn làm video về chủ đề gì?", "Kể một câu chuyện ngắn về chú mèo bay vào vũ trụ")

    if st.button("🚀 Bắt đầu tạo Video"):
        with st.spinner("AI đang xử lý... Vui lòng đợi trong giây lát!"):
            try:
                # BƯỚC 1: Dùng Gemini tạo lời thoại ngắn (Dưới 30 từ để xử lý nhanh)
                text_response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=f"Viết 1 câu lời thoại ngắn (dưới 30 từ) bằng tiếng Việt cho chủ đề: {user_prompt}. Chỉ trả về câu lời thoại, không kèm theo chữ khác."
                )
                voice_text = text_response.text
                st.write(f"📝 **Lời thoại AI:** {voice_text}")

                # BƯỚC 2: Chuyển văn bản thành giọng đọc (Sử dụng Google TTS miễn phí)
                tts = gTTS(text=voice_text, lang='vi')
                audio_path = "voice.mp3"
                tts.save(audio_path)

                # BƯỚC 3: Dùng Gemini Image Generation để vẽ ảnh minh họa
                image_response = client.models.generate_images(
                    model='imagen-3.0-generate-002',
                    prompt=f"A cinematic vertical 9:16 background photo for: {user_prompt}, high resolution",
                    config=dict(numberOfImages=1, aspectRatio="9:16", outputMimeType="image/jpeg")
                )
                
                # Lưu ảnh về bộ nhớ tạm
                image_path = "ai_image.jpg"
                for generated_image in image_response.generated_images:
                    with open(image_path, "wb") as f:
                        f.write(generated_image.image.image_bytes)

                # BƯỚC 4: Dùng MoviePy tự động ghép ảnh và âm thanh thành Video 9:16 (Chuẩn TikTok)
                audio_clip = AudioFileClip(audio_path)
                video_clip = ImageClip(image_path).set_duration(audio_clip.duration)
                video_clip = video_clip.set_audio(audio_clip)
                
                output_video_path = "final_ai_video.mp4"
                video_clip.write_videofile(output_video_path, fps=24, codec="libx264", audio_codec="aac")

                # BƯỚC 5: Hiển thị video kết quả lên màn hình điện thoại để tải về
                st.success("🎉 Video của bạn đã sẵn sàng!")
                st.video(output_video_path)
                
                # Nút bấm tải về máy điện thoại
                with open(output_video_path, "rb") as file:
                    st.download_button(
                        label="📥 Tải video về điện thoại",
                        data=file,
                        file_name="ai_video.mp4",
                        mime="video/mp4"
                    )

                # Dọn dẹp file tạm trên server
                audio_clip.close()
                video_clip.close()
                os.remove(audio_path)
                os.remove(image_path)
                os.remove(output_video_path)

            except Exception as e:
                st.error(f"Có lỗi xảy ra: {e}")
else:
    st.info("Vui lòng nhập API Key để kích hoạt phần mềm.")
