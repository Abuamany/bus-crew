import streamlit as st
from openai import OpenAI
from io import BytesIO
from PIL import Image
import base64

st.set_page_config(page_title='ORBEX AGI Vision ', page_icon='👁️')

if 'history' not in st.session_state:
    st.session_state['history'] = [{'role': 'system', 'content': 'Expert in marketing and sales and highly skilled in statistical analysis, only answering questions related to the world of marketing, sales, and their connection with statistical analysis. If there are questions outside of that, respond with: "I am an AI designed to answer questions related to the world of sales, marketing, and statistical analysis."'}]
    st.session_state['cost'] = 0.0
    st.session_state['counters'] = [0, 1]

st.markdown('ORBEX AGI VISION : MARKETING SALES ANALYTICS')

# logo
image_url = "https://cdn-icons-png.flaticon.com/512/1998/1998614.png"
st.sidebar.image(image_url, caption="", use_column_width=True)
st.sidebar.write(" This ORBEX-AGI is built using Generative AI. It can give you Marketing and Sales insights, statistical analysis and up-to-date information about any Marketing and Sales topic. This Orbex AGI  delivers knowledge on demand and for Your Value Added!")


api_key = st.text_input('OpenAI API Key', '', type='password')

# display cost
if st.session_state['cost'] > 0:
    st.info('Session Cost: ${:f}'.format(st.session_state['cost']), icon='💰')

# make tabs
chatTab, settingsTab = st.tabs(['Chat', 'Settings'])

# set openai settings
with settingsTab:
    image_detail = st.selectbox('Image Detail', ['low', 'high'])
    temperature = st.slider('Temperature', 0.0, 2.0, 0.7)
    max_tokens = st.slider('Max Token Output', 100, 1000, 300)

with chatTab:
    # optional system message
    with st.expander('System Message'):
        st.session_state['history'][0]['content'] = st.text_area('sys message',
                                                                 st.session_state['history'][0]['content'],
                                                                 label_visibility='collapsed')

    # display chat
    for msg in st.session_state['history'][1:]:
        if msg['role'] == 'user':
            with st.chat_message('user'):
                for i in msg['content']:
                    if i['type'] == 'text':
                        st.write(i['text'])
                    else:
                        with st.expander('Attached Image'):
                            img = Image.open(BytesIO(base64.b64decode(i['image_url']['url'][23:])))
                            st.image(img)
        else:
            with st.chat_message('assistant'):
                msg_content = ''.join(['  ' + char if char == '\n' else char for char in msg['content']])  # fixes display issue
                st.markdown('Assistant: ' + msg_content)

    # get user inputs
    text_input = st.text_input('Prompt', '', key=st.session_state['counters'][0])
    img_input = st.file_uploader('Images', accept_multiple_files=True, key=st.session_state['counters'][1])

    # set up button layout
    st.markdown(
        """
        <style>
            [data-testid="column"]
            {
                width: calc(33.3333% - 1rem) !important;
                flex: 1 1 calc(33.3333% - 1rem) !important;
                min-width: calc(33% - 1rem) !important;
            }
            div[data-testid="column"]:nth-of-type(2)
            {
                text-align: right;
            }
        </style>
        """, unsafe_allow_html=True
    )
    cols = st.columns(2)

    # send api request
    with cols[0]:
        if st.button('Send'):
            if not api_key:
                st.warning('API Key required')
                st.stop()
            if not (text_input or img_input):
                st.warning('You can\'t just send nothing!')
                st.stop()
            msg = {'role': 'user', 'content': []}
            if text_input:
                msg['content'].append({'type': 'text', 'text': text_input})
            for img in img_input:
                if img.name.split('.')[-1].lower() not in ['png', 'jpg', 'jpeg', 'gif', 'webp']:
                    st.warning('Only .jpg, .png, .gif, or .webp are supported')
                    st.stop()
                encoded_img = base64.b64encode(img.read()).decode('utf-8')
                msg['content'].append(
                    {
                        'type': 'image_url',
                        'image_url': {
                            'url': f'data:image/jpeg;base64,{encoded_img}',
                            'detail': image_detail
                        }
                    }
                )
            st.session_state['history'].append(msg)
            history = (
                st.session_state['history']
                if st.session_state['history'][0]['content']
                else st.session_state['history'][1:]
            )
            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model='gpt-4o-2024-05-13',
                temperature=temperature,
                max_tokens=max_tokens,
                messages=history
            )
            st.session_state['history'].append(
                {'role': 'assistant', 'content': response.choices[0].message.content}
            )
            st.session_state['cost'] += response.usage.prompt_tokens * 0.01 / 1000
            st.session_state['cost'] += response.usage.completion_tokens * 0.03 / 1000
            st.session_state['counters'] = [i+2 for i in st.session_state['counters']]
            st.rerun() 

    # clear chat history
    with cols[1]:
        if st.button('Clear'):
            st.session_state['history'] = [st.session_state['history'][0]]
            st.rerun()
