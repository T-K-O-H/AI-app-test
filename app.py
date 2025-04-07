# You can find this code for Chainlit python streaming here (https://docs.chainlit.io/concepts/streaming/python)

# OpenAI Chat completion
import os
from openai import AsyncOpenAI  # importing openai for API usage
import chainlit as cl  # importing chainlit for our app
from dotenv import load_dotenv

load_dotenv()

# Changed keys from Hugging Face so we dont go broke again
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in .env file")

#ChatOpenAI Templates
system_template = """You are a friendly AI assistant who:
1. Gives short, simple answers
3. Give analogies
2. Uses everyday language
3. Avoids long explanations
4. Gets straight to the point
5. Uses simple examples
6. Keeps responses under 4-5 points when possible
7. No technical terms
8. No "sure" or similar phrases at the start
9. No unnecessary words
10. End with a question or a call to action (if appropriate)
Keep it super simple and direct!
"""
# system_template = """You are a helpful assistant who always speaks in a pleasant tone!
# """

# Add user template
user_template = """
Think through your response step by step.
Question: {user_input}
Additional Context (if any): {context} 
"""
# This is where we can add context to the user's question and make it more accurate how we want it to be
# We can also add more context to the user's question and make it more accurate how we want it to be
# example of context for that would be location age etc
#

@cl.on_chat_start  # marks a function that will be executed at the start of a user session
async def start_chat():
    settings = {
        "temperature": 1, # No temperature, just the facts
        "max_tokens": 300, # Max tokens
        "top_p": 1, # Top p, 1 is the most random words 
        "frequency_penalty": 0, #   No penalty for frequency repeating words
        "presence_penalty": 0, # No penalty for presence of words   
    }

    # Initialize conversation session history
    cl.user_session.set("settings", settings)
    cl.user_session.set("messages", [{"role": "system", "content": system_template}])
    
    
    # Welcome message
    
    await cl.Message("Hello! I'm ready to help. Send me a message!").send()


@cl.on_message  # marks a function that should be run each time the chatbot receives a message from a user
async def main(message: cl.Message):
    try:
        settings = cl.user_session.get("settings")
        messages = cl.user_session.get("messages")
        client = AsyncOpenAI(api_key=api_key)

        print(f"Received message: {message.content}")  # Debug print

        # Add user message to history


        messages.append({"role": "user", "content": message.content})

        # Create a new message
        msg = cl.Message(content="")
        await msg.send()

        # Call OpenAI
        async for chunk in await client.chat.completions.create(
            model="gpt-3.5-turbo",  # Using GPT-3.5-turbo for cost efficiency??? tried other models also
            #model="gpt-4o-mini", and cost? Not sure 3.5 seems to work better
            messages=messages,
            stream=True,
            **settings
        ):
            if chunk.choices[0].delta.content:
                print(f"Received token: {chunk.choices[0].delta.content}")  
                
                
                # Debug print

                # Stream the tokens
                await msg.stream_token(chunk.choices[0].delta.content)

        # Add assistant's response to history

        # remember prev response
        messages.append({"role": "assistant", "content": msg.content})
        cl.user_session.set("messages", messages)

        await msg.update()
    except Exception as e:
        error_msg = f"An error occurred: {str(e)}"
        print(error_msg)  
        
        
        # Debug print
        await cl.Message(content=error_msg).send()