import random
import re
import sys
import threading
import textwrap
import openai
import pandas as pd
from pydub import AudioSegment
import SpeechToText
import TextToSpeech
import openai_key # file containing the openai key (can also use an environmental variable)
# from pydub.playback import play
from playsound import playsound
from tabulate import tabulate
import concurrent.futures

openai.api_key = openai_key.key

# client_name = "Aaron"

messages = [{"role": "system", "content": f""" Assume the persona of a salesperson for the company My Tax Saver, 
a firm specializing in property tax reduction. Initiate a cold call to a potential client. Begin by courteously 
introducing yourself and the company. Proceed to advertise the service, focusing on its benefits and how it can 
assist the client. Ensure the conversation flows smoothly. Remember to keep responses brief (try for at most 10 words 
at a time), providing value and maintaining the client's interest. Gauge the client's reactions and their level of 
interest throughout the conversation. Once the client expresses interest, politely and non-intrusively request their 
first and last name, along with their phone number. Make sure to verify the number and other information. If the user 
still has questions, address them. Remember, the key goal is to engage and build interest in the client while 
professionally representing your company. When you believe it's appropriate to end the call, say "END_CALL"."""}]


# messages = [
#     {"role": "system", "content": f""" Assume the persona of a receptionist for the dental clinic, BrightSmiles
#     Dental Care. Initiate a call to a patient due for a regular check-up. Introduction: Begin by courteously
#     introducing yourself and the clinic. Example: "Hello, this is Alex from BrightSmiles Dental Care." Purpose of
#     Call: Proceed to explain the purpose of the call, which is to assist the patient in scheduling their regular
#     dental check-up. Emphasize the importance of routine dental care. Ask for Information: Politely and
#     non-intrusively request the patient's first and last name to confirm you're speaking to the right individual.
#     Then, ask if now is a good time to discuss their appointment details. Keep your language casual and
#     accommodating. Appointment Details: If they consent, present a couple of available slots, being flexible with
#     morning and afternoon timings. Highlight that the clinic has taken measures to ensure patient safety, especially
#     if there are ongoing health concerns. Briefly Pause for Confirmation: After offering the times, wait for their
#     preference. Limit explanations, and if they have questions, provide concise responses (aiming for 10 words or
#     less). Elevator Pitch Opportunity: Before discussing the clinic's latest services or promotions, politely inquire
#     if they're interested in a short update about what's new at BrightSmiles. Emphasize the brief nature of this
#     update. Deliver the Elevator Pitch: If they're interested, provide a concise and appealing description of the new
#     services or promotions at BrightSmiles. This shouldn't exceed 30 seconds. Gauge Interest: Throughout the
#     conversation, pay attention to the patient's responses and enthusiasm. If they sound rushed or disinterested,
#     promptly wrap up the call. Finalizing Details: Once they've chosen an appointment time, repeat the date and time
#     to ensure clarity. Ask if they'd like a reminder via email or text. Ending the Call: When all questions have been
#     addressed and details confirmed, conclude by expressing gratitude for their time and loyalty to BrightSmiles. End
#     with a cheerful note, and say "END_CALL". Make sure to always leave room for questions, and always thank them for
#     choosing BrightSmiles Dental Care. """}
# ]


def initiate():
    """
    This method initiates a conversation by sending an initial message to the user.

    :return: None
    """
    initial_message = (f"Hi, are you interested in hearing about how "
                       f"we can save you money on your property taxes?")
    # initial_message = (f"Good day! How can we bring a brighter smile to "
    #                    f"your day?")
    messages.append({"role": "assistant", "content": initial_message})
    print_and_play_audio(initial_message)


def end_call():
    """
    Ends the call and performs necessary tasks such as playing a goodbye message, generating client information, and
    exiting the program.

    :return: None
    """
    print_and_play_audio(f"Goodbye!")
    # print_and_play_audio(f"Thank you for considering BrightSmiles Dental Care. Remember to brush and floss daily. "
    #                      f"Goodbye!")
    pretty_print("Call ended. Generating client information and exiting program...")
    client_info = chatbot(
        str(messages) + "\n\nis the client interested? whats the client information gathered -- provide "
                        "it in this format (0 is low, 100 is high). Don't use commas in additional notes column:\n\n"
                        "'name: John Doe, phone: 123-456-7890,"
                        "interest_level_score: 67.5, additional_notes: BEGIN__seemed sort of interested -- asked me to "
                        "note down that he wants to be called back Wednesday at 9am. He has 2 properties that he is "
                        "considering to bring up with us in that call__END'", True)

    client_info = remove_commas_in_additional_notes(client_info)
    pretty_print("\n\n" + client_info + "\n\n")

    client_data = parse_client_info(client_info)
    df = pd.DataFrame(client_data)
    print(tabulate(df, headers='keys', tablefmt='psql'))
    sys.exit()


