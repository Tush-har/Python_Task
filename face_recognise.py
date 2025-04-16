import cv2
import face_recognition
import numpy as np
import os
import datetime
import time
import winsound  # Windows-only

# ======== Setup Known Faces ==========
known_encodings = []
known_names = []
images_folder = "images"

print("[INFO] Loading known faces...")
for filename in os.listdir(images_folder):
    if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
        img_path = os.path.join(images_folder, filename)
        image = face_recognition.load_image_file(img_path)
        encodings = face_recognition.face_encodings(image)
        if encodings:
            known_encodings.append(encodings[0])
            name = os.path.splitext(filename)[0]
            known_names.append(name)
            print(f"✔️ Loaded: {name}")
        else:
            print(f"❌ No face found in {filename}, skipping...")

# ======== Attendance and Time Tracking ==========
present_today = set()
log_filename = "attendance_log.txt"
first_detection = {}
last_detection = {}
last_beep_time = {}  # Tracks the last time a beep was played for each person

# Working time notification variables
working_notification_text = ""
working_notification_end = 0

# ======== IP Camera Setup ==========
ip_camera_url = "rtsp://admin:trident@123@192.168.1.110:554/stream1?transport=tcp"  # TCP for reliability
save_folder = "saved_images_cctv1"
if not os.path.exists(save_folder):
    os.makedirs(save_folder)

cap = cv2.VideoCapture()
cap.open(ip_camera_url, cv2.CAP_FFMPEG)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 5)  # Increased buffer size

if not cap.isOpened():
    print("Error: Could not open the camera stream.")
    exit()

print("Press 's' to save a frame or 'q' to quit.")

# ======== Frame Skipping Logic ==========
frame_counter = 0
frame_skip_interval = 10  # Process every 10th frame

# ======== Main Loop ==========
fail_count = 0  # Track frame capture failures
while True:
    ret, frame = cap.read()
    if not ret:
        fail_count += 1
        print(f"Error: Failed to capture frame ({fail_count}), reconnecting...")
        cap.release()  # Release the current capture object
        cap = cv2.VideoCapture()
        cap.open(ip_camera_url, cv2.CAP_FFMPEG)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 5)  # Reapply buffer size
        time.sleep(1)  # Brief delay before reconnecting
        continue

    frame_counter += 1
    if frame_counter % frame_skip_interval != 0:
        continue

    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_small_frame = small_frame[:, :, ::-1]

    face_locations = face_recognition.face_locations(rgb_small_frame)
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

    current_time = time.time()
    recognised_list = []  # To track recognition status of all faces

    for face_location, face_encoding in zip(face_locations, face_encodings):
        recognized = False
        name = None

        if known_encodings:
            face_distances = face_recognition.face_distance(known_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            best_distance = face_distances[best_match_index]
            confidence = (1.0 - best_distance) * 100

            if confidence >= 55:
                recognized = True
                name = known_names[best_match_index]

                # Beep every time a known face is recognized, with a 5-second cooldown per person
                if name not in last_beep_time or current_time > last_beep_time[name] + 5:
                    winsound.Beep(1000, 200)  # 1000 Hz for 200 ms
                    last_beep_time[name] = current_time

                if name not in present_today:
                    present_today.add(name)
                    mark_time = datetime.datetime.now().strftime("%H:%M:%S")
                    print(f"{name} detected at {mark_time}")
                    log_timestamp = datetime.datetime.now().strftime("%d:%m:%Y %H:%M:%S")
                    with open(log_filename, "a") as log_file:
                        log_file.write(f"{name} {log_timestamp}\n")

                if name not in first_detection:
                    first_detection[name] = current_time
                last_detection[name] = current_time

                elapsed_seconds = int(last_detection[name] - first_detection[name])
                working_time = str(datetime.timedelta(seconds=elapsed_seconds))
                working_notification_text = f"{name}: {working_time}"
                working_notification_end = current_time + 3

        top, right, bottom, left = face_location
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        if recognized:
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 3)
        else:
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 3)

        recognised_list.append(recognized)

    # ===== Display Overlays =====
    # Fonts
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1.2
    thickness = 3
    color = (0, 0, 0)

    # 1. Timestamp at top-right (250 px from top)
    current_dt = datetime.datetime.now().strftime("%A, %B %d, %Y %H:%M:%S")
    dt_text_size, _ = cv2.getTextSize(current_dt, font, font_scale, thickness)
    dt_pos_x = frame.shape[1] - dt_text_size[0] - 10
    dt_pos_y = 250
    cv2.putText(frame, current_dt, (dt_pos_x, dt_pos_y), font, font_scale, color, thickness)

    # 2. Working time (name + duration) below timestamp (approx. 1 cm = 37 px)
    if current_time < working_notification_end and working_notification_text:
        notif_font_scale = 1.3
        notif_color = (0, 0, 0)
        notif_text_size, _ = cv2.getTextSize(working_notification_text, font, notif_font_scale, thickness)
        notif_pos_x = frame.shape[1] - notif_text_size[0] - 10
        notif_pos_y = dt_pos_y + 37
        cv2.putText(frame, working_notification_text, (notif_pos_x, notif_pos_y), font, notif_font_scale, notif_color, thickness)

    # 3. Authorization Status at Bottom
    if face_locations:
        if all(recognised_list):
            status_text = "Authorised person"
            text_color = (0, 255, 0)  # green
        else:
            status_text = "Unauthorised person"
            text_color = (0, 0, 255)  # red
    else:
        status_text = ""

    if status_text:
        msg_font = cv2.FONT_HERSHEY_SIMPLEX
        msg_font_scale = 3
        msg_thickness = 3
        text_size, _ = cv2.getTextSize(status_text, msg_font, msg_font_scale, msg_thickness)
        text_x = (frame.shape[1] - text_size[0]) // 2
        text_y = frame.shape[0] - 50
        # Background rectangle
        rect_top_left = (text_x - 10, text_y - text_size[1] - 10)
        rect_bottom_right = (text_x + text_size[0] + 10, text_y + 10)
        cv2.rectangle(frame, rect_top_left, rect_bottom_right, (0, 0, 0), -1)  # black
        # Text
        cv2.putText(frame, status_text, (text_x, text_y), msg_font, msg_font_scale, text_color, msg_thickness)

    # Show the frame
    display_frame = cv2.resize(frame, (640, 640))
    cv2.imshow("IP Camera Feed", display_frame)

    key = cv2.waitKey(1) & 0xFF

    if key == ord('q'):
        print("Exiting...")
        break

# ===== Cleanup =====
cap.release()
cv2.destroyAllWindows()

date_str = datetime.datetime.now().strftime("%Y-%m-%d")
attendance_file = f"attendance_{date_str}.txt"
with open(attendance_file, "w") as f:
    for name in sorted(present_today):
        f.write(f"{name}\n")

print(f"\n✅ Attendance saved to {attendance_file}")
print(f"📝 Log of attendance marks saved in {log_filename}")