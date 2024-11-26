import streamlit as st
import openai
from gtts import gTTS
import os
import speech_recognition as sr
from docx import Document  # To handle .docx files
from PyPDF2 import PdfReader  # To handle .pdf files

# Set up your OpenAI API key
openai.api_key = 'sk-proj-SOWEfXRcOPAVA8pN7UM9T3BlbkFJdEsqOXSMrBd6KMsQSFBz'

# Generic OpenAI API Call Function with error handling
def openai_api_call(messages, max_tokens=200, temperature=0.7):
    try:
        completion = openai.chat.completions.create(
            model="gpt-4",
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return completion.choices[0].message.content.strip()
    except openai.error.OpenAIError as e:
        st.error(f"An error occurred with the OpenAI API: {e}")
        return "Sorry, I'm having trouble processing your request right now."

# Function to call OpenAI API for chat response (with context)
def get_openai_response(user_input, history, user_name, doc_content=None):
    # Restrict the assistant to only answer within the context of TGM Education and its operations
    messages = [
        {
            "role": "system", 
            "content": (
                f"You are a helpful assistant for TGM Education. "
                f"Refer to the user by the name {user_name} throughout the conversation. "
                "You should only provide answers strictly related to TGM Education, its services, offerings, processes, and any other relevant information. "
                "Do not answer or provide information on any topics outside of TGM Education's operations or scope."
            )
        }
    ]
    
    for item in history:
        messages.append({"role": "user", "content": item['user']})
        messages.append({"role": "assistant", "content": item['bot']})
    
    if doc_content:
        messages.append({"role": "system", "content": f"Here is the content of the document uploaded by the user:\n\n{doc_content}"})
    
    messages.append({"role": "user", "content": user_input})
    
    return openai_api_call(messages)

# Function to generate audio response using gTTS with a British accent
def generate_audio_response(text):
    tts = gTTS(text=text, lang='en', tld='co.uk')  # British accent
    audio_file = "response.mp3"
    tts.save(audio_file)
    return audio_file


# Function to capture voice input for a fixed time limit
def capture_voice_input():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.write("Listening... Speak now.")
        audio = recognizer.listen(source, timeout=None, phrase_time_limit=10)  # Fixed 10 seconds of listening
    return audio

# Function to extract text from a .docx file
def extract_text_from_docx(docx_file):
    doc = Document(docx_file)
    full_text = []
    for paragraph in doc.paragraphs:
        full_text.append(paragraph.text)
    return '\n'.join(full_text)

# Function to extract text from a .pdf file
def extract_text_from_pdf(pdf_file):
    pdf_reader = PdfReader(pdf_file)
    full_text = []
    for page in pdf_reader.pages:
        full_text.append(page.extract_text())
    return '\n'.join(full_text)

# Initialize session state for chat history, user details, and document content
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

if 'user_details' not in st.session_state:
    st.session_state['user_details'] = {'name': '', 'email': '', 'phone': ''}

if 'document_content' not in st.session_state:
    st.session_state['document_content'] = None

# Ask for user details
if not st.session_state['user_details']['name']:
    st.title("Welcome to the TGM Education Chatbot!")
    st.write("Please enter your details to get started.")

    # Collect user details
    name = st.text_input("Your Name", value=st.session_state['user_details']['name'])
    email = st.text_input("Your Email", value=st.session_state['user_details']['email'])
    phone = st.text_input("Your Phone Number", value=st.session_state['user_details']['phone'])

    if st.button("Submit"):
        if name and email and phone:
            st.session_state['user_details']['name'] = name
            st.session_state['user_details']['email'] = email
            st.session_state['user_details']['phone'] = phone
            st.success("Details submitted successfully!")
        else:
            st.warning("Please fill in all the fields.")
else:
    st.title(f"Welcome, {st.session_state['user_details']['name']}!")
    st.write("Feel free to ask any questions.")

    # Custom CSS for chat layout with more enhanced UI elements
    st.markdown(""" 
        <style>
        .chat-container {
            height: 450px;
            overflow-y: auto; /* Enables vertical scroll if content overflows */
            border: 1px solid #CCC;
            border-radius: 15px;
            padding: 15px;
            background-color: #f1f5f9;
            margin-bottom: 20px;
            position: relative; /* Ensure the content stays inside */
        }

        .chat-box {
            border-radius: 12px;
            padding: 12px 20px;
            margin: 10px 0;
            display: block; /* Ensures block layout for each message */
            word-wrap: break-word; /* Ensures long words wrap to the next line */
            max-width: 70%; /* Ensure the message boxes don't overflow the container */
        }

        .user-box, .bot-box {
            display: block;
            white-space: pre-wrap; /* Ensures whitespace and line breaks are preserved */
            clear: both; /* Clears float to prevent overlap */
        }

        .user-box {
            background-color: #007BFF;
            color: white;
            text-align: right;
            margin-left: auto; /* Aligns the user message to the right */
            margin-bottom: 5px;
            border-radius: 15px 0 15px 15px;
            box-shadow: 0px 3px 10px rgba(0, 123, 255, 0.2);
            overflow-wrap: break-word; /* Break long words if necessary */
        }

        .bot-box {
            background-color: #E5E5EA;
            color: black;
            text-align: left;
            margin-right: auto; /* Aligns the bot message to the left */
            margin-bottom: 5px;
            border-radius: 0 15px 15px 15px;
            box-shadow: 0px 3px 10px rgba(0, 0, 0, 0.1);
            overflow-wrap: break-word; /* Break long words if necessary */
        }

        .clear-fix {
            clear: both;
        }

        .chat-icon {
            vertical-align: middle;
            margin-right: 10px;
        }

        .user-icon {
            float: right;
        }
        </style>
        """, unsafe_allow_html=True)

    # Display chat history with icons and a clearer layout
    st.markdown('<div class="chat-container" id="chat-container">', unsafe_allow_html=True)
    if st.session_state['chat_history']:
        for chat in st.session_state['chat_history']:
            st.markdown(f'<div class="chat-box user-box"><img src="https://img.icons8.com/color/48/000000/user.png" class="chat-icon user-icon" /> {chat["user"]}</div><div class="clear-fix"></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="chat-box bot-box"><img src="https://img.icons8.com/color/48/000000/robot-2.png" class="chat-icon" /> {chat["bot"]}</div><div class="clear-fix"></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Option for user to type or speak their input
    input_option = st.radio("How would you like to provide your input?", ("Type", "Speak"))

    user_input = ""
    if input_option == "Type":
        user_input = st.text_area("Your message:", height=150, placeholder="Type your message here...")
    elif input_option == "Speak":
        if st.button("Start Speaking"):
            audio_data = capture_voice_input()
            recognizer = sr.Recognizer()
            try:
                # Recognize the speech from the audio data
                user_input = recognizer.recognize_google(audio_data)
                st.write(f"You said: {user_input}")
                st.session_state['user_input'] = user_input  # Save it in session state for consistency
            except sr.UnknownValueError:
                st.error("Sorry, I couldn't understand the audio.")
                user_input = ""
            except sr.RequestError as e:
                st.error(f"Error with the speech recognition service: {e}")
                user_input = ""

    # Button to submit user input
    if st.button("Send") and (user_input or 'user_input' in st.session_state):
        user_input = user_input or st.session_state.get('user_input', '')  # Make sure we are using the recognized input
        st.write("Bot is typing...")
        with st.spinner("Thinking..."):
            response = get_openai_response(user_input, st.session_state['chat_history'], st.session_state['user_details']['name'], st.session_state['document_content'])
            
            # Update chat history
            st.session_state['chat_history'].append({"user": user_input, "bot": response})
            
            # Generate audio response
            audio_file = generate_audio_response(response)
            
            # Provide option to play the audio (autoplay may not work in all browsers)
            st.audio(audio_file, format="audio/mp3", autoplay=True)
            
            st.success("Response received!")

    # Button to generate and download the conversation summary as a text file
    if st.button("Download Conversation Summary"):
        if st.session_state['chat_history']:
            summary_text = "\n".join([f"User: {chat['user']}\nBot: {chat['bot']}" for chat in st.session_state['chat_history']])
            
            # Provide the summary text file for download
            st.download_button(
                label="Download Summary as Text",
                data=summary_text,
                file_name="chat_summary.txt",
                mime="text/plain",
            )
        else:
            st.warning("No conversation to summarize yet.")

    # --- NEW SECTION: DOCUMENT UPLOAD AND ANALYSIS ---
    st.markdown("## Upload a Document for Analysis")
    uploaded_file = st.file_uploader("Upload a document (PDF, DOCX, or TXT)", type=["pdf", "docx", "txt"])

    if uploaded_file is not None:
        # Read the document content based on the file type
        if uploaded_file.type == "application/pdf":
            content = extract_text_from_pdf(uploaded_file)
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            content = extract_text_from_docx(uploaded_file)
        else:
            content = str(uploaded_file.read(), 'utf-8')  # For TXT files

        st.session_state['document_content'] = content
        st.success("Document uploaded successfully!")

        # Allow the user to ask specific questions about the uploaded document
        document_query = st.text_input("Ask a question about the document:")
        if st.button("Analyze Document") and document_query:
            st.write("Analyzing document...")
            with st.spinner("Analyzing..."):
                response = get_openai_response(document_query, st.session_state['chat_history'], st.session_state['user_details']['name'], st.session_state['document_content'])
                st.session_state['chat_history'].append({"user": document_query, "bot": response})
                st.success("Analysis complete!")
                st.write(response)
