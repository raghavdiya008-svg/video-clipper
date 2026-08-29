import streamlit as st
import subprocess
import tempfile
import os

st.set_page_config(page_title="1-Click Clipper", layout="centered")
st.title("⚡ 1-Click Video Rebrander")

# Upload and settings
video_file = st.file_uploader("Upload Video", type=["mp4", "mov", "avi"])
headline = st.text_input("Headline Text", placeholder="Enter headline...")

col1, col2 = st.columns(2)
with col1:
    speed = st.slider("Speed Factor", 0.8, 1.5, 1.12, 0.01)
    contrast = st.slider("Contrast", 0.8, 1.4, 1.05, 0.01)
with col2:
    saturation = st.slider("Saturation", 0.8, 1.5, 1.10, 0.01)
    bg_color = st.selectbox("Header Pad", ["white", "black"])

if st.button("⚡ Render Video", type="primary"):
    if not video_file:
        st.error("Please upload a video first.")
    else:
        with st.spinner("Processing with FFmpeg..."):
            # Save input to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as in_tmp:
                in_tmp.write(video_file.read())
                in_path = in_tmp.name

            out_path = in_path.replace(".mp4", "_out.mp4")

            # Build FFmpeg command with color grading, retiming, and 9:16 layout
            cmd = [
                "ffmpeg", "-y", "-i", in_path,
                "-vf", (
                    f"eq=contrast={contrast}:saturation={saturation},"
                    f"setpts=PTS/{speed},"
                    f"scale=1080:1920:force_original_aspect_ratio=decrease,"
                    f"pad=1080:1920:(ow-iw)/2:(oh-ih)/2:{bg_color}"
                ),
                "-filter:a", f"atempo={speed}",
                "-c:v", "libx264", "-preset", "veryfast", "-crf", "22",
                "-movflags", "+faststart",
                out_path
            ]

            res = subprocess.run(cmd, capture_output=True, text=True)

            if res.returncode == 0:
                st.success("Render complete!")
                st.video(out_path)
                with open(out_path, "rb") as f:
                    st.download_button(
                        label="⬇️ Download MP4",
                        data=f,
                        file_name="rebranded_clip.mp4",
                        mime="video/mp4"
                    )
            else:
                st.error("FFmpeg error occurred.")
                st.code(res.stderr)

            # Cleanup temp input
            if os.path.exists(in_path):
                os.remove(in_path)  
