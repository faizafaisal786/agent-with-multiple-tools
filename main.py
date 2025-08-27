import os
import json
import requests
from dotenv import load_dotenv
import google.generativeai as genai

# 🔑 Load API Keys
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)


# -------------------------
# Step 1: Define Tools
# -------------------------
def add(a: int, b: int) -> int:
    """Simple addition function"""
    return a + b

def get_weather(city: str) -> str:
    """Fetch weather info from WeatherAPI"""
    url = f"http://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q={city}&aqi=no"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        temp = data["current"]["temp_c"]
        condition = data["current"]["condition"]["text"]
        return f"The weather in {city} is {temp}°C with {condition}."
    else:
        return f"Sorry, could not fetch weather for {city}."


# -------------------------
# Step 2: Agent Logic
# -------------------------
def multi_tool_agent(query: str):
    model = genai.GenerativeModel("gemini-1.5-flash")

    prompt = f"""
    You are a helpful assistant with two tools:
    1. "add(a, b)" → for math addition
    2. "get_weather(city)" → for weather questions

    If the query is about math, return JSON like:
    {{"tool": "add", "a": 5, "b": 7}}

    If the query is about weather, return JSON like:
    {{"tool": "get_weather", "city": "Karachi"}}

    Query: {query}
    """

    response = model.generate_content(prompt)
    tool_call = response.text.strip()

    print("🤖 Gemini Suggestion:", tool_call)

    try:
        tool_data = json.loads(tool_call)

        if tool_data["tool"] == "add":
            result = add(tool_data["a"], tool_data["b"])
        elif tool_data["tool"] == "get_weather":
            result = get_weather(tool_data["city"])
        else:
            result = "Unknown tool."

        return result
    except Exception as e:
        return f"Error: {e}"


# -------------------------
# Step 3: Test Cases
# -------------------------
if __name__ == "__main__":
    print(multi_tool_agent("What is 10 + 20?"))
    print(multi_tool_agent("What’s the weather in Karachi?"))
    print(multi_tool_agent("Add 7 and 13"))
    print(multi_tool_agent("Tell me the weather in Lahore"))
