#Import libraries
import cv2
import numpy as np
import arabic_reshaper
import time
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from bidi.algorithm import get_display

#A function that makes Arabic text correct
def fix_arabic(text):
    return get_display(arabic_reshaper.reshape(text))

#Preparing the new Mediapipipe Tasks

model_path="face_landmarker.task"
base_options=python.BaseOptions(model_asset_path=model_path)
options=vision.FaceLandmarkerOptions(
    base_options=base_options,
    output_face_blendshapes=False,
    output_facial_transformation_matrixes=False,
    num_faces=1
)
detector=vision.FaceLandmarker.create_from_options(options)
#Start the virtual camera
cap=cv2.VideoCapture(0)
print(fix_arabic("📷 الكاميرا اشتغلت.. جربي اضحكي أو اتنرفزي وشوفي الـ AI هيقول إيه!"))

#|==============================================================================================|
#|=======📊[Key variables for calibrating and analyzing facial expressions and tension]========|
#|=============================================================================================|

#Blink rate calculation variables 👁️(Blinking)

blink_count=0   #Blink counter during the current five-seconds period
eye_closed=False   #To determine if the eye is closed in the current frame
last_blink_time=time.time()
blink_rate=0       # Blinks per minute

#Varibles for calculating head stability and movement🧠
prev_nose_x,prev_nose_y=None,None   #To store the nose coordinates of the previous frame and compare them
head_movement_score=0       #A cumulative index that expresses the degree of head shaking

#Smile analysis varibles and facial confidence
smouth_mouth=0.220   #Initial value for mouth widht

#Varibles for calculating the total display time for each case (for final report)📈

start_presentation_time=time.time()
confident_duration=0   #Time spent cultivating confidence and smiling(In seconds)
neutral_duration=0    #Time spent cultivating calmness and focus (In seconds)
tense_duraion=0      #Time spent cultivating tension (In seconds)
last_frame_time=time.time()

