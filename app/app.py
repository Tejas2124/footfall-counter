import base64
import streamlit as st
import asyncio
import websockets
import cv2
import json
import time
import tempfile
import numpy as np
from streamlit_drawable_canvas import st_canvas
from PIL import Image
import tempfile

WS_URL = "ws://localhost:8765"

st.title("🎥 Smart People Counter")

# --- Choose video source ---
source_type = st.radio("Select Video Source", ["Webcam", "Video File"])

video_source = None
temp_video_path = None

if source_type == "Video File":
    uploaded_file = st.file_uploader("Upload video file", type=["mp4"])
    if uploaded_file is not None:
        # Save uploaded video temporarily
        tfile = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        tfile.write(uploaded_file.read())
        temp_video_path = tfile.name
        video_source = temp_video_path
else:
    video_source = 0  # Webcam

# --- Capture frame for boundary ---
if st.button("📸 Capture Frame for Boundary Setup"):
    if source_type == "Video File" and video_source is None:
        st.error("Please upload a video file first.")
    else:
        cap = cv2.VideoCapture(video_source)
        ret, frame = cap.read()
        cap.release()

        if ret:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            st.session_state["captured_frame"] = frame_rgb
            st.session_state["frame_shape"] = frame.shape
            st.text(f"shape of frame {frame.shape}")
            st.success("✅ Frame captured successfully! You can now draw the boundary.")
        else:
            st.error("Failed to capture frame. Please try again.")



# --- Show canvas for boundary drawing ---


if "captured_frame" in st.session_state:
    frame_rgb = st.session_state["captured_frame"]
    h, w = st.session_state["frame_shape"][:2]

    # Display smaller version for Streamlit layout
    display_width = min(640, w)
    display_height = int(h * (display_width / w))

    # Show captured frame (for visual reference)
    st.image(frame_rgb, caption="Captured frame (for reference)", width=display_width)

    # 🎨 Canvas — no background image
    canvas_result = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)",
        stroke_width=3,
        stroke_color="#FF0000",
        height=display_height,
        width=display_width,
        drawing_mode="line",
        key="canvas",
    )

    # --- Extract and rescale coordinates ---
    # if canvas_result.json_data is not None:
    #     objects = canvas_result.json_data["objects"]
    #     if len(objects) > 0:
    #         last_obj = objects[-1]
    #         if "x1" in last_obj and "y1" in last_obj:
    #             x1, y1, x2, y2 = last_obj["x1"], last_obj["y1"], last_obj["x2"], last_obj["y2"]
    #         else:
    #             x1 = last_obj["x"]
    #             y1 = last_obj["y"]
    #             x2 = x1 + last_obj["width"]
    #             y2 = y1 + last_obj["height"]

    #         # Scale back to original frame size
    #         scale_x = w / display_width
    #         scale_y = h / display_height
    #         x1_img, y1_img = int(x1 * scale_x), int(y1 * scale_y)
    #         x2_img, y2_img = int(x2 * scale_x), int(y2 * scale_y)

    #         st.session_state["boundary_line"] = (2*x1_img, 2*y1_img, 2*x2_img, 2*y2_img)
    #         st.success(f"Boundary: ({x1_img},{y1_img}) → ({x2_img},{y2_img})")

    if canvas_result.json_data is not None:
        objects = canvas_result.json_data["objects"]
        if len(objects) > 0:
            last_obj = objects[-1]

            left = last_obj.get("left", 0)
            top = last_obj.get("top", 0)
            width = last_obj.get("width", 0)
            height = last_obj.get("height", 0)

            originX = last_obj.get("originX", "left")
            originY = last_obj.get("originY", "top")

            # ✅ Convert from center-based → corner-based coordinates
            if originX == "center":
                x1 = left - width / 2
                x2 = left + width / 2
            else:
                x1 = left
                x2 = left + width

            if originY == "center":
                y1 = top - height / 2
                y2 = top + height / 2
            else:
                y1 = top
                y2 = top + height

            # Scale to image coordinates (if needed)
            scale_x = w / display_width
            scale_y = h / display_height

            x1_img, y1_img = int(x1 * scale_x), int(y1 * scale_y)
            x2_img, y2_img = int(x2 * scale_x), int(y2 * scale_y)

            st.session_state["boundary_line"] = (x1_img, y1_img, x2_img, y2_img)
            print(st.session_state["boundary_line"])
            st.success(f"Boundary: ({x1_img},{y1_img}) → ({x2_img},{y2_img})")


# --- Display saved boundary ---
if "boundary_line" in st.session_state:
    st.info(f"✅ Current boundary line: {st.session_state['boundary_line']}")

# --- Start/Stop stream ---
col1, col2 = st.columns(2)
if col1.button("▶ Start Counting"):
    st.session_state["running"] = True
    st.session_state["video_source"] = video_source
elif col2.button("⏹ Stop"):
    st.session_state["running"] = False

# --- WebSocket Streaming Display ---
if "running" in st.session_state and st.session_state["running"]:
    stframe = st.empty()
    entry_box = st.empty()
    exit_box = st.empty()

    # async def receive_frames():
    #     async with websockets.connect(WS_URL) as ws:
    #         # Send config (video source + line coordinates)
    #         await ws.send(json.dumps({
    #         "video_source": st.session_state.get("video_source", 0),
    #         "boundary_line": st.session_state.get("boundary_line", None)}))
    #         while True:
    #             data = await ws.recv()

    #             parsed = json.loads(data)
    #             frame_b64 = parsed["frame"]
    #             entries = parsed["entries"]
    #             exits = parsed["exits"]
    #             frame = base64.b64decode(frame_b64)


    #             np_frame = np.frombuffer(frame, np.uint8)
    #             frame = cv2.imdecode(np_frame, cv2.IMREAD_COLOR)
    #             frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    #             stframe.image(frame_rgb, width="content")
    #             # entries = st.session_state.get("entries", 0)
    #             # exits = st.session_state.get("exits", 0)
    #             entry_box.metric("Entries", entries)
    #             exit_box.metric("Exits", exits)
    async def receive_frames():
        async with websockets.connect(WS_URL) as ws:
            stframe = st.empty()
            entry_box = st.empty()
            exit_box = st.empty()
            await ws.send(json.dumps({
            "video_source": st.session_state.get("video_source", 0),
            "boundary_line": st.session_state.get("boundary_line")}))

            while True:
                msg = await ws.recv()

                try:
                    parsed = json.loads(msg)
                except json.JSONDecodeError:
                    st.warning("⚠️ Received non-JSON data, skipping...")
                    continue

                # --- Extract data safely ---
                frame_b64 = parsed.get("frame")
                entries = parsed.get("entries", 0)
                exits = parsed.get("exits", 0)

                if frame_b64 is None:
                    st.warning("No frame data received.")
                    continue

                # --- Decode base64 frame ---
                try:
                    frame_bytes = base64.b64decode(frame_b64)
                    np_frame = np.frombuffer(frame_bytes, np.uint8)
                    frame = cv2.imdecode(np_frame, cv2.IMREAD_COLOR)
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                except Exception as e:
                    st.error(f"Frame decode error: {e}")
                    continue

                # --- Display frame + metrics ---
                stframe.image(frame_rgb, channels="RGB", width="content")
                entry_box.metric("Entries", entries)
                exit_box.metric("Exits", exits)

    asyncio.run(receive_frames())
