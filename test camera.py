import cv2
import math
from cvzone.FaceMeshModule import FaceMeshDetector
from cvzone.PoseModule import PoseDetector
cap = cv2.VideoCapture(0)
face_detector=FaceMeshDetector(maxFaces=1)
pose_detector=PoseDetector()

print("Starrtt ! ")

while True:
    success, frame = cap.read()

    if not success:
        cv2.waitKey(100)
        continue
    frame=cv2.flip(frame,1)
    
    posture_status="Posture : Adjusting..."
    arms_status="Arms : Adjusting..."
    eye_status="Eye Contact : Adjusting..."
# و ده جزء الاي كونتاكت و تمام فله 
    try:
        frame,faces=face_detector.findFaceMesh(frame,draw=True)
        if faces:
            face=faces[0]
            nose=face[1]
            left_cheek=face[234]
            right_cheek=face[454]

            dist_left=((nose[0]- left_cheek[0])**2 + (nose[1]-left_cheek[1])**2)**0.5
            dist_right=((nose[0]-right_cheek[0])**2 + (nose[1]-right_cheek[1])**2)**0.5
            ratio=dist_left / dist_right if dist_right !=0 else 1

        if ratio > 1.45 or ratio < 0.65:
            eye_status="Eye Contact : Distracted ❌"
        else:
            eye_status="Eye Contact : Focused ✔️"
    except:
        pass
#جزء الاكتاف و الوضعيه تماام بس مش دقيق 
    try:
        frame = pose_detector.findPose(frame,draw=True)
        lmList, bboxInfo = pose_detector.findPosition(frame,draw=False)
        if lmList and len(lmList) > 14:
            left_shoulder=lmList[11]
            right_shoulder=lmList[12]
            left_elbow=lmList[13]
            right_elbow=lmList[14]
            left_wrist=lmList[15]
            right_wrist=lmList[16]

            shoulder_width=abs(left_shoulder[0]-right_shoulder[0])
            
            if shoulder_width==0: shoulder_width=1

            shoulder_diff=abs(left_shoulder[1]-right_shoulder[1])
            if (shoulder_diff / shoulder_width) > 0.06:
                posture_status="Posture : Unbalanced Shoulder ❌ "
            else:
                posture_status="Posture : Confident & Straight ✔️ "
            
            wrist_to_elbow1=abs(right_wrist[0]-left_elbow[0])
            wrist_to_elbow2=abs(left_wrist[0]-right_elbow[0])
            
            if wrist_to_elbow1 < (shoulder_width*0.5) and wrist_to_elbow2 <(shoulder_width*0.5):
                arms_status="Arms : Crossed (Defensive) 🙅‍♀️"
            else:
                arms_status="Arms : Open & Welcoming 🙌"
    except:
        pass

    # A Nice Report
    cv2.rectangle(frame,(10,10),(420,140),(0,0,0),cv2.FILLED)
    cv2.putText(frame,eye_status,(20,40),cv2.FONT_HERSHEY_SIMPLEX,0.6,(255,255,255),2)
    cv2.putText(frame,posture_status,(20,80),cv2.FONT_HERSHEY_SIMPLEX,0.6,(255,255,255),2)
    cv2.putText(frame,arms_status,(20,120),cv2.FONT_HERSHEY_SIMPLEX,0.6,(255,255,255),2)
    
    cv2.imshow("AI Stage Coach - Bulletproof Editon",frame)

    if cv2.waitKey(5) & 0xFF == ord("q"):
        break
cap.release()
cv2.destroyAllWindows()
print("Closed")