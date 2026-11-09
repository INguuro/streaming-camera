# Importing what we need
import cv2
import time
import datetime

#Give my access to the camera
cap = cv2.VideoCapture(0)

Camera_Name = "I SEE YOU"

if not cap.isOpened():
    print("Error: Cannot connect to camera")
    exit()

print("Camera connected successfully")


face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
body_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_fullbody.xml")


#Only records the video when the person starts to appear in the frame.
detection = True
detection_stopped_time = None
timer_started = False
SECONDS_TO_RECORD_AFTER_DETECTION = 10
recording = False
manual_recording = False
video_writer = None 


fourcc = cv2.VideoWriter_fourcc(*"mp4v")


# I'll get the video's frame width and height from my camera's own instead of creating my own
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
out = cv2.VideoWriter(
    'output.mp4v',
    fourcc,
    20.0,
    (frame_width, frame_height)
)

# Getting the time and day
current_time = datetime.datetime.now().strftime("%Y-%m-%d ---%H:%M:%S")


while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_width, frame_height = frame.shape[:2]
    frame_size = (frame_width, frame_height)
    resolution = f"{frame_height}x{frame_width}"

# convertting your frames into grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.2, 4)
    bodies = body_cascade.detectMultiScale(gray, 1.2, 4)

    # Face and body detection
    for (x, y, width, height) in faces:
        cv2.rectangle(frame, (x, y), (x + width, y + height), (255, 0, 0), 3)

    for (x, y, width, height) in bodies:
        cv2.rectangle(frame, (x, y), (x + width, y + height), (0, 255, 0), 3)

    # Checking if person is detected
    detected = len(faces) + len(bodies) > 0

    if detected:
        if not detection:
            detection = True
            current_time = datetime.datetime.now().strftime("%d-%m-%Y-%H-%M_%S")
            out = cv2.VideoWriter(f"{current_time}.mp4", fourcc, 20, frame_size)
            recording = True
            print("Recording started!")
            timer_started = False
            detection_stopped_time = None
    else:
        if detection and not timer_started:
            timer_started = True
            detection_stopped_time = time.time()
            print("Person Not In Sight, Video Ends In 10 seconds.")
        elif detection and timer_started:
            if time.time() - detection_stopped_time >= SECONDS_TO_RECORD_AFTER_DETECTION:
                detection = False
                timer_started = False
                recording = False
                if out.isOpened():
                    out.release()
                print("Recording Has Stopped!")

    key = cv2.waitKey(1)

    if key == ord("s"):
        filename = datetime.datetime.now().strftime("Screenshot_%Y%m%d_%H%M%S.jpg")
        cv2.imwrite(filename, frame)
        print("Screenshot Saved:", filename)

    if key == ord("r"):
        manual_recording = not manual_recording
        if manual_recording:
            print("You have begun recording")
        else:
            print("Manual Recording Has Stopped")

    auto_record = detection or manual_recording
    if auto_record:
        if not recording:
            filename = datetime.datetime.now().strftime("Video Recording Saved_%Y%m%d_%H%M%S.mp4")
            out = cv2.VideoWriter(filename, fourcc, 20.0, frame_size)
            recording = True
            print("Video Saved")
    elif recording:
        if out.isOpened():
            out.release()
        recording = False
        print("Recording Has Stopped")

    # Overlay information on the video
    resolution = f"{frame_width}x{frame_height}"
    cv2.putText(frame, Camera_Name, (20, 35),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    cv2.putText(frame, current_time, (20, 65),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    cv2.putText(frame, f"Resolution: {resolution}", (20, 95),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    if recording:
        cv2.putText(frame, "It Is Recording", (frame_width - 100, 40),
                    cv2.FONT_HERSHEY_PLAIN, 0.8, (255, 0, 0), 2)

    if out.isOpened() and recording:
        out.write(frame)
    cv2.imshow("Ich Sehe Dich", frame)

# out.release #SAVES THE VIDEO
cap.release()
cv2.destroyAllWindows()
out.release()