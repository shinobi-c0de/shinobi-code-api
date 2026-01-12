from io import BytesIO
from typing import Optional

import speech_recognition as sr

# Jutsu - List of Jutsu;
JUTSU = {
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
    "talk no jutsu",
}

# Translations
TRANSLATION = {
    "影分身の術": "shadow clone jutsu",
    "口寄せの術": "summoning jutsu",
    "穢土転生": "reanimation jutsu",
    "火遁豪火球の術": "fire release fireball jutsu",
    "仙人モード": "sage mode",
    "神羅天征": "almighty push",
    # Universal pull - Correct transcript 万象天引
    # Even with Google translate web can't get it right
    # Hence went with common pronounciation
    "番匠 店員": "universal pull",  # Shop assistant
    "番匠 天然": "universal pull",  # Bansho Natural
    "自爆転生": "planetary devastation",
    "イザナギ": "izanagi",
    "イザナミ": "izanami",
    "天照": "amaterasu",
    "神威": "kamui",
    # ----------------------------------------
    # "":"release", -> English
    # "":"chidori", -> English
    # "":"sharingan", -> English
    # "":"genjutsu", -> English
    # "":"kakashi of the sharingan", -> English
    # "":"susanoo", -> English
    # "":"kamui", -> English/Japanese
    # "":"talk no jutsu" -> English
}

# Grammer - Correct the spelling of misspelled Jutsu
GRAMMAR_CORRECTIONS = {
    "illusion": "genjutsu",
    "edo tensei": "reanimation jutsu",
    "re animation jutsu": "reanimation jutsu",
    "plover": "chidori",
    "shinra tensei": "almighty push",
    "universal pool": "universal pull",
    "suicide reincarnation": "planetary devastation",
    "kamoi": "kamui",
    "lintel": "kamui",
    "susano": "susanoo",
}


def _normalize_text(text: str) -> str:
    """Apply grammar corrections to text."""
    normalized = text.lower()
    return GRAMMAR_CORRECTIONS.get(normalized, normalized)


def _recognize_in_language(
    recognizer: sr.Recognizer,
    audio_content: sr.AudioData,
    language: str,
    api_key: Optional[str] = None,
) -> str:
    """Recognize speech in specified language."""
    return recognizer.recognize_google(audio_content, language=language, key=api_key)


def recognize_speech(audio: bytes, api_key: Optional[str] = None) -> str:
    """
    Recognize and validate jutsu from audio.

    Args:
        audio: Audio data in bytes
        api_key: Optional Google Speech API key

    Returns:
        Recognized and validated jutsu name

    Raises:
        ValueError: If audio cannot be understood or jutsu is invalid
        RuntimeError: If API request fails
    """
    recognizer = sr.Recognizer()
    audio_file = BytesIO(audio)

    try:
        with sr.AudioFile(audio_file) as source:
            audio_content = recognizer.record(source)

        # Try English first
        try:
            text = _recognize_in_language(recognizer, audio_content, "en", api_key)
            normalized = _normalize_text(text)

            if normalized in JUTSU:
                return normalized

        except sr.UnknownValueError:
            pass  # Try Japanese if English fails

        # Try Japanese if English didn't work
        try:
            japanese_text = _recognize_in_language(
                recognizer, audio_content, "ja", api_key
            )

            # Translate if found in translation dict
            if japanese_text in TRANSLATION:
                english_text = TRANSLATION[japanese_text]
                normalized = _normalize_text(english_text)

                if normalized in JUTSU:
                    return normalized

            raise ValueError(f"Unrecognized jutsu (Japanese): {japanese_text}")

        except sr.UnknownValueError:
            raise ValueError("Couldn't understand audio in English or Japanese")

    except sr.UnknownValueError as e:
        raise ValueError("Couldn't understand audio") from e
    except sr.RequestError as e:
        raise RuntimeError(f"API request failed: {str(e)}") from e
