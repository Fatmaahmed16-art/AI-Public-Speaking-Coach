import cv2
import numpy as np
import time
import arabic_reshaper
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from bidi.algorithm import get_display
from cvzone.PoseModule import PoseDetector

def fix_arabic(text):
    return get_display(arabic_reshaper.reshape(text))

def analyze_presentation_vision():
    """
    👁️🎬 موديول الرؤية المدمج الشامل
    يقوم بفتح الكاميرا وتحليل: تعبيرات الوجه، الرمش، هزة الرأس، التواصل البصري، وضعية الأكتاف، وحركة الأيدي.
    يعود بقاموس (Dictionary) يحتوي على النسب المئوية النهائية للتقرير الشامل.
    """

    #Face landmarker & Pose Landmarker
    model_path="face_landmarker.task"
    base_options=python.BaseOptions(model_asset_path=model_path)
    options=vision.FaceLandmarkerOptions(
        base_options=base_options,
        output_face_blendshapes=False,
        output_facial_transformation_matrixes=False,
        num_faces=1
    )
    face_detector=vision.FaceLandmarker.create_from_options(options)
    pose_detector=PoseDetector()

    cap=cv2.VideoCapture(0)
    print(fix_arabic("🎥 موديول الرؤية المتكامل يعمل الآن... الكاميرا مفتوحة!"))


    confident_duration=0
    neutral_duration=0
    tense_duration=0
    last_frame_time=time.time()

    focused_frames=0
    distracted_frames=0
    total_valid_frame=0

    blink_count=0
    eye_closed=False
    last_blink_time=time.time()
    blink_rate=0

    prev_nose_x,prev_nose_y=None,None
    head_movement_score=0
    smooth_mouth=0.220

    while cap.isOpened():
        ret,frame=cap.read()
        if not ret:
            break
    
        frame=cv2.flip(frame,1)
        h,w,_=frame.shape

        current_frame_time=time.time()
        frame_delta=current_frame_time - last_frame_time
        last_frame_time=current_frame_time

        eye_status="Eye Contact : Adjusting..."
        posture_status="Posture : Adjusting..."
        arms_status="Arms : Adjusting..."
        face_status="Neutral"

        color_face=(255,255,0)
        current_state="neutral"


        rgb=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
        mp_image=mp.Image(image_format=mp.ImageFormat.SRGB,data=rgb)

        detection_results=face_detector.detect(mp_image)

        if detection_results.face_landmarks:
            landmarks=detection_results.face_landmarks[0]
            total_valid_frame+=1

            face_top=np.array([landmarks[10].x,landmarks[10].y])
            face_bottom=np.array([landmarks[152].x,landmarks[152].y])
            face_size=np.linalg.norm(face_top - face_bottom)

            nose_pt=np.array([landmarks[4].x*w,landmarks[4].y*w])
            left_cheek_pt=np.array([landmarks[234].x*w,landmarks[234].y*w])
            right_cheek_pt=np.array([landmarks[454].x*w,landmarks[454].y*w])

            dist_left=np.linalg.norm(nose_pt - left_cheek_pt)
            dist_right=np.linalg.norm(nose_pt - right_cheek_pt)
            ratio=dist_left/dist_right if dist_right !=0 else 1

            if ratio>1.45 or ratio<0.65:
                eye_status="Eye Contact : Distracted "
                distracted_frames+=1
            else:
                eye_status="Eye Contact : Focused"
                focused_frames+=1

            mouth_left=np.array([landmarks[61].x,landmarks[61].y])
            mouth_right=np.array([landmarks[291].x,landmarks[291].y])
            live_mouth=np.linalg.norm(mouth_left - mouth_right) / face_size
            smooth_mouth=(0.8 * smooth_mouth)+(0.2 * live_mouth)

            #Blink Rate
            eye_top=np.array([landmarks[159].x,landmarks[159].y])
            eye_bottom=np.array([landmarks[145].x,landmarks[145].y])
            eye_open_dist=np.linalg.norm(eye_top - eye_bottom) / face_size

            if eye_open_dist < 0.045:
                if not eye_closed:
                    blink_rate+=1
                    eye_closed=True
            else:
                eye_closed=False

            current_time=time.time()
            time_passed=current_time - last_blink_time
            if time_passed>4:
                blink_rate=(blink_count/ time_passed)*60
                blink_count=0
                last_blink_time=current_time
            

            nose_x,nose_y=landmarks[4].x,landmarks[4].y
            if prev_nose_x is not None:
                move_dist=np.sqrt((nose_x - prev_nose_x)**2 + (nose_y - prev_nose_y)**2)/face_size
                head_movement_score=(0.7 * head_movement_score)+(0.3 * move_dist * 1000)
            else:
                head_movement_score=0
            prev_nose_x,prev_nose_y=nose_x,nose_y

            if smooth_mouth>0.265:
                face_status="Confident/Smiling "
                color_face=(0,255,0)
                current_state="Confident"
            elif blink_rate>32.0 or head_movement_score>3.8:
                face_status="Tense/High Anxiety"
                color_face=(0,0,255)
                current_state="Tense"
            else:
                face_status="Neutral/Calm"
                color_face=(255,255,0)
                current_state="neutral"

            if current_state=="Confident":
                confident_duration+=frame_delta
            elif current_state=="Tense":
                tense_duration+=frame_delta
            else:
                neutral_duration+=frame_delta
        else:
            prev_nose_x,prev_nose_y=None,None
            head_movement_score=0

        frame=pose_detector.findPose(frame,draw=False)
        lmList,bboxInfo=pose_detector.findPosition(frame,draw=False)

        if lmList and len(lmList)>16:

            left_shoulder=lmList[11]
            right_shoulder=lmList[12]
            left_elbow=lmList[13]
            right_elbow=lmList[14]
            left_wrist=lmList[15]
            right_wrist=lmList[16]

            shoulder_widht=abs(left_shoulder[0]-right_shoulder[0])
            if shoulder_widht==0: shoulder_widht=1
            shoulder_diff=abs(left_shoulder[1]-right_shoulder[1])
            if (shoulder_diff/shoulder_widht) > 0.06:
                posture_status="Posture : Unbalanced Shoulder "
            else:
                posture_status="Posture : Confident & Straight "

            wrist_to_elbow1=abs(right_wrist[0]-left_elbow[0])
            wrist_to_elbow2=abs(left_wrist[0]-right_elbow[0])

            if wrist_to_elbow1 < (shoulder_widht * 0.5) and wrist_to_elbow2 < (shoulder_widht * 0.5):
                arms_status="Arms : Crossed (Defensive)"
            else:
                arms_status="Arms : open & Welcoming "

        cv2.rectangle(frame,(10,10),(320,125),(0,0,0),cv2.FILLED)
        cv2.putText(frame,eye_status,(20,30),cv2.FONT_HERSHEY_COMPLEX,0.45,(255,255,255),1)
        cv2.putText(frame,posture_status,(20,50),cv2.FONT_HERSHEY_COMPLEX,0.45,(255,255,255),1)
        cv2.putText(frame,arms_status,(20,70),cv2.FONT_HERSHEY_COMPLEX,0.45,(255,255,255),1)

        cv2.putText(frame,f"Face Status:{face_status}",(20,90), cv2.FONT_HERSHEY_COMPLEX,0.45,color_face,1)
        cv2.putText(frame,f"Blink Rate:{blink_rate:.1f} RPM",(20,110),cv2.FONT_HERSHEY_COMPLEX,0.45,(200,200,200),1)

        cv2.imshow("AI Stage Coach - Integrated Vision Module",frame)

        if cv2.waitKey(5) & 0xFF ==ord("q"):
            break
        
    cap.release()
    cv2.destroyAllWindows()

    total_time=confident_duration + neutral_duration + tense_duration
    eye_contact_percentage=(focused_frames / total_valid_frame * 100) if total_valid_frame > 0 else 0.0
    
    confident_pct=(confident_duration / total_time * 100) if total_time >0 else 0.0
    neutral_pct=(neutral_duration / total_time * 100) if total_time >0 else 0.0
    tense_pct=(tense_duration / total_time * 100) if total_time > 0 else 0.0

    return {
        "eye_contact_pct":round(eye_contact_percentage,1),
        "face_confident_pct":round(confident_pct,1),
        "face_neutral_pct":round(neutral_pct,1),
        "face_tense_pct":round(tense_pct,1),
        "total_vision_time":round(total_time,1)
    }
if __name__=="__main__":
    results=analyze_presentation_vision()
    print(fix_arabic("\n🏁 رؤية الكاميرا انتهت. النتائج المستخرجة:"))
    print(results)