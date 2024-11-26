import streamlit as st
import openai
from gtts import gTTS
import os
import speech_recognition as sr

# Set your OpenAI API key manually
openai.api_key = "sk-proj-SOWEfXRcOPAVA8pN7UM9T3BlbkFJdEsqOXSMrBd6KMsQSFBz"

# Initialize session state for chat history
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# Function to interact with OpenAI API
def get_openai_response(user_input):
    messages = [
        {"role": "system", "content": "You are a friendly and helpful chatbot. Engage in a general conversation with the user and provide helpful, polite, and informative responses."}
    ]
    for chat in st.session_state["chat_history"]:
        messages.append({"role": "user", "content": chat["user"]})
        messages.append({"role": "assistant", "content": chat["bot"]})

    messages.append({"role": "user", "content": user_input})
    
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=200,
            temperature=0.7,
        )
        return completion.choices[0].message.content.strip()
    except openai.error.OpenAIError as e:
        return f"An error occurred: {e}"

# Function to generate audio response using gTTS
def generate_audio_response(text):
    tts = gTTS(text=text, lang="en", tld="co.uk")  # British accent
    audio_file = "response.mp3"
    tts.save(audio_file)
    return audio_file

# Chatbot title
st.title("Normal Chatbot")
st.write("Welcome to the chatbot! Feel free to have a general conversation or ask any question.")

# Display chat history
if st.session_state["chat_history"]:
    for chat in st.session_state["chat_history"]:
        st.write(f"**You:** {chat['user']}")
        st.write(f"**Bot:** {chat['bot']}")

# Option for user to type or speak their input
input_option = st.radio("How would you like to provide your input?", ("Type", "Speak"))

user_input = ""
if input_option == "Type":
    user_input = st.text_area("Your message:", placeholder="Type your message here...")
elif input_option == "Speak":
    if st.button("Start Speaking"):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            st.write("Listening... Speak now.")
            audio = recognizer.listen(source, timeout=10)
        try:
            user_input = recognizer.recognize_google(audio)
            st.write(f"You said: {user_input}")
        except sr.UnknownValueError:
            st.error("Sorry, I couldn't understand the audio.")
        except sr.RequestError as e:
            st.error(f"Error with the speech recognition service: {e}")

# Button to send user input
if st.button("Send") and user_input:
    with st.spinner("Bot is typing..."):
        response = get_openai_response(user_input)
        st.session_state["chat_history"].append({"user": user_input, "bot": response})

        # Display the response
        st.write(f"**Bot:** {response}")

        # Generate and play audio response
        audio_file = generate_audio_response(response)
        st.audio(audio_file, format="audio/mp3", autoplay=True)

# Button to clear chat history
if st.button("Clear Chat History"):
    st.session_state["chat_history"] = []
    st.success("Chat history cleared!")
