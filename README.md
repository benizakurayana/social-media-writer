---
title: Social Media Writer
emoji: ✍️
colorFrom: pink
colorTo: pink
sdk: gradio
sdk_version: 5.9.1
app_file: app.py
pinned: false
---

# Social Media Writer
- A social media trend-based post generator, which generates social media posts based on trending keywords in selected countries, 
using OpenAI's API function callings for treading searches and content generation.

- Features
  - Identifies trending keywords in a specified country.
  - Retrieves relevant search results from Google.
  - Generates a 100-word social media post in the chosen language, using OpenAI's function calling capabilities.
- Techs used in this project: Google Custom Search API, Google Trends (pytrends), OpenAI API function callings, Gradio

## View on:
- [Github](https://github.com/benizakurayana/social-media-writer)
- [Hugging Face](https://huggingface.co/spaces/benizakurayana/social-media-writer) <br>
If it says "This Space is sleeping due to inactivity," please click the "Restart this space" button

## Environment variables 
- _(友善提醒：切勿將API key直接寫在程式碼中！)_
- Save these variables to a `.env` file locally, or to `Hugging Face Spaces > space settings > Variables and secrets`:
  - OPENAI_API_KEY
  - LLM_DEPLOYMENT_NAME=gpt-4o-mini
  - GOOGLE_API_KEY
  - GOOGLE_ENGINE_ID

## Project overview
- Files:
  - Gradio App: `app.py` (Main application using Gradio for UI)  
  - Function definitions: `my_calling_functions.py` (For OpenAI function callings to choose from) 
- Flow:
  - First call of OpenAI API: Provide prompt and two function descriptions. Will receive the chosen function and arguments to use. <br>
    (Correct function choice should be pytrends, ane three arguments to use)
  - Run the chosen function with the given arguments. Will get the trending words.
  - Second call of OpenAI API: Provide prompt and two function descriptions and trending keywords. Will receive the chosen function and argument to use. <br>
    (Correct function choice should be Google search and a trending keyword as the argument)
  - Run the chosen function with the given arguments. Will get the Google search results.
  - Third call of OpenAI API: Provide the information from the previous two OpenAI API calls and executions. Will receive the generated content.

## Screenshots
![2024-12-10 17 37 55.png](screenshots/2024-12-10%2017%2037%2055.png) <br>
![2024-12-10 17 36 50.png](screenshots/2024-12-10%2017%2036%2050.png) 
