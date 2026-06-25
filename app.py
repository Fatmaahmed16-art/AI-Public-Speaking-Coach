import sys
import os
import streamlit as st
import threading
import time

# 1. حل مشكلة الـ Import للموديلز في الفولدر الحالي
root_directory = os.path.abspath(os.path.dirname(__file__))
if root_directory not in sys.path:
    sys.path.insert(0, root_directory)

# إعدادات الصفحة الأساسية
st.set_page_config(page_title="المدرب الذكي | AI Coach", page_icon="🤖", layout="wide")

from Audio_Module import analyze_presentation_audio
from vision_module import analyze_presentation_vision

# App State
if '_app_state' not in st.__dict__:
    st._app_state = {
        'stop_event': threading.Event(),
        'audio_thread': None,
        'vision_thread': None,
        'audio_results': None,
        'vision_results': None,
        'timer_thread': None,
    }

_state = st._app_state

# تفعيل الـ Session State 
if 'is_recording' not in st.session_state:
    st.session_state.is_recording = False
if 'threads_started' not in st.session_state:
    st.session_state.threads_started = False
if 'report_ready' not in st.session_state:
    st.session_state.report_ready = False
if 'duration_seconds' not in st.session_state:
    st.session_state.duration_seconds = 120  
if 'time_remaining' not in st.session_state:
    st.session_state.time_remaining = 0


# 🔥 القائمة الجانبية الذكية للتنقل بين الـ 3 صفحات 
st.sidebar.title("📌 قائمة التطبيق")
choice = st.sidebar.radio("اختر الصفحة للذهاب إليها:", ["👋 صفحة الترحيب", "🎙️ المدرب الذكي (AI Coach)", "💡 نصائح وإرشادات"])

# ==========================================
# 🛑 الصفحة الأولى: صفحة الترحيب
# ==========================================
if choice == "👋 صفحة الترحيب":
    st.title("👋 مرحباً بك في منصة المدرب الذكي")
    st.write("هذا التطبيق مصمم خصيصاً لمساعدتك على تطوير مهارات العرض والإلقاء باستخدام تقنيات الذكاء الاصطناعي.")
    
    st.markdown("""
    ### 🚀 أقسام التطبيق المتاحة:
    1. **🎙️ المدرب الذكي (AI Coach):** لتقييم أدائك الصوتي ولغة الجسد مباشرة عبر الكاميرا والمايك والحصول على تقرير تفصيلي بالعداد التنازلي.
    2. **💡 نصائح وإرشادات:** مجموعة من النصائح الذهبية المخصصة لتحسين مهارات الإلقاء والتحدث أمام الجمهور.
    """)
    st.info("👈 استخدم القائمة الجانبية للتنقل بين الأقسام بكل سهولة!")

