# Face Recognition Attendance System

This project is a face recognition-based attendance system. It uses a combination of OpenCV, face_recognition, and other Python libraries to detect and recognize faces in an IP camera stream and log attendance in real-time. The system distinguishes between authorized and unauthorized persons and provides real-time working time notifications.

## Features

- **Face Detection & Recognition**: Utilizes the `face_recognition` and OpenCV libraries to process video frames, locate faces, and compare them with a set of known faces.
- **IP Camera Integration**: Streams video from an IP camera using RTSP over FFMPEG.
- **Attendance Logging**: Automatically logs the timestamp of first detection, calculates working time for recognized faces, and saves attendance in a text file.
- **Visual Feedback**: Draws green or red rectangles on faces depending on if they are recognized (authorized) or not.
- **Audio Notification**: Plays a beep sound for recognized faces (with a cooldown to avoid multiple beeps).
- **Error Handling**: Implements a frame skipping logic and reconnect mechanism in case of camera feed failures.

## Prerequisites

- **Python 3.6+**
- **Libraries**:
  - OpenCV (`opencv-python`)
  - face_recognition
  - NumPy
  - winsound (Windows-only for audio notification)
  - Other utilities: `os`, `datetime`, `time`

*Note: For Linux/Mac users, replace `winsound` with an alternative sound library or disable beep functionality.*

## Installation

1. **Clone the repository** (if using Git):
   ```bash
   git clone <repository_url>
   cd <repository_directory>