def remove_commas_in_additional_notes(text):
    """
    Remove commas in the additional notes.

    :param text: The text containing the additional notes.
    :return: The text with commas removed from the additional notes.
    """
    # Find the BEGIN__...__END portion
    pattern = r"BEGIN__(.*?)__END"
    substring = re.search(pattern, text)
    if substring:
        # Remove commas from the found substring
        substring_no_commas = substring.group().replace(",", "")
        # Replace the old substring with the new one in the original text
        return text.replace(substring.group(), substring_no_commas)
    else:
        return text


def pretty_print(text, line_length=170):  # 200 characters per line here
    """
    Pretty prints the given text by wrapping lines at the specified line length.

    :param text: The text to be pretty printed.
    :param line_length: The maximum length of each line. Defaults to 170 characters.
    :return: None
    """
    print('\n'.join(textwrap.wrap(text, width=line_length)))


def parse_client_info(info_text):
    """
    Parse the client information from the given text.

    :param info_text: A string containing the client information in the format "key:value".
    :return: A list containing a dictionary with the parsed client information.
    """
    fields = info_text.split(',')
    data = {}
    for field in fields:
        key, value = [s.strip() for s in field.split(':')]

        # filtering out strings
        value = re.sub("BEGIN__", "", value)
        value = re.sub("__END", "", value)
        value = re.sub("'", "", value)
        key = re.sub("'", "", key)
        key = re.sub("'name", "", key)

        data[key] = value
    return [data]


def stream_and_speak_output(model, input_text):
    """
    Stream the output of the chat model and speak it out using text-to-speech.

    :param model: The name of the chat model.
    :param input_text: The input text for the chat model.
    :return: None
    """
    messages.append({"role": "user", "content": input_text})
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0,
        stream=True,
    )

    out_string = ""
    temp_string = ""
    count = 0
    for message in response:

        try:
            temp_string += message['choices'][0]['delta']['content']
            if ((re.search('[;:.?!]', message['choices'][0]['delta']['content']) or "END_CALL" in temp_string)
                    and temp_string):  # count % 20 == 0

                if "END_CALL" in temp_string:
                    res = temp_string
                    res = re.sub("END_CALL", "", res)
                    res = re.sub(".", "", res)
                    print_and_play_audio(res)
                    end_call()

                print(temp_string)
                song = convert_text_to_audio(temp_string)
                # play(song)
                playsound("output_voice_google.wav")
                out_string += temp_string
                temp_string = ""
            count += 1
        except Exception:
            print(" __END__")

    messages.append({"role": "assistant", "content": out_string})


def chatbot(input_text, isend=False, retries=3):
    """
    :param input_text: The input text message from the user.
    :param isend: A boolean value indicating if the conversation is ending.
    :param retries: The number of retries allowed for API calls.
    :return: The reply message generated by the chatbot.

    This method is used to interact with a chatbot powered by the OpenAI GPT-3.5 Turbo or GPT-4 models. It takes an
    input_text message from the user and returns a reply message generated by the chatbot.

    The `input_text` parameter is a string that represents the user's message.

    The `isend` parameter is an optional boolean value that indicates if the conversation is ending. By default, it is
    set to False.

    The `retries` parameter is an optional integer value that specifies the number of retries allowed for API calls. By
    default, it is set to 3.

    The method performs the following steps:

    1. Initializes the `reply_message` variable as an empty string.
    2. Creates a threading event `is_reply_available` to signal when the API call is done.
    3. Defines an inner function `api_call` that performs the API call to generate the reply message.
    4. Starts a new thread and executes the `api_call` function.
    5. Waits for 20 seconds or until the API call is done using the `is_reply_available` event.
    6. If the thread is still alive and the `reply_message` is empty or contains no alphanumeric characters, retries
    the API call recursively.
        a. Prints a retry message indicating the number of retries left.
        b. Chooses a random response message to play as a pre-response audio.
        c. Calls the `chatbot` method again with the same `input_text`, `isend=False`, and `retries` decreased by 1.
    7. If the `reply_message` is not empty, appends the assistant's reply message to the `messages` list.
    8. Returns the generated `reply_message` from the chatbot.
    """
    reply_message = ''
    is_reply_available = threading.Event()

    def api_call():
        """
        Returns the response generated by the GPT-3.5 Turbo or GPT-4 model.

        The `api_call` method is used to interact with the OpenAI GPT-3.5 Turbo or GPT-4 model and generate a response
        based on the provided input text. The generated response is then returned.

        :return: A string containing the generated response.
        """
        nonlocal reply_message
        if input_text:

            # if retries < 3:
            print(f"\n\n{retries} TRIES LEFT -- generating response\n\n")

            model = "gpt-3.5-turbo"
            if isend:
                model = "gpt-4"

            messages.append({"role": "user", "content": input_text})
            chat = openai.ChatCompletion.create(
                model=model,
                messages=messages,
                temperature=0
            )
            reply_message = chat.choices[0].message.content

        is_reply_available.set()

    thread = threading.Thread(target=api_call)
    thread.start()

    # Wait for 20 seconds or until the API call is done
    is_reply_available.wait(timeout=20)

    if thread.is_alive() and not re.search(r'\w', reply_message):
        pretty_print(f"API call taking too long. Retrying: {reply_message}")
        # If retries left, call chatbot again recursively
        if retries > 0:

            response_array = [
                "just a second.",
                "just a moment.",
                "sorry, just a second.",
            ]

            pre_res = random.choice(response_array)
            print_and_play_audio(pre_res)

            return chatbot(input_text, False, retries - 1)
        else:
            pretty_print("Max retries reached. Shutting Down")
            exit(1)

    if reply_message:
        messages.append({"role": "assistant", "content": reply_message})

    return reply_message