# ==========================================
# 🛑 الصفحة الثانية: المدرب الذكي 
# ==========================================
elif choice == "🎙️ المدرب الذكي (AI Coach)":
    
    # دالة توليد النصائح المعتمدة على الدرجات 
    def generate_feedback(audio_res, vision_res):
        strengths = []
        improvements = []
        tips = []

        # ── التواصل البصري
        eye = vision_res.get('eye_contact_pct', 0)
        if eye >= 75:
            strengths.append("👀 التواصل البصري ممتاز! كنت متواصل مع الجمهور بشكل قوي ومقنع طول الوقت.")
        elif eye >= 50:
            improvements.append("👀 التواصل البصري كان معقول بس محتاج تحسين، كنت بتبعد نظرك أحياناً.")
            tips.append("💡 حاول تقسّم الجمهور في 3 نقاط (يمين، وسط، شمال) وتتنقل بينهم بعينيك بشكل منتظم.")
        else:
            improvements.append("👀 التواصل البصري كان ضعيف، كنت بتتجنب النظر للجمهور.")
            tips.append("💡 تدرب قبل العرض قدام المراية أو صاحب وركز إنك تبص في عيون الشخص اللي قدامك.")

        # ── وضعية الجسم
        posture = vision_res.get('posture_score', 0)
        if posture >= 80:
            strengths.append("🧍 وضعية جسمك كانت ممتازة، كتفين متساويين وواقف بثقة.")
        elif posture >= 55:
            improvements.append("🧍 وضعية جسمك كانت متقلبة، في لحظات كنت بتنحني أو كتفك مايلة.")
            tips.append("💡 تخيل إن في خيط بيشدك من رأسك للسقف، ده بيساعدك تفضل واقف مستقيم.")
        else:
            improvements.append("🧍 وضعية جسمك كانت ضعيفة وبتأثر على انطباع الجمهور عنك.")
            tips.append("💡 قبل أي عرض، وقف قدام المراية وتأكد إن كتفيك مفتوحين وظهرك مستقيم لمدة دقيقتين.")

        # ── انفتاح الذراعين
        arms = vision_res.get('arms_open_pct', 0)
        if arms >= 75:
            strengths.append("👐 ذراعيك كانوا مفتوحين ومرحبين وده بيدي انطباع بالثقة والانفتاح.")
        elif arms >= 50:
            improvements.append("👐 كنت بتقفل ذراعيك أحياناً وده ممكن يديك مظهر defensive.")
            tips.append("💡 حاول تخلي إيديك متاحة وتستخدمهم في الإيماءات بدل ما تقفلهم على صدرك.")
        else:
            improvements.append("👐 ذراعيك كانوا مقفولين معظم الوقت وده بيديك مظهر دفاعي ومتوتر.")
            tips.append("💡 تدرب على استخدام إيديك في التعبير، زي إنك تعد على أصابعك لما بتقول نقاط.")

        # ── حركة الجسم
        movement = vision_res.get('movement_intensity', '')
        if 'هادئة' in movement:
            strengths.append("🧘 حركة جسمك كانت هادئة ومتزنة وده بيوحي بالاتزان والثقة.")
        elif 'عاليه' in movement or 'فرط' in movement:
            improvements.append("🏃 كنت كتير الحركة وده ممكن يشتت انتباه الجمهور عن كلامك.")
            tips.append("💡 حاول تتحرك بهدف فقط، زي لما تنتقل لنقطة جديدة في العرض، وبعدين اتثبت.")

        # ── تعبيرات الوجه
        confident_face = vision_res.get('face_confident_pct', 0)
        tense_face = vision_res.get('face_tense_pct', 0)
        if confident_face >= 60:
            strengths.append(f"😊 تعبيرات وشك كانت إيجابية ومبتسمة {confident_face}% من الوقت، وده بيجذب الجمهور.")
        elif tense_face >= 40:
            improvements.append(f"😟 وشك كان واضح عليه التوتر {tense_face}% من الوقت.")
            tips.append("💡 قبل العرض خد 3 نفسات عميقة وفكر في حاجة بتحبها، ده بيساعد وشك يسترخي.")
        else:
            improvements.append("😐 تعبيرات وشك كانت محايدة، حاول تضيف حيوية أكتر.")
            tips.append("💡 تمرن على الابتسامة الطبيعية قدام المراية، مش لازم تبقى exaggerated بس تبقى حقيقية.")

        # ── سرعة الكلام
        wpm = audio_res.get('wpm', 0)
        speech_status = audio_res.get('speech_rate_status', '')
        if speech_status == "معتدل وممتاز":
            strengths.append(f"🎙️ سرعة كلامك كانت مثالية ({wpm} كلمة/د)، الجمهور قدر يستوعب كل حاجة بتقولها.")
        elif speech_status == "سريع جداً":
            improvements.append(f"🎙️ كنت بتتكلم بسرعة كبيرة ({wpm} كلمة/د) وده بيخلي الجمهور يفوته معلومات.")
            tips.append("💡 بعد كل فكرة مهمة، خد pause لمدة ثانيتين، ده بيكسر السرعة ويخلي الكلام يترسخ.")
        elif speech_status == "بطيء":
            improvements.append(f"🎙️ كنت بتتكلم ببطء ({wpm} كلمة/د) وده ممكن يخلي الجمهور يفقد تركيزه.")
            tips.append("💡 تدرب على قراءة نص بصوت عالي بسرعة أكبر شوية يومياً لمدة 5 دقايق.")
        elif speech_status == "لم يتم رصد كلام واضح":
            improvements.append("🎙️ مش اتسجل كلام كافي، تأكد إن المايك شغال وإنت بتتكلم بصوت واضح.")

        # ── كلمات الحشو
        fillers = audio_res.get('filler_count', 0)
        if fillers == 0:
            strengths.append("🛑 مفيش كلمات حشو خالص! ده دليل على إنك متحضر ومتحكم في كلامك.")
        elif fillers <= 3:
            strengths.append(f"🛑 كلمات الحشو كانت قليلة ({fillers} بس)، كويس جداً!")
        elif fillers <= 7:
            improvements.append(f"🛑 فيه {fillers} كلمات حشو زي 'يعني' و'امم'، محتاج تقللهم.")
            tips.append("💡 لما تحس إنك هتقول 'يعني' أو 'امم'، بدلها بصمت لثانية، الصمت أقوى من الحشو.")
        else:
            improvements.append(f"🛑 فيه {fillers} كلمات حشو كتير جداً، دي أكبر حاجة محتاجة تشتغل عليها.")
            tips.append("💡 سجل نفسك وانت بتتكلم كل يوم لمدة أسبوع وارصد كلمات الحشو، الوعي بيها هو أول خطوة.")

        return strengths, improvements, tips

    def start_recording():
        st.session_state.is_recording = True
        st.session_state.threads_started = False
        st.session_state.report_ready = False
        st.session_state.time_remaining = st.session_state.duration_seconds
        _state['audio_results'] = None
        _state['vision_results'] = None
        _state['stop_event'].clear()

    def stop_recording():
        st.session_state.is_recording = False
        st.session_state.time_remaining = 0
        _state['stop_event'].set()

    # واجهة الكود
    st.title("🎙️ المدرب الذكي لمهارات العرض")

    if not st.session_state.is_recording and not st.session_state.report_ready:
        st.markdown("### ⏱️ حدد وقت العرض")
        col_min, col_sec = st.columns(2)
        with col_min:
            minutes = st.number_input("الدقايق", min_value=0, max_value=30, value=2, step=1)
        with col_sec:
            seconds = st.number_input("الثواني", min_value=0, max_value=59, value=0, step=5)

        total_seconds = int(minutes * 60 + seconds)
        st.session_state.duration_seconds = max(10, total_seconds)

        if total_seconds < 10:
            st.warning("⚠️ الوقت الأدنى هو 10 ثواني.")
        st.info(f"⏱️ مدة العرض المحددة: **{minutes} دقيقة و {seconds} ثانية**")
        st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.button("🟢 بدء التقييم", on_click=start_recording, disabled=st.session_state.is_recording, use_container_width=True)
    with col2:
        st.button("🔴 إنهاء مبكر", on_click=stop_recording, disabled=not st.session_state.is_recording, use_container_width=True)

    report_container = st.container()

    if st.session_state.is_recording and not st.session_state.threads_started:
        def run_audio():
            _state['audio_results'] = analyze_presentation_audio(_state['stop_event'])
        def run_vision():
            _state['vision_results'] = analyze_presentation_vision(_state['stop_event'])

        if _state['audio_thread'] is None or not _state['audio_thread'].is_alive():
            _state['audio_thread'] = threading.Thread(target=run_audio, daemon=True)
            _state['audio_thread'].start()
        if _state['vision_thread'] is None or not _state['vision_thread'].is_alive():
            _state['vision_thread'] = threading.Thread(target=run_vision, daemon=True)
            _state['vision_thread'].start()
        st.session_state.threads_started = True

    if st.session_state.is_recording:
        duration = st.session_state.duration_seconds
        timer_placeholder = report_container.empty()

        for remaining in range(duration, -1, -1):
            if not st.session_state.is_recording or _state['stop_event'].is_set():
                break
            mins = remaining // 60
            secs = remaining % 60
            if remaining > 10:
                timer_placeholder.info(f"🎥 التسجيل جاري... الوقت المتبقي: **{mins:02d}:{secs:02d}** |  اضغط 'إنهاء مبكر' لو خلصت قبل الوقت.")
            elif remaining > 0:
                timer_placeholder.warning(f"⚠️ اقترب الوقت! المتبقي: **{mins:02d}:{secs:02d}**")
            else:
                timer_placeholder.success("✅ انتهى وقت العرض! جاري التحليل...")
            time.sleep(1)

        if st.session_state.is_recording:
            st.session_state.is_recording = False
            _state['stop_event'].set()
            st.rerun()

    if not st.session_state.is_recording and st.session_state.threads_started and not st.session_state.report_ready:
        with report_container.spinner("⏳ جاري تجميع التقرير النهائي..."):
            for _ in range(150):
                audio_alive = _state['audio_thread'] is not None and _state['audio_thread'].is_alive()
                vision_alive = _state['vision_thread'] is not None and _state['vision_thread'].is_alive()
                if not audio_alive and not vision_alive:
                    break
                time.sleep(0.2)
        st.session_state.threads_started = False
        st.session_state.report_ready = True
        st.rerun()

    # ── عرض التقرير بـ 3 أعمدة 
    if st.session_state.report_ready and _state['audio_results'] is not None and _state['vision_results'] is not None:
        audio_res = _state['audio_results']
        vision_res = _state['vision_results']

        with report_container:
            st.success("✅ تم تجميع وتحليل البيانات بنجاح!")
            st.markdown("---")
            st.markdown("### 📊 النتائج التفصيلية")

            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.subheader("👀 لغة الجسد")
                st.metric("التواصل البصري", f"{vision_res.get('eye_contact_pct', 0)}%")
                st.metric("وضعية الجسم", f"{vision_res.get('posture_score', 0)}%")
                st.write(f"👐 انفتاح الذراعين: **{vision_res.get('arms_open_pct', 0)}%**")
                st.write(f"🏃 حركة الجسم: **{vision_res.get('movement_intensity', 'غير متوفر')}**")

            with col_b:
                st.subheader("😊 تعبيرات الوجه")
                st.metric("واثق / مبتسم", f"{vision_res.get('face_confident_pct', 0)}%")
                st.metric("متوتر", f"{vision_res.get('face_tense_pct', 0)}%")
                st.write(f"⏱️ مدة التحليل: **{vision_res.get('total_vision_time', 0)} ثانية**")

            with col_c:
                st.subheader("🎙️ الأداء الصوتي")
                st.metric("سرعة الكلام", f"{audio_res.get('wpm', 0)} كلمة/د")
                st.write(f"📊 التقييم: **{audio_res.get('speech_rate_status', 'غير معروف')}**")
                st.write(f"🛑 كلمات الحشو: **{audio_res.get('filler_count', 0)} كلمات**")

            st.markdown("---")
            with st.expander("📝 عرض الكلام الذي قلته"):
                st.info(audio_res.get('transcript', 'لم يتم تسجيل النص'))

            st.markdown("---")
            st.markdown("### 🧠 تحليل ونصايح المدرب الذكي")
            strengths, improvements, tips = generate_feedback(audio_res, vision_res)

            col_s, col_i = st.columns(2)
            with col_s:
                st.markdown("#### ✅ نقاط القوة")
                if strengths:
                    for s in strengths: st.success(s)
                else: st.info("استمري في التدريب وهتظهر نقاط قوة أكتر!")
            with col_i:
                st.markdown("#### ⚠️ نقاط تحتاج تحسين")
                if improvements:
                    for i in improvements: st.warning(i)
                else: st.success("أداء ممتاز! مفيش نقاط ضعف واضحة.")

            st.markdown("#### 💡 نصايح عملية للعرض الجاي")
            if tips:
                for t in tips: st.info(t)
            else: st.success("🎉 أداء رائع! فضلي تتمرني للحفاظ على المستوى ده.")

            st.markdown("---")
            if st.button("🔄 تقييم جديد", use_container_width=True):
                st.session_state.report_ready = False
                st.session_state.is_recording = False
                st.session_state.threads_started = False
                _state['audio_results'] = None
                _state['vision_results'] = None
                _state['stop_event'].clear()
                st.rerun()

# ==========================================
# 🛑 الصفحة الثالثة: صفحة النصائح الثابتة
# ==========================================
elif choice == "💡 نصائح وإرشادات":
    st.title("💡 نصائح ذهبية عامة لمهارات العرض والإلقاء")
    st.write("إليك أهم القواعد العامة للوصول لأداء احترافي أمام الجمهور:")
    st.success("🎯 **التواصل البصري (Eye Contact):** حاول دائماً النظر إلى عدسة الكاميرا مباشرة وليس إلى الشاشة، ليقيس السيستم تفاعلك العالي ويمنحك درجة مرتفعة.")
    st.info("🛑 **تجنب كلمات الحشو (Filler Words):** قلل من استخدام كلمات مثل (اممم، يعني، كده)، واستبدلها بسكتات خفيفة مريحة لتبدو واثقاً ومحضّراً جيداً.")
    st.warning("🏃‍♂️ **ثبات الجسد والوقوف:** اجعل وضعية كتفيك مستقيمة وحركات يديك طبيعية ومفتوحة لتعكس ثقتك الكاملة بنفسك وتتجنب المظهر الدفاعي.")