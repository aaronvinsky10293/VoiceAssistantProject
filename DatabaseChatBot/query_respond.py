import openai
import Credentials
import TextToSpeech
from pydub import AudioSegment
from pydub.playback import play
import openai_key

# notes
# add introduction

possibleColumns = "\"Customer_ID\", \"First_Name\", \"Last_Name\", \"Email\", \"Phone_Number\", \"Section\", " \
                  "\"Block\", \"Lot\", \"Street_Address\", \"City\", \"Zip_Code\", \"Case_Status\", " \
                  "\"Expected_Savings\""

prompt = "Translate the following English text to SQL: "

response_rules = f"""
Rules for responding:
1. schema and table is "CRMFakeData"."crm_data"
2. make sure to surround column table and schema names with quotes -- case sensitive search
3. only output a sql query output
4. possible columns are: {possibleColumns}. Please keep the quotation marks in queries.
"""

introduction_prompt = f"You are a customer service representative... "

# robot_dialogue = {
#     "introduction_inbound": [
#         {"text": "Thank you for reaching out, how can I assist you today?"},
#         {"text": "Before we proceed, could you please share more about your query?"},
#         {"text": "Can I assist you with a specific question or would you like a brief overview?"},
#     ],
#     "introduction_outbound": [
#         {"text1": "Hi, am I speaking with Aaron?"},
#         {"text2": "Hi Aaron. Would you like to lower your property taxes?"},
#     ],
#     "elevator_pitch": [
#         {"text": "We're an organization dedicated to providing the best services. We guarantee effective solutions, "
#                  "and if there's no improvement, there's no fee."},
#         {"text": "The potential savings depend on various factors in your specific case. While our algorithm "
#                  "estimates a significant reduction, please note that the results can vary."},
#         {"text": "Ready to move forward? Let me guide you through the next steps."},
#     ],
#     "filler": [
#         {"text": "Okay, let's proceed."},
#         {"text": "Okay, let's look into that for you."},
#         {"text": "Currently processing your information."},
#         {"text": "Still retrieving your data, bear with me."},
#         {"text": "Alright, I'm validating the information now."},
#         {"text": "Thanks for waiting. Now, let's proceed to the next step."},
#         {"text": "Thank you for your patience."},
#         {"text": "Everything is set now. Let's proceed."},
#     ]
# }


# Function to convert speech to text using Whisper ASR API
def speech_to_text(mp3_file):
    """
    Transcribes speech from an MP3 file to text using OpenAI API.

    :param mp3_file: Path to the MP3 file.
    :return: Transcription text as a string.
    """
    openai.api_key = openai_key.key
    audio_file = open(mp3_file, "rb")
    transcript = openai.Audio.transcribe("whisper-1", audio_file)
    return transcript.text


# Function to create SQL query using GPT-3.5 API
def text_to_sql(text, response_rules, prompt):
    """
    Convert text to SQL using OpenAI GPT-3.5-turbo model.

    :param text: The input text to be converted to SQL.
    :type text: str
    :param response_rules: The response rules for the AI model.
    :type response_rules: str
    :param prompt: The prompt for the AI model.
    :type prompt: str
    :return: The converted SQL statement.
    :rtype: str
    """
    openai.api_key = openai_key.key

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": f'{response_rules}'},
            {"role": "user", "content": f'{prompt}{text}'}
        ],
        temperature=0,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    return response.choices[0].message.content


def create_connection():
    """

    This method creates a connection to a server for authentication purposes.

    :return: The connection object used for further communication with the server.

    """
    conn = Credentials.getCredentials()
    return conn


# Function to execute SQL query in Postgres database
def execute_query(sql_query, cur):
    """
    Execute a SQL query using the given cursor object.

    :param sql_query: The SQL query to be executed.
    :param cur: The cursor object to execute the query on.
    :return: The results of the query, if applicable.
    """
    cur.execute(sql_query)
    results = None
    if sql_query.strip().upper().startswith("SELECT"):
        results = cur.fetchall()  # fetch results from a SELECT statement

    return results


# Main function
def respond_to_user(mp3_file):
    """
    :param mp3_file: Path to the audio file in mp3 format
    :return: None

    This method takes in an audio file in mp3 format and performs the following tasks:
    1. Converts the speech in the audio file to text.
    2. Translates the text into a SQL query.
    3. Executes the SQL query and retrieves the output.
    4. Translates the SQL output into a readable text.
    5. Converts the text into an audio file in wav format.
    6. Plays the audio file out loud.

    Note: This method requires the necessary credentials, key, and modules to be imported.

    Example Usage:
        respond_to_user("audio_file.mp3")
    """
    # Convert speech to text
    text = speech_to_text(mp3_file)

    # text = "what's my expected savings? My name is Kevin Diaz"
    # text = "my number is +1-440-651-1484x0997 -- what's my name?"
    print(f"speech to text: {text}\n")

    # Translate text to SQL
    sql_query = text_to_sql(text, response_rules, prompt)

    print(f"text to SQL query: {sql_query}\n")

    # Execute SQL query
    conn = create_connection()
    cur = conn.cursor()
    output = execute_query(sql_query, cur)
    cur.close()
    conn.close()

    print(f"SQL query to SQL output: {str(output)}\n")

    # Translate SQL output back to pretty text
    sql_query_output = text_to_sql(f"translate sql result back into pretty english output: f{output} \n "
                                   f"btw, dont mention that this came from a sql output. please respond"
                                   f"as if you are a customer service representative", "", text)

    print(f"SQL output to text output: {sql_query_output}\n")

    # convert text to mp3:
    TextToSpeech.text_to_wav(sql_query_output)

    # play mp3 out loud
    song = AudioSegment.from_wav("output_voice_google.wav")
    play(song)


if __name__ == "__main__":
    respond_to_user('expected_savings_example.mp3')
