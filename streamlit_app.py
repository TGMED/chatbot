import streamlit as st
from openai import OpenAI

# Show title and description.
st.title("💬 TGM Education Chatbot")
st.write(
    "This chatbot is designed to answer questions related to TGM Education, "
    "such as courses, admissions, scholarships, visa requirements, and study abroad programs. "
    "To use this app, you need to provide an OpenAI API key, which you can get [here](https://platform.openai.com/account/api-keys)."
)

# Ask user for their OpenAI API key.
openai_api_key = st.text_input("OpenAI API Key", type="password")
if not openai_api_key:
    st.info("Please add your OpenAI API key to continue.", icon="🗝️")
else:
    # Create an OpenAI client.
    client = OpenAI(api_key=openai_api_key)

    # Create a session state variable to store chat messages.
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Function to check if a query is related to TGM Education.
    def is_tgm_related(query):
        keywords = [
            "TGM Education", "courses", "admissions", "scholarships",
            "visa requirements", "study abroad", "universities", "student programs"
        ]
        return any(keyword.lower() in query.lower() for keyword in keywords)

    # Display existing chat messages.
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Create a chat input field for user input.
    if prompt := st.chat_input("Ask about TGM Education, courses, or visas."):

        # Store and display the user's prompt.
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Check if the query is related to TGM Education.
        if is_tgm_related(prompt):
            # Generate a response using the OpenAI API.
            with st.chat_message("assistant"):
                try:
                    stream = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": m["role"], "content": m["content"]}
                            for m in st.session_state.messages
                        ],
                        stream=True,
                    )
                    response = st.write_stream(stream)
                except Exception as e:
                    response = "I'm sorry, I'm having trouble processing your request. Please try again later."
                    st.error(response)
            # Store the assistant's response in session state.
            st.session_state.messages.append({"role": "assistant", "content": response})
        else:
            # Provide a predefined response for unrelated queries.
            response = (
                "I can only answer questions related to TGM Education, such as courses, "
                "admissions, scholarships, visa requirements, or study abroad programs. "
                "Please ask a relevant question."
            )
            with st.chat_message("assistant"):
                st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
