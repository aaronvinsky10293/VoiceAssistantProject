import speech_recognition as sr
import ChatBot
import concurrent.futures
import time


def your_Mic_Function():
    """
    This method captures audio from your microphone and sends it to a ChatBot for processing and reply.

    :return: None
    """
    while True:
        r = sr.Recognizer()
        with sr.Microphone() as source:
            r.pause_threshold = 1
            audio = r.listen(source)
            # write audio to a WAV file
            with open("output.wav", "wb") as file:
                file.write(audio.get_wav_data())

        ChatBot.reply("output.wav")

        # # Use threading to avoid the bot from hearing itself
        # threading.Thread(target=ChatBot.reply("output.wav")).start()


# Create an executor that will run our functions in separate threads.
executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)

# Run the functions and get Futures representing their execution.
future1 = executor.submit(ChatBot.initiate)

time.sleep(10.5)

print("listening")
your_Mic_Function()
