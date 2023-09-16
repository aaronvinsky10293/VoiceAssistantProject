import google.cloud.texttospeech as tts
import os

credential_path = "ChatBot/spry-sensor-....json"
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path


def text_to_wav(text: str, voice_name: str = "en-US-Neural2-J"):
    """
    Converts text to speech and saves it as a WAV file.

    :param text: The text to be converted to speech.
    :param voice_name: The name of the voice to use for the speech conversion. Default is 'en-US-Neural2-J'.
    :return: None
    """
    language_code = "-".join(voice_name.split("-")[:2])
    text_input = tts.SynthesisInput(text=text)
    voice_params = tts.VoiceSelectionParams(
        language_code=language_code, name=voice_name
    )
    audio_config = tts.AudioConfig(audio_encoding=tts.AudioEncoding.LINEAR16)

    client = tts.TextToSpeechClient()
    response = client.synthesize_speech(
        input=text_input,
        voice=voice_params,
        audio_config=audio_config,
    )

    filename = f"output_voice_google.wav"
    with open(filename, "wb") as out:
        out.write(response.audio_content)
