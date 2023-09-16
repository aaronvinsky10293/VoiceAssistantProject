from google.cloud import speech
import os
import openai
import openai_key

credential_path = "ChatBot/spry-sensor-....json"
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path


def speech_to_text(
        config: speech.RecognitionConfig,
        audio: speech.RecognitionAudio,
) -> speech.RecognizeResponse:
    """
    Transcribes speech from audio using the Google Cloud Speech-to-Text API.

    :param config: A speech.RecognitionConfig object that represents the configuration for speech recognition.
    :param audio: A speech.RecognitionAudio object that represents the audio data to be transcribed.
    :return: A speech.RecognizeResponse object that contains the transcriptions of the speech.
    """
    client = speech.SpeechClient()

    # Synchronous speech recognition request
    response = client.recognize(config=config, audio=audio)

    return response


def print_response(response: speech.RecognizeResponse):
    """
    Prints the results of a speech recognition response.

    :param response: The speech recognition response to be printed.
    :type response: speech.RecognizeResponse
    :return: None
    :rtype: None
    """
    for result in response.results:
        print_result(result)


def print_result(result: speech.SpeechRecognitionResult):
    """
    Prints the speech recognition result.

    :param result: The speech recognition result object.
    :return: None
    """
    best_alternative = result.alternatives[0]
    print("-" * 80)
    print(f"language_code: {result.language_code}")
    print(f"transcript:    {best_alternative.transcript}")
    print(f"confidence:    {best_alternative.confidence:.0%}")


def stt_google(mp3_file):
    """
    :param mp3_file: path to the MP3 file to be processed
    :return: transcribed text from the given MP3 file
    """
    config = speech.RecognitionConfig(language_code="en", )

    with open(mp3_file, 'rb') as audio_file:
        audio_data = audio_file.read()

    audio = speech.RecognitionAudio(content=audio_data)


    try:
        response = speech_to_text(config, audio)
        out = response.results[0].alternatives[0].transcript
    except Exception:
        out = ""
    return out


def stt_whisper(mp3_file):
    """
    :param mp3_file: The path of the mp3 file to transcribe.
    :return: The transcript of the audio file as text.
    """
    openai.api_key = openai_key.key
    audio_file = open(mp3_file, "rb")
    transcript = openai.Audio.transcribe("whisper-1", audio_file)
    return transcript.text

