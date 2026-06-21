import streamlit as st
import threading
import time

#importing modules
from vision_module import analyze_presentation_vision
from Audio_Module import analyze_presentetion_audio

#Home page settings
st.set_page_config(page_title="AI Stage Coach",page_icon="🎤",layout="centered")

#User interface design
st.title("AI Stage Coach 🎤")
st.subheader("مدربك الشخصي بالذكاء الاصطناعي لمهارات العرض و الالقاء")
st.markdown("---")

#Take input from the user (Time selection bar)
user_minutes=st.number_input("حدد وقت العرض (بالدقائق⏱️)",min_value=0.5,max_value=15.0,value=2.0,step=0.5)
duration_seconds=int(user_minutes*60)

st.markdown("*بمجرد الضغط على زرار البدءوستفتح نافذة الكاميرا و سيبدأ الميكروفون في تسجيل أدائك*💡")

#Start button
if st.button("ابدأ التدريب الان 🚀",use_container_width=True):
    with st.spinner(f"جاري تشغيل الكاميرا والمايك لمدة {user_minutes} دقيقة... استعد!"):

        #Prepare varibles to save results
        audio_results={}

        def run_audio():
            res=analyze_presentetion_audio(duration_seconds)
            audio_results.update(res)

        #Turn on the Audio
        audio_thread=threading.Thread(target=run_audio)
        audio_thread.start()

        #Turn on the Camera
        vision_results=analyze_presentation_vision()

        #Wait for the audio to finsh
        audio_thread.join()

    #====================================================================
    #===============Show Finall Report on the web📊=====================
    #===================================================================
    st.success("انتهى التدريب بنجاح  اليك تقرير الاداء : ")
    st.markdown("---")
    
    #Split the screen into two columns to display the results
    col1,col2=st.columns(2)

    with col1:
        st.header("لغة الجسد")
        st.metric("التواصل البصري",f"{vision_results['eye_contact_pct']}%")
        st.metric("الثقة و الابتسام",f"{vision_results['face_confident_pct']}%")
        st.metric("التوتر اللحظي",f"{vision_results['face_tense_pct']}%")
    
    with col2:
        st.header("الاداء الصوتي 🎤")
        st.metric("نبرة الصوت (الثقه)",f"{audio_results.get('confidence_score',0)}%")
        st.metric("كلمات الحشو",f"{audio_results.get('filler_words_count',0)}% كلمه ")
        st.metric("سرعة التحدث",f"{audio_results.get('speech_rate','N/A')}")

    st.markdown('---')
    st.subheader('الفيدباك الذكي (AI Feedback)💡')

    tense_face=vision_results['face_tense_pct']
    fillers=audio_results.get('filler_words_count',0)
    eye_contact=vision_results['eye_contact_pct']

    if tense_face > 20 and fillers > 5:
        st.error("🚨 التوتر كان ملحوظاً! ظهر هذا في لغة الجسد وتزامن مع كثرة كلمات الحشو. خذ نفساً عميقاً وتدرب على وقفات الصمت.")
    elif eye_contact > 80 and vision_results['face_confident_pct'] >30:
        st.balloons()
        st.success("🌟 أداء احترافي جداً! نجحت في الحفاظ على تواصل بصري ممتاز مع ابتسامة واثقة، مما يعطي انطباعاً قوياً للمستمعين.")
    else:
        st.info("✅ أداء متوازن ومستقر. انتبه فقط لعدم التشتت البصري وحاول الحفاظ على نبرة صوت هادئة.")
