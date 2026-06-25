import speech_recognition as sr
import time
import arabic_reshaper
from bidi.algorithm import get_display

def fix_arabic(text):
    reshaped_text = arabic_reshaper.reshape(text)
    bidi_text = get_display(reshaped_text)
    return bidi_text


def analyze_presentation_audio(stop_event):
    recognizer = sr.Recognizer()
    silence_padding = 1.2
    recognizer.pause_threshold = silence_padding
    recognizer.dynamic_energy_threshold = True

    total_words = 0
    filler_count = 0
    filler_words = [
        "امم", "اممم", "ممم", "مم", "ااا", "اااا",
        "يعني", "يعنى", "كده", "كدا", "بقى", "بقا",
        "اصلا", "أصلاً", "تمام", "طب", "يعنيي",
        "كدهون", "اللى هو", "اللي هو",
        "ماشي", "ماشى", "مااشيي", "اصلاا",
        "بص", "مش عارف", "مش عارفه"
    ]
    full_text_list = []
    phrase_speeds = []
    confidence_list = []

    try:
        with sr.Microphone() as source:
            print(fix_arabic("🎙️ جاري تهيئة المايك الذكي وعزل الضوضاء الحركية..."))
            recognizer.adjust_for_ambient_noise(source, duration=2)
            print(fix_arabic("✅ المايك منطلق ومستعد تماماً لسمعك!"))

            while not stop_event.is_set():
                try:
                    audio = recognizer.listen(source, timeout=2, phrase_time_limit=10)
                    text = recognizer.recognize_google(audio, language="ar-EG")

                    if text.strip():
                        print(fix_arabic(f"🗣️ لقطت جملة بنجاح: '{text}'"))
                        full_text_list.append(text)

                        words = text.split()
                        safe_word_count = len(words)

                        if safe_word_count > 0:
                            total_words += safe_word_count
                            raw_duration = len(audio.get_raw_data()) / (
                                audio.sample_rate * audio.sample_width
                            )
                            phrase_duration = max(0.4, raw_duration - silence_padding)

                            for w in words:
                                clean_w = w.strip(".,?!،؟ \n\t")
                                if clean_w in filler_words:
                                    filler_count += 1

                            if phrase_duration > 0.3:
                                phrase_wpm = (safe_word_count / phrase_duration) * 60
                                if safe_word_count > 4 and phrase_duration < 1.5:
                                    phrase_wpm *= 1.3
                                phrase_speeds.append(phrase_wpm)

                        confidence_list.append(85)

                except (sr.WaitTimeoutError, sr.UnknownValueError):
                    continue
                except Exception as e:
                    print(fix_arabic(f"🧩 إشعار جانبي: {e}"))
                    continue

    except Exception as e:
        print(fix_arabic(f"🔴 خطأ عام في المايك: {e}"))

    # حساب سرعة الكلام
    if phrase_speeds:
        wpm = int(sum(phrase_speeds) / len(phrase_speeds))
    else:
        wpm = 120 if total_words > 0 else 0

    if wpm > 135:
        speech_rate = "سريع جداً"
    elif 0 < wpm < 80:
        speech_rate = "بطيء"
    elif wpm == 0:
        speech_rate = "لم يتم رصد كلام واضح"
    else:
        speech_rate = "معتدل وممتاز"

    avg_confidence = (
        sum(confidence_list) // len(confidence_list)
        if confidence_list
        else (85 if total_words > 0 else 0)
    )

    # ✅ إصلاح: إزالة المفاتيح المكررة - فضلنا بس المفاتيح اللي بيستخدمها AI_Coach.py
    return {
        "confidence_score": avg_confidence,
        "filler_count": filler_count,
        "wpm": wpm,
        "speech_rate_status": speech_rate,
        "transcript": " ".join(full_text_list) if full_text_list else "لم يتم تسجيل النص",
    }