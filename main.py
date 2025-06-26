import os
from dotenv import load_dotenv
from agents import Agent, Runner, OpenAIChatCompletionsModel, AsyncOpenAI
import chainlit as cl
import asyncio

load_dotenv()

@cl.on_chat_start
async def start():
    MODEL_NAME = 'gemini-2.0-flash'
    API_KEY = os.getenv('GEMINI_API_KEY')

    client = AsyncOpenAI(
        api_key = API_KEY,
        base_url = 'https://generativelanguage.googleapis.com/v1beta/openai/'
    )

    model = OpenAIChatCompletionsModel(
        model = MODEL_NAME,
        openai_client = client
    )

    cl.user_session.set('chat_history', [])

    instructor = Agent(
        name = 'Assistant',
        instructions = 'You are a helpful assistant',
        model = model
    )

    cl.user_session.set('agent', instructor)

    await cl.Message(content = 'WELCOME TO MY CHATBOT').send()

@cl.on_message
async def main(message: cl.Message):
    msg = await cl.Message(content = 'Thinking or Processing your query').send()

    instructor = cl.user_session.get('agent')
    history = cl.user_session.get('chat_history')

    history.append({'role': 'user', 'content': message.content})

    result = await Runner.run(starting_agent = instructor, input = history)

    msg.content = result.final_output
    await msg.update()

    cl.user_session.set('chat_history', result.to_input_list())

    print(result.final_output)

if __name__ == '__main__':
    asyncio.run(main())