def convert_text_to_audio(text):
    """
    Convert given text to audio using text-to-speech.

    :param text: The text to convert to audio.
    :return: The audio as an AudioSegment object.
    """
    TextToSpeech.text_to_wav(text)
    return AudioSegment.from_wav("output_voice_google.wav")


def print_and_play_audio(text):
    """
    :param text: the text to be printed and converted to audio
    :return: None
    """
    if re.search(r'\w', text):
        pretty_print(f"output text: {text}")
        song = convert_text_to_audio(text)
        # play(song)
        playsound("output_voice_google.wav")


def reply(mp3_file):
    """
    :param mp3_file: The path to the MP3 file containing the recorded speech.
    :return: None

    This method takes an MP3 file containing recorded speech as input and performs the following actions:

    1. Converts the speech to text using either the Whisper API or the Google TTS API, based on the content of the speech.
    2. Plays a random pre-defined response to indicate that the conversion process is ongoing.
    3. Uses the Google TTS API to convert the pre-defined response to audio and plays it.
    4. Waits for the speech to text conversion to complete.
    5. Prints the input text obtained from the speech.
    6. Prints the pre-defined response played to indicate ongoing conversion.
    7. If the input text is not empty, streams the input text to the GPT-3.5 Turbo model and speaks the output.
    8. If the input text is empty, the method continues listening for more speech.

    Note: This method assumes the availability of various external modules, such as SpeechToText, TextToSpeech, openai_key, pydub, playsound, and tabulate.

    """
    text = ""

    def convert_speech_to_text():
        """
        Convert speech to text using different APIs.

        Returns:
            None
        """
        nonlocal text

        # \b(name|phone)\b
        # if chatbot asks for the name of the client
        if re.search(r'\b(name)\b', messages[-1]["content"], re.IGNORECASE):
            try:
                # print("Using Whisper API")
                # text = SpeechToText.stt_whisper(mp3_file)

                print("Using Google TTS API")
                text = SpeechToText.stt_google(mp3_file)
            except Exception:
                print("Using Google TTS API")
                text = SpeechToText.stt_google(mp3_file)
        else:
            print("Using Google TTS API")
            text = SpeechToText.stt_google(mp3_file)

    # Create an executor that will run our functions in separate threads.
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)

    # Run the functions and get Futures representing their execution.
    future1 = executor.submit(convert_speech_to_text)

    response_array = [
        "Hold on.",
        "Hold on, please.",
        "One moment.",
        "Sure.",
        "Ok.",
        "Got it."
    ]

    pre_res = random.choice(response_array)

    # song = convert_text_to_audio(pre_res)
    # play(song)

    playsound("output_voice_google.wav")

    # Wait for the speech to text conversion to complete.
    future1.result()

    pretty_print(f"input text: {text}")
    pretty_print(f"output text: {pre_res}")

    if text:
        stream_and_speak_output("gpt-3.5-turbo", text)
    else:
        print("Listening more...")
