import os
import zipfile
import subprocess
import tempfile
import gdown
import streamlit as st

st.set_page_config(page_title="1-Click Rebrander", layout="centered")

# Auto-download and extract assets from Google Drive on initial boot
GDRIVE_FILE_ID = "1UZRpqVlaC4FDQb-7Gab_imnACZh1fR5-"
ZIP_NAME = "assets.zip"

if not os.path.exists("assets"):
    with st.spinner("Downloading assets from Google Drive (one-time setup)..."):
        url = f"https://drive.google.com/uc?id={GDRIVE_FILE_ID}"
        gdown.download(url, ZIP_NAME, quiet=False)
        if os.path.exists(ZIP_NAME):
            with zipfile.ZipFile(ZIP_NAME, "r") as zip_ref:
                zip_ref.extractall(".")
            os.remove(ZIP_NAME)

st.title("⚡ 1-Click Video Rebrander")

# Upload and options
video_file = st.file_uploader("Upload Video Clip", type=["mp4", "mov", "avi"])
headline = st.text_input("Headline Text", placeholder="Type headline...")

col1, col2 = st.columns(2)
with col1:
    speed = st.slider("Clip Speed", 0.5, 2.5, 1.12, 0.01)
    contrast = st.slider("Contrast", 0.8, 1.5, 1.05, 0.01)
with col2:
    saturation = st.slider("Saturation", 0.8, 1.5, 1.10, 0.01)
    bg_color = st.selectbox("Header Pad Background", ["black", "white"])

if st.button("⚡ Render Video", type="primary"):
    if not video_file:
        st.error("Please upload a video file first.")
    else:
        with st.spinner("Rendering video with FFmpeg..."):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as in_tmp:
                in_tmp.write(video_file.read())
                in_path = in_tmp.name

            out_path = in_path.replace(".mp4", "_rebranded.mp4")

            # FFmpeg: adjustments, speed retiming, and 9:16 layout
            cmd = [
                "ffmpeg", "-y", "-i", in_path,
                "-vf", (
                    f"eq=contrast={contrast}:saturation={saturation},"
                    f"setpts=PTS/{speed},"
                    "scale=1080:1920:force_original_aspect_ratio=decrease,"
                    f"pad=1080:1920:(ow-iw)/2:(oh-ih)/2:{bg_color}"
                ),
                "-filter:a", f"atempo={speed}",
                "-c:v", "libx264", "-preset", "veryfast", "-crf", "22",
                "-movflags", "+faststart",
                out_path
            ]

            res = subprocess.run(cmd, capture_output=True, text=True)

            if res.returncode == 0:
                st.success("Render completed successfully!")
                st.video(out_path)
                with open(out_path, "rb") as f:
                    st.download_button(
                        label="⬇️ Download Rebranded MP4",
                        data=f,
                        file_name="rebranded_clip.mp4",
                        mime="video/mp4"
                    )
            else:
                st.error("FFmpeg render failed.")
                st.code(res.stderr)

            if os.path.exists(in_path):
                os.remove(in_path)
