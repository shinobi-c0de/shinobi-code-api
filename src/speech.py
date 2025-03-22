import speech_recognition as sr
from io import BytesIO

# Jutsu - List of Jutsu;
jutsu = [
    "shadow clone jutsu",
    "summoning jutsu",
    "reanimation jutsu",
    "release",
    "fire release fireball jutsu",
    "chidori",
    "sage mode",
    "almighty push",
    "universal pull",
    "planetary devastation",
    "sharingan",
    "genjutsu",
    "izanagi",
    "kakashi of the sharingan",
    "izanami",
    "susanoo",
    "amaterasu",
    "kamui",
    "talk no jutsu"
   ]

# Translations
translation = {
    "影分身の術":"shadow clone jutsu",
    "口寄せの術":"summoning jutsu",
    "穢土転生":"reanimation jutsu",
    "火遁豪火球の術":"fire release fireball jutsu",
    "仙人モード":"sage mode",
    "神羅天征":"Shinra Tensei",
    # Universal pull - Correct transcript 万象天引
    # Even with Google translate web can't get it right
    # Hence went with common pronounciation
    "番匠 店員":"universal pull", # Shop assistant
    "番匠 天然":"universal pull", # Bansho Natural
    "自爆転生":"Suicide Reincarnation",
    "天照":"amaterasu",
    "イザナギ":"izanagi",
    "イザナミ":"izanami",
    # ----------------------------------------
    #"":"release", -> English
    #"":"chidori", -> English
    #"":"sharingan", -> English
    #"":"genjutsu", -> English
    #"":"kakashi of the sharingan", -> English
    #"":"susanoo", -> English
    #"":"kamui", -> English
    #"":"talk no jutsu" -> English
}

# Grammer - Correct the spelling of misspelled Jutsu
grammer = {
    "illusion":"genjutsu",
    "edo tensei":"reanimation jutsu",
    "re animation jutsu":"reanimation jutsu",
    "plover":"chidori",
    "shinra tensei":"almighty push",
    "universal pool":"universal pull",
    "suicide reincarnation":"planetary devastation",
    "kamoi":"kamui",
    "lintel":"kamui",
    "susano":"susanoo",
    }

def recognize_speech(audio, api_key):
    recognizer = sr.Recognizer()
    audio_file = BytesIO(audio)

    with sr.AudioFile(audio_file) as source:
        audio_content = recognizer.record(source)

    try:
        transcript = recognizer.recognize_google(audio_content,language="en",key=api_key)
        text = transcript.lower()

        if text in  grammer:
            Text = grammer[text]
        else:
            Text = text

        if Text not in jutsu:
            transcript = recognizer.recognize_google(audio_content,language="ja",key=api_key)

            if transcript in translation:
                translated_text = translation[transcript]
                text = translated_text.lower()
            else:
                raise ValueError(f"Translation not found for: {transcript}")

        if text in  grammer:
            Text = grammer[text]
        else:
            Text = text

        return Text

    except sr.UnknownValueError:
        raise ValueError("Couldn't understand audio")
    except sr.RequestError as e:
        raise RuntimeError(f"API request failed: {str(e)}")
