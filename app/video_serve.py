import asyncio
import websockets
import cv2
import json
import numpy as np
from ultralytics import YOLO
import base64
from sort import SortTracker

# --- Load YOLO + SORT once ---
model = YOLO("yolov8n.pt")
tracker = SortTracker(max_age=15, min_hits=3, iou_threshold=0.3)

# --- Shared state ---
entry_count = 0
exit_count = 0
counted_ids = set()
line_coords = None  #  Will be updated from Streamlit
video_source = 0
connected_clients = set()


# --- Helper: process frame ---
def process_frame(frame):
    global entry_count, exit_count, counted_ids, line_coords

    results = model(frame, stream=True, classes=[0])  # detect people
    detections = []

    for result in results:
        boxes = result.boxes.xyxy.cpu().numpy()
        confs = result.boxes.conf.cpu().numpy()
        for box, conf in zip(boxes, confs):
            if conf > 0.5:
                detections.append([box[0], box[1], box[2], box[3], conf, 0])

    detections = np.array(detections) if len(detections) > 0 else np.empty((0, 6))
    tracks = tracker.update(detections,1)# 1 is required positional argument , which is not used inside the update function, i have added this just to avoid error, there is not usage of it inside the function but required just as positional argument.

    # --- Draw user-defined line ---
    if line_coords:
        #  Draw the boundary line from Streamlit
        x1, y1, x2, y2 = map(int, line_coords)
        cv2.line(frame, (2*x1, 2*y1), (2*x2, 2*y2), (0, 0, 255), 3)
    else:
        # fallback horizontal midline
        h = frame.shape[0]
        cv2.line(frame, (0, h // 2), (frame.shape[1], h // 2), (0, 0, 255), 2)

    # --- Process tracked objects ---
    for track in tracks:
        # SORT tracker returns: x1, y1, x2, y2, id
        x1, y1, x2, y2, track_id = map(int, track[:5])
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        # Draw box and ID
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(frame, f"ID {track_id}", (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        cv2.circle(frame, (cx, cy), 4, (0, 255, 255), -1)

        # --- Count entries/exits ---
        if line_coords:
            lx1, ly1, lx2, ly2 = map(int, line_coords)
            line_y = (ly1 + ly2) // 2  # assume mostly horizontal
        else:
            line_y = frame.shape[0] // 2

        if track_id not in counted_ids and abs(cy - line_y) < 10:
            if cy < line_y:
                entry_count += 1
            else:
                exit_count += 1
            counted_ids.add(track_id)

    # --- Overlay counts ---
    cv2.putText(frame, f"Entries: {entry_count}", (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.putText(frame, f"Exits: {exit_count}", (20, 80),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    return frame

async def broadcast(message):
    if connected_clients:
        await asyncio.gather(*(client.send(message) for client in connected_clients))

# --- WebSocket handler ---
async def video_stream(websocket):
    global line_coords, video_source, entry_count, exit_count, counted_ids

    #  Receive the initial config (video source + boundary)
    print("[DEBUG] Server starting...", flush=True)
    config_message = await websocket.recv()
    print("[DEBUG] Server starting...", flush=True)
    config = json.loads(config_message)

    video_source = config.get("video_source", 0)
    line_coords = config.get("boundary_line", None)
    print(line_coords)
    print(f"[CONFIG] Video source: {video_source}")
    print(f"[CONFIG] Boundary line: {line_coords}")

    cap = cv2.VideoCapture(0 if video_source in [0, "0"] else video_source)
    if not cap.isOpened():
        print("Error: Could not open video source")
        await websocket.close()
        return
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps == 0: fps = 30
    delay = 1 / fps
    entry_count = 0
    exit_count = 0
    counted_ids.clear()

    while True:
        ret, frame = cap.read()
        if not ret:
            print("End of stream or read error.")
            break

        processed_frame = process_frame(frame)

        # Encode frame as JPG and send over WebSocket
        _, buffer = cv2.imencode(".jpg", processed_frame)
        frame_b64 = base64.b64encode(buffer).decode("utf-8")
        data = {
            "frame": frame_b64,
            "entries": entry_count,
            "exits": exit_count
            }
        print()
        await websocket.send(json.dumps(data))
        await asyncio.sleep(delay)  # ~30 FPS

    cap.release()


# --- Run WebSocket server ---
async def main():
    async with websockets.serve(video_stream, "localhost", 8765):
        print(" WebSocket server running at ws://localhost:8765")
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
