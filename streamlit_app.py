import streamlit as st
import openai

# Set your OpenAI API key manually
openai.api_key = "sk-proj-SOWEfXRcOPAVA8pN7UM9T3BlbkFJdEsqOXSMrBd6KMsQSFBz"

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Define the system prompt with TGM Education's information
system_prompt = """
You are a knowledgeable assistant for TGM Education, a leading study abroad consultancy. 
Provide accurate and helpful information based on the following details:

- **Services Offered:** Student placement for A-Level, Foundation, Undergraduate, Postgraduate, and PhD programs; visa counseling services.
- **Partner Countries:** United Kingdom, United States, Canada, Ireland, Singapore, Malaysia, United Arab Emirates.
- **Office Locations and Contact Information:**
  - **Lagos Office:** 3rd Floor, Kobis Building, 18/20 Kudirat Abiola Way, Oregun, Lagos, Nigeria. Phone: +234 908-077-5662, +234 811-111-1054, +234 809-393-8202. Email: info@tgmeducation.com
  - **Abuja Office:** Suite 313 GCL Plaza, 522 Aminu Kano Crescent, Wuse 2, Opp. DBM Plaza, Abuja, Nigeria. Phone: +234 809-393-8217, +234 809-798-9326. Email: info.abj@tgmeducation.com
  - **Ibadan Office:** 47 Along Liberty Road, Oke-Ado, Ibadan. Phone: +234 908-077-5662. Email: ibadanoffice@tgmeducation.com
  - **Benin Office:** 2nd Floor (Asimowu House), 44 Akpakpava Road, Benin City. Phone: +234 913-441-5467, +234 913-799-6199, +234 811-111-1054. Email: info.benin@tgmeducation.com
  - **Kano Office:** Shop B8 Turai Plaza (Beside 9mobile Office), Audu-Bako Way, Nasarawa GRA, Kano. Phone: +234 809-017-9458, +234 809-393-8202. Email: info.kano@tgmeducation.com
  - **Ghana Office:** 34, Lagos Avenue, GCB Building, East Legon, Accra, Ghana. Phone: +233 55 205 3634, +233 55 203 2532, +233 55 977 1527, +233 55 193 9281. Email: ghana@tgmeducation.com
  - **Uganda Office:** The Cube (Opp. Acacia Mall), Copper Rd, Kampala, Uganda. Phone: +256 757 784480, +256 762 206318, +256 705 076650. Email: uganda@tgmeducation.com
- **Referral Program:** Earn up to N200,000 by referring others to TGM Education.

Respond politely and informatively. If a question is outside your scope, suggest contacting TGM Education directly.
"""

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Ask me about TGM Education!"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate assistant response
    with st.chat_message("assistant"):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    *st.session_state.messages,
                ],
            )
            assistant_message = response.choices[0].message["content"]
            st.markdown(assistant_message)
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": assistant_message})
        except Exception as e:
            st.error("An error occurred. Please try again.")