#Video steam loop
while cap.isOpened():
    ret, frame= cap.read()
    if not ret:
        break

    h,w, _=frame.shape
    #Converting the frame from BGR to RGB
    rgb=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
    mp_image=mp.Image(image_format=mp.ImageFormat.SRGB,data=rgb)

    #Run the model to extract facial points(landmarks)
    detection_results=detector.detect(mp_image)
    #Calculating the actual time difference between the cuurent and previous frames to accuratly compile seconds
    current_frame_time=time.time()
    frame_delta=current_frame_time - last_frame_time
    last_frame_time=current_frame_time

    #Default scenarios for each frame
    display_text="Neutral"
    color=(255,255,0)
    current_state="neutral"

    #Cheking for a face in the frame to begin the engineering analysis
    if detection_results.face_landmarks:
        landmarks=detection_results.face_landmarks[0]
        
        #1️⃣Calculating the ralative scale of the face to avoid the effects of proximity and distance from the camera.
        #Point 10 is above tje forehead and point 152 is below the chin.
        face_top=np.array([landmarks[10].x,landmarks[10].y])
        face_bottom=np.array([landmarks[152].x,landmarks[152].y])
        face_size=np.linalg.norm(face_top-face_bottom)
         
        #2️⃣Smile analysis
        mouth_left=np.array([landmarks[61].x,landmarks[61].y])
        mouth_right=np.array([landmarks[291].x,landmarks[291].y])
        live_mouth=np.linalg.norm(mouth_left-mouth_right)/face_size
        #Applying a smoothing fillter to reduce noise and momentary vibration in lighting.
        smouth_mouth=(0.8*smouth_mouth)+(0.2*live_mouth)

        #3️⃣Blink Rate
        eye_top=np.array([landmarks[159].x,landmarks[159].y])
        eye_bottom=np.array([landmarks[145].x,landmarks[145].y])
        eye_open_dist=np.linalg.norm(eye_top - eye_bottom)/face_size

        #If the distance is less than 0.045 the eye is considered closed
        if eye_open_dist<0.045:
            if not eye_closed:
                blink_count+=1
                eye_closed=True
        else:
            eye_closed=False
        
        #Update and calculate the blink rate per minute every 5 seconds to ensure the indicator's stability
        current_time=time.time()
        time_passed=current_time - last_blink_time
        if time_passed>5:
            blink_rate=(blink_count/time_passed)*60
            blink_count=0   #Reset the counter for the next cycle
            last_blink_time=current_time
        
        #4️⃣Head stability analysis
        #Point 4 represents thr tip of the nose as a crntral indicator of head movement
        nose_x,nose_y=landmarks[4].x,landmarks[4].y
        if prev_nose_x is not None:
            move_dist=np.sqrt((nose_x - prev_nose_x)**2 +(nose_y - prev_nose_y)**2/face_size)
            #Smoothing filter for calculating the overall vibration index
            head_movement_score=(0.95 * head_movement_score)+(0.05*move_dist*1000)
        prev_nose_x,prev_nose_y=nose_x,nose_y
        
        #================================================================================
        #======Decision tree and digital logic for calibrating facial expressions🧠=====
        #===============================================================================

        #First case: The confident smile (if the mouth exceeds the 0.265 barrier due to the wide smile)
        if smouth_mouth>0.265:
            display_text="Confident/Smiling'😊"
            color=(0,255,0)
            current_state="Confident"

        #Second condition: High stress (blink rate > 45 per minute or head shaking > 5.5 due to anxiety)
        elif blink_rate > 45 or head_movement_score>5.5:
            display_text="Tense/High Anxitey⚠️"
            color=(0,0,255)
            current_state="Tense"
        #Third state: Stability and formal focus (weighted normal state)
        else:
            display_text="Neutral/Calm👍"
            color=(255,255,0)
            current_state="Neutral"

        #Compile the elapsed seconds and add them to the timer for each case in order to report.
        if current_state=="Confident":
            confident_duration+=frame_delta
        elif current_state=="Tense":
            tense_duraion+=frame_delta
        else:
            neutral_duration+=frame_delta

        cv2.circle(frame,(int(landmarks[159].x*w),int(landmarks[159].y*h)),2,(0,255,0),-1)
        cv2.circle(frame,(int(landmarks[4].x*w),int(landmarks[4].y*h)),3,(0,0,255),-1)
    
    #📺 Writing live and smoothed data and indicators directly on the screen
    cv2.putText(frame, display_text, (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
    cv2.putText(frame, f"Mouth Smile:{smouth_mouth:.3f}", (30, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6,(255,255,255),1)
    cv2.putText(frame, f"Blink Rate(RPM):{blink_rate:.1f}", (30, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.6,(255,255,255),1)
    cv2.putText(frame,f"Head Jitter:{head_movement_score:.2f}",(30,150),cv2.FONT_HERSHEY_COMPLEX,0.6,(255,255,255),1)

    cv2.imshow('AI Face Expression Coach', frame)
    
    #The program will end when the 'q' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Close the camera and windows after exiting the episode
cap.release()
cv2.destroyAllWindows()

# ======================================================================================
# 📊📊 [Generating and processing the final smart report and customized feedback] 📊📊
# =======================================================================================
total_presentation_time=confident_duration+tense_duraion+neutral_duration

print("\n"+"="*50)
print(fix_arabic("📊 التقرير النهائي لتحليل الأداء ولغة الجسد للوجه 📊"))
print("="*50)
print(fix_arabic(f"⏱️ إجمالي وقت العرض الفعلي: {total_presentation_time:.1f} ثانية.\n"))

#Accurately calculate the percentages for each case based on the total seconds.
if total_presentation_time>0:
    confident_pct=(confident_duration/total_presentation_time)*100
    neutral_pct=(neutral_duration/total_presentation_time)*100
    tense_pct=(tense_duraion/total_presentation_time)*100

    print(fix_arabic(f"🔹 نسبة الثقة والابتسام الذكي (Confident): {confident_pct:.1f}%"))
    print(fix_arabic(f"🔹 نسبة التركيز والثبات الهادئ (Neutral): {neutral_pct:.1f}%"))
    print(fix_arabic(f"🔹 نسبة التحفز والتوتر الملحوظ (Tense): {tense_pct:.1f}%\n"))

    print("-"*50)
    print(fix_arabic("💡 الفيدباك والتقييم النهائي للجنة التحكيم:"))
    print('-'*50)

    #A smart rule engine to provide personalized advice to the user based on an analysis of their behavior
    if tense_pct>35:
        print(fix_arabic("🚨 ملحوظة توتر: كان هناك تسرع في حركة الرأس أو معدل رمش سريع للعين في بعض الأوقات. حاول التنفس بهدوء وتثبيت نظراتك على الجمهور/الكاميرا لتبدو أكثر ثباتاً."))
    elif confident_pct>40:
        print(fix_arabic("🌟 أداء ممتاز ومبهر! ابتسامتك وثقتك وتفاعلك الإيجابي يمنح الجمهور شعوراً بالراحة والاحترافية. حافظ على هذا الستايل دائماً."))
    elif neutral_pct>60:
        print(fix_arabic("👍 أداء رسمي ومستقر جداً. تعبيرات وجهك هادئة ومركزة، ومظهرك جاد ومحترف. يمكنك إضافة بعض الابتسامات الخفيفة لكسر الجمود وجذب انتباه اللجنة بشكل أكبر."))
    else:
        print(fix_arabic("✅ أداء متوازن ومقبول جداً. تذكر دائماً أن لغة الجسد الهادئة والابتسامة الموزونة هما مفتاح إقناع أي لجنة تحكيم."))

print('='*50)