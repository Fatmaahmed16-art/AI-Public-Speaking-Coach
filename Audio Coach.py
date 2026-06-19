import speech_recognition as sr
import arabic_reshaper
from bidi.algorithm import get_display
import numpy as np
import time 

recognizer=sr.Recognizer()
microphone=sr.Microphone()

recognizer.dynamic_energy_threshold=True
recognizer.dymanic_energy_adjustment_damping=0.15
recognizer.pause_threshold=3.0

filler_words = [
    "يعني",
    "اممم",
    "ااا",
    "اه",
    "آه",
    "مم",
    "بصراحة",
    "طب",
    "زي",
    "كده",
    "مثلا",
    "حرفيا",
    " بص",
    "مش عارف",
    "مش عارفه",
    "تقريبا",
    "بقى"
]

def fix_arabic(text):
    reshaped_text=arabic_reshaper.reshape(text)
    bidi_text=get_display(reshaped_text)
    return bidi_text

print(fix_arabic("🎙️ الـ Audio Coach شغال دلوقتي.. ابدأي اتكلمي والمايك بيسمعك!"))


try:
    with microphone as source:
        print(fix_arabic("⏳ جاري تجهيز المايك... (ثانية واحدة)"))
        try:recognizer.listen(source,timeout=1,phrase_time_limit=1)
        except:pass
        print(fix_arabic("اتكلمي دلوقت "))
        start_time=time.time()
        audio=recognizer.listen(source,timeout=5,phrase_time_limit=25)
        end_time=time.time()

    print(fix_arabic("جاري تحليل الصوت و تحليله لنص..."))

    #Confidint analysis

    duration_seconds=end_time - start_time - recognizer.pause_threshold
    if duration_seconds <= 0: duration_seconds=1

    raw_data=np.frombuffer(audio.get_raw_data(),dtype=np.int16)
    audio_energy=np.sqrt(np.mean(raw_data**2))

    text=recognizer.recognize_google(audio,language="ar-EG")
    print(fix_arabic(f"💬 النص اللي إنتِ قولتيه: {text}"))
    
    words_list=text.split()
    total_words=len(words_list)
    words_per_minute=int((total_words / duration_seconds) * 60)
    filler_report={}
    total_fillers=0
    cleaned_words=[]

    for word in words_list:
        w=word.replace("ى","ي").replace("ا","أ").replace("ا","إ")
        cleaned_words.append(w)
    for i in range(len(cleaned_words)):
        current_word=cleaned_words[i]
        
        if i > 0 and current_word==cleaned_words[i-1]:
            filler_report[current_word]=filler_report.get(current_word,0) + 1
            total_fillers +=1
            continue
        if current_word in filler_words:
            filler_report[current_word]=filler_report.get(current_word,0) + 1
            total_fillers +=1

    #Finall Report 

    print("\n" + fix_arabic("📊 --- تقرير الأداء الصوتي ---"))
    print(fix_arabic(f" 🔹 إجمالي حركات الحشو والتكرار:{total_fillers}"))

    for word,count in filler_report.items():
        print(fix_arabic(f"   • كلمة ({word}): اتكررت {count} مرات كحشو."))
    print("\n"+ fix_arabic(f"⏱️ --- تحليل سرعة الإلقاء والطلاقة ({words_per_minute} كلمة/دقيقة) ---"))
    if words_per_minute > 160:
        print(fix_arabic("⚠️ السرعة: بتتكلمي بسرعة عالية جداً! ده مؤشر على التوتر أو الاندفاع والتلعثم."))
    elif words_per_minute < 90:
        print(fix_arabic("⚠️ السرعة: بطيئة بزيادة ومتقطعة، وده ممكن يوحي بالخوف، التردد، أو التوتر الشديد."))
    else:
        print(fix_arabic("✔️ السرعة: سرعة طبيعية، متزنة، وتدل على الطلاقة، الثقة العالية، والتحكم."))
    
    
    print("\n" + fix_arabic("🔊 --- تحليل نبرة الصوت والاتزان ---"))

    if audio_energy < 150:
        print(fix_arabic("⚠️ نبرة الصوت: واطية جداً ومترددة (ممكن تكوني متوترة أو بعيدة عن المايك)."))
    elif 150 <= audio_energy <=800:
        print(fix_arabic("✔️ نبرة الصوت: متزنة، هادية، وتدل على الثقة والتحكم الكامل."))
    else:
        print(fix_arabic("🔥 نبرة الصوت: قوية، حماسية، وممتازة للإلقاء والعروض!"))

    print("========================================================================")

except sr.UnknownValueError:
    print(fix_arabic("❌ الـ AI مسمعش صوت واضح، جربي تتكلمي تاني بصوت أعلى."))
except sr.RequestError:
    print(fix_arabic("🌐 في مشكلة في الاتصال بالإنترنت لتحليل الصوت."))
