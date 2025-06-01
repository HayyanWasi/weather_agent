import os

from agents import (
    Agent,
    Runner,
    AsyncOpenAI,
    OpenAIChatCompletionsModel,
    RunConfig
)
from agents.run import RunConfig
from agents import function_tool



import google.generativeai as genai
from dotenv import load_dotenv

from agents import function_tool
import requests
import os
import asyncio
import streamlit as st

load_dotenv()

#Local Agent setup

gemini_api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=gemini_api_key)

if not gemini_api_key:
  raise ValueError("GEMINI_API_KEY not found in userdata")

external_client = AsyncOpenAI(
    api_key = gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta",
)
model = OpenAIChatCompletionsModel(
    model = "gemini-2.0-flash",
    openai_client=external_client
)
config = RunConfig(
    model=model,
    model_provider=external_client,
    tracing_disabled=(True)

)


st.title("Weather agent")
st.header("Ask weather for any city")
#Weather tool
 
@function_tool
def get_weather(city):
  api_key = os.getenv('WEATHER_API_KEY')
  base_url="https://api.openweathermap.org/data/2.5/weather"

  params = {
      "q":city,
      "appid":api_key,
      "units":"metric"
  }
  response = requests.get(base_url, params=params)

  if response.status_code == 200:
    data= response.json()
    weather = data["weather"][0]['description'].title()
    temp=data["main"]['temp']
    return f"Weather of {city.title()}: {weather}, Temperature: {temp}C"
  else:
    print(f"Error: {response.status_code}")
    print(response.json())


agent = Agent(
    name="weather agents",
    tools=[get_weather],
    instructions="""You are a friendly assistant who can chat naturally with the user on any topic. 
If the user asks about the weather in any city, respond with accurate and clear weather information including the weather description (like “Clear Sky” or “Light Rain”), temperature in Celsius, humidity, and wind speed. Use simple and concise language.
If the user only wants specific weather details (like just temperature), provide only those details.
If you cannot find weather data or there is an error, politely inform the user about the issue.
For any other questions or conversation topics, respond normally in a friendly manner without giving weather information.
""",
    model=model

)

get_input = st.text_input("Ask weather for any city", placeholder="Enter a city (e.g., New York)")
if st.button("Get Weather"):
    if get_input:

        async def run_agent():
            result = await Runner.run(agent, get_input)
            return result.final_output if result and hasattr(result, 'final_output') else "No response received"
            
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        response = loop.run_until_complete(run_agent())
        loop.close()
            
        st.write(response)
else:
    st.error("Please enter a city name.")
