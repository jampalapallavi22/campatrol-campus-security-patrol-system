###cd desktop
###cd campatrol
###pip install opencv-python pushbullet.py
###python back.py

import cv2
import time
from pushbullet import Pushbullet

# Pushbullet Access Token (replace with your token)
PUSHBULLET_TOKEN = 'o.TiXUIogDYjYLO73gX8sXMkdKdRIMDFfV'
pb = Pushbullet(PUSHBULLET_TOKEN)

def send_push_alert():
    pb.push_note("🚨 Campatrol Alert", "Suspicious movement detected by webcam.")
    print("[PUSH SENT] Alert sent to your devices.")

# Open the camera (0 = default laptop webcam, change to 1/2 if using USB camera)
camera_index = 0  # Change to 1 if an external USB webcam is connected and not default
cap = cv2.VideoCapture(camera_index)

if not cap.isOpened():
    print(f"[ERROR] Cannot open webcam at index {camera_index}.")
    exit()

print("[INFO] Campatrol surveillance started using webcam...")

# Read two initial frames for motion detection
ret, frame1 = cap.read()
ret, frame2 = cap.read()

ALERT_INTERVAL = 10  # Time between alerts in seconds
last_alert_time = 0

while cap.isOpened():
    # Compute frame difference
    diff = cv2.absdiff(frame1, frame2)
    gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blur, 25, 255, cv2.THRESH_BINARY)
    dilated = cv2.dilate(thresh, None, iterations=3)
    contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    suspicious = False
    for contour in contours:
        if cv2.contourArea(contour) < 1000:
            continue
        suspicious = True
        (x, y, w, h) = cv2.boundingRect(contour)
        cv2.rectangle(frame1, (x, y), (x + w, y + h), (0, 0, 255), 2)

    current_time = time.time()
    if suspicious and (current_time - last_alert_time > ALERT_INTERVAL):
        print("[ALERT] Suspicious motion detected.")
        send_push_alert()
        last_alert_time = current_time

    # Show the camera feed (comment this line for headless mode)
    cv2.imshow("Campatrol Surveillance", frame1)

    # Prepare for next loop
    frame1 = frame2
    ret, frame2 = cap.read()

    # Quit if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()
