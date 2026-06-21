import threading
import arabic_reshaper
import time
from bidi.algorithm import get_display

#Importing Moudules
from vision_module import analyze_presentation_vision
from Audio_Module import analyze_presentetion_audio

def fix_arabic(text):
    return get_display(arabic_reshaper.reshape(text))

def main():
    print("\n"+"="*60)
    print(fix_arabic("🚀 جاري بدء نظام تقييم مهارات العرض المتكامل (AI Coach)..."))
    print("="*60+"\n")

    #Take a dynamic input from the user to set the display time in minutes 📥
    try:
        print(fix_arabic("⏱️ حابب تعرض فكرتك في كام دقيقة؟ (مثال: 2 أو 5 أو 1.5 دقيقة) : "))
        user_minutes=float(input())
        if user_minutes <=0:
            user_minutes=1.0
    except ValueError:
        print(fix_arabic("⚠️ إدخال غير صحيح، سيتم ضبط الوقت الافتراضي لـ 2 دقيقة."))
        user_minutes=2.0

    #Conveting minutes into seconds
    duration_seconds=int(user_minutes*60)
    
    print(fix_arabic(f"\n🎯 تم ضبط وقت التدريب على {user_minutes} دقيقة ({duration_seconds} ثانية)."))
    print(fix_arabic("🎥 جاري فتح الكاميرا وتجهيز المايك... استعد للإلقاء!"))
    print('-'*60 + "\n")
    
    #Dictionary to store audio results
    audio_results={}

    #An intermediate function for playing audio and saving results
    def run_audio():
        nonlocal audio_results
        audio_results=analyze_presentetion_audio(duration_seconds)
    
    #Turn on audio model
    audio_thread=threading.Thread(target=run_audio)
    audio_thread.start()

    #Turn on the vision model
    vision_results=analyze_presentation_vision()

    #Wait until the audio analysis is completely finshed
    print(fix_arabic("\nجاري تجميع و تحليل البيانات النهائيه ⏳"))
    audio_thread.join()

    #=====================================================================
    #=========================FINAL REPORT================================
    #=====================================================================
    print("\n"+"="*70)
    print(fix_arabic("التقرير الشامل النهائي لقييم مهارات العرض🏆"))
    print("="*70)

    #-----Results of Vision and body language----
    print(fix_arabic("\n[تحليل لغة الجسد و التواصل البصري]👁️"))
    print(fix_arabic(f"▪️التواصل البصري (Eye Contact) :{vision_results['eye_contact_pct']}%"))
    print(fix_arabic(f"▪️ الثقة و الابتسام (Confident):{vision_results['face_confident_pct']}%"))
    print(fix_arabic(f"▪️التوتر الللحظي(Tense):{vision_results['face_tense_pct']}%"))

    #----Results of Audio-----
    print(fix_arabic("\n🎤[تحليل الاداء الصوتي]"))
    print(fix_arabic(f"▪️نبرة الصوت و الاداء :{audio_results.get('confidence_score',0)}%"))
    print(fix_arabic(f"▪️عدد كلمات الحشو :{audio_results.get('filler_words_count',0)}كلمات"))
    print(fix_arabic(f"سرعة التحدث (Speech Rate):{audio_results.get('speech_rate','N/A')}"))

    print("\n"+'-'*70)
    print(fix_arabic("الفيدباك الذكي💡"))
    print('-'*70)

    #Smart Condition that linking audio to vision model
    tense_face=vision_results["face_tense_pct"]
    fillers=audio_results.get('filler_words_count ', 0)
    eye_contact=vision_results["eye_contact_pct"]

    if tense_face > 20 and fillers > 5:
        print(fix_arabic("🚨 تقييم مدمج: التوتر كان ملحوظاً! ظهر هذا في لغة الجسد (رمش سريع/حركة رأس) وتزامن مع كثرة كلمات الحشو. خذ نفساً عميقاً وتدرب على وقفات الصمت."))
    elif eye_contact > 80 and vision_results["face_confident_pct"] > 30:
        print(fix_arabic("🌟 أداء احترافي جداً! نجحت في الحفاظ على تواصل بصري ممتاز مع ابتسامة واثقة، مما يعطي انطباعاً قوياً جداً للمستمعين."))
    else:
        print(fix_arabic("✅ أداء متوازن ومستقر. انتبه فقط لعدم التشتت البصري وحاول الحفاظ على نبرة صوت هادئة."))

    print("="*70 + "\n")

if __name__ =='__main__':
    main()

