import cv2
import os

# IP camera URL (modify based on your camera's stream URL format)
ip_camera_url = "rtsp://admin:trident@123@192.168.1.110:554/stream1"  # Example RTSP URL, change according to your camera

# Create a folder to save images
save_folder = "saved_images_cctv1"
if not os.path.exists(save_folder):
    os.makedirs(save_folder)

# Open video capture

cap = cv2.VideoCapture()
cap.open(ip_camera_url, cv2.CAP_FFMPEG)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

if not cap.isOpened():
    print("Error: Could not open the camera stream.")
    exit()

print("Press 's' to save a frame or 'q' to quit.")

frame_counter = 0  # To track saved images

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to capture a frame.")
        break

    # Display the frame in an OpenCV window
    
    cv2.imshow("IP Camera Feed", cv2.resize(frame, (640, 640)))

    # Wait for key press
    key = cv2.waitKey(1) & 0xFF

    if key == ord('s'):  # Save frame when 's' is pressed
        frame_counter += 1
        image_path = os.path.join(save_folder, f"frame_{frame_counter}.jpg")
        cv2.imwrite(image_path, frame)
        print(f"Frame saved to: {image_path}")

    elif key == ord('q'):  # Quit when 'q' is pressed
        print("Exiting...")
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
