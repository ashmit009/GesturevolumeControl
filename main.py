import cv2
import time
import numpy as np
import handtrackingmodule as htm
import math
import platform
print("made by ashmit dubey")
if platform.system() == "Windows":
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(
        IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = interface.QueryInterface(IAudioEndpointVolume)
    volRange = volume.GetVolumeRange()
    minVol = volRange[0]
    maxVol = volRange[1]
elif platform.system() == "Darwin":
    import osascript

    minVol = 0
    maxVol = 1


def set_volume(volume_level):
    if platform.system() == "Windows":
        volume.SetMasterVolumeLevelScalar(volume_level, None)
    elif platform.system() == "Darwin":
        osascript.osascript(f"set volume output volume {volume_level * 100}")


wCam, hCam = 640, 480

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
pTime = 0

detector = htm.handDetector(detectionCon=0.9)
vol = 0
volBar = 400  # Initial position of the volume bar
volPer = 0  # Initial volume percentage
while True:
    success, img = cap.read()
    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)
    if len(lmList) != 0:
        x1, y1 = lmList[4][1], lmList[4][2]
        x2, y2 = lmList[8][1], lmList[8][2]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (x2, y2), 15, (255, 0, 255), cv2.FILLED)
        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
        cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)

        length = math.hypot(x2 - x1, y2 - y1)
        print(length)
        if length < 40:
            cv2.circle(img, (cx, cy), 15, (0, 255, 0), cv2.FILLED)

        # Convert length to volume level
        vol = np.interp(length, [30, 150], [minVol, maxVol])
        volBar = np.interp(length, [30, 150], [400, 150])
        volPer = np.interp(length, [30, 150], [0, 100])
        set_volume(vol / maxVol if platform.system() == "Windows" else vol)

    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime

    # Draw the volume bar
    cv2.rectangle(img, (50, 150), (85, 400), (0, 255, 0), 3)
    cv2.rectangle(img, (50, int(volBar)), (85, 400), (0, 255, 0), cv2.FILLED)
    cv2.putText(img, f'{int(volPer)} %', (40, 450), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 3)

    # Display FPS
    cv2.putText(img, f'FPSofASHMIT: {int(fps)}', (40, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 3)

    cv2.imshow("ASHMITDUBEY", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
