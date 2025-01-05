from dotenv import load_dotenv
import os
import json
from openai import OpenAI
import gradio as gr
from my_calling_functions import FUNCTIONS, get_trending_searches, google_res


# Load environment variables from .env file if it exists (for local execution.)
if os.path.exists('.env'):
    load_dotenv()
LLM_DEPLOYMENT_NAME = os.getenv('LLM_DEPLOYMENT_NAME')

def llm_calls(country, output_lang):
    # OpenAI API client
    client = OpenAI()  # 無參數，即自動抓取環境變數

    # 定義query內容
    # query = f"{country}的今日熱門關鍵字有哪些，選擇一個關鍵字，選擇的方式以新聞事件或人名為優先，其次是趣味性，並以google搜尋，了解此關鍵字內容，根據內容用{output_lang}撰寫一篇100字社群貼文，第一行為標題，適度的使用表情符號作為項目符號或表達情感，並在結尾加上三個hashtag"
    query = f"Identify today's trending keywords in {country}. Select one keyword, prioritizing based on news events or personal names, \
    followed by interesting or entertaining topics. Use Google search to understand the context of the selected keyword. \
    Based on the information, write a 100-word social media post in {output_lang}, starting with a headline. \
    Use emojis appropriately as bullet points or to express emotions, and conclude the post with three hashtags."

    # 第一次呼叫OpenAI API，取回需要執行的function和參數，正解應為get_trending_searches和三個參數
    response_1 = client.chat.completions.create(
        model=LLM_DEPLOYMENT_NAME,  # 特定模型版本才有支援function calling
        messages=[{"role":"user", "content": query}],
        tools=FUNCTIONS,
        tool_choice="required"
    )
    print('===== response_1 =====')
    print(response_1)
    print('===== response_1.choices[0].message.tool_calls[0] =====')
    print(response_1.choices[0].message.tool_calls[0])

    # 為下一次呼叫OpenAI API準備function call和function call的結果
    # 因為OpenAI API不接受response.choices[0].message裡面的某些key，所以用此function保留它接受的
    def get_tool_message(response):
        tool_msg = response.choices[0].message
        tool_msg_dict = tool_msg.model_dump()

        clean_tool_msg_dict = {
            'role': tool_msg_dict['role'],
            'content': tool_msg_dict['content'],
            'tool_calls': tool_msg_dict['tool_calls']
        }
        return clean_tool_msg_dict

    tool_msg_1 = get_tool_message(response_1)
    print("===== tool_msg_1 =====")
    print(tool_msg_1)

    # 依照tool_msg_1的指示執行function
    country_name = json.loads(tool_msg_1['tool_calls'][0]['function']['arguments'])['country_name']
    hl = json.loads(tool_msg_1['tool_calls'][0]['function']['arguments'])['hl']
    tz = json.loads(tool_msg_1['tool_calls'][0]['function']['arguments'])['tz']
    function_call_result_1 = get_trending_searches(country_name, hl, tz)

    # 做成OpenAI API要的格式
    function_call_result_message_1 = {
        "role": "tool",
        "content": json.dumps(function_call_result_1, ensure_ascii=False),
        "tool_call_id": tool_msg_1['tool_calls'][0]['id'],
    }
    print("===== function_call_result_message_1 =====")
    print(function_call_result_message_1)

    # 第二次呼叫OpenAI API，取回需要執行的function和參數，正解應為google_res和一個參數
    response_2 = client.chat.completions.create(
        model=LLM_DEPLOYMENT_NAME,
        messages=[
            {"role":"user", "content": query},
            get_tool_message(response_1),  # 附上第一次呼叫的資訊
            function_call_result_message_1,
        ],
        tools=FUNCTIONS,
        tool_choice="required"
    )
    print('===== response_2 =====')
    print(response_2.choices[0].message)

    # 為下一次呼叫OpenAI API準備function call和function call的結果
    # 因為OpenAI API不接受response.choices[0].message裡面的某些key，所以用此function保留它接受的
    tool_msg_2 = get_tool_message(response_2)
    print("===== tool_msg_2 =====")
    print(tool_msg_2)

    # 依照tool_msg_2的指示執行function
    search_keyword = json.loads(tool_msg_2['tool_calls'][0]['function']['arguments'])['search_keyword']
    function_call_result_2 = google_res(search_keyword)

    # 做成OpenAI API要的格式
    function_call_result_message_2 = {
        "role": "tool",
        "content": json.dumps(function_call_result_2, ensure_ascii=False),
        "tool_call_id": tool_msg_2['tool_calls'][0]['id'],
    }
    print("===== function_call_result_message_2 =====")
    print(function_call_result_message_2)

    # 第三次呼叫OpenAI API，根據前兩次呼叫的所獲得的資訊，得出最終產出結果
    response_3 = client.chat.completions.create(
        model=LLM_DEPLOYMENT_NAME,
        messages=[
            {"role":"user", "content": query},
            # 附上第一和第二次呼叫的資訊
            get_tool_message(response_1),
            function_call_result_message_1,
            get_tool_message(response_2),
            function_call_result_message_2,
        ],
    )
    print('===== Query =====')
    print(query)
    print('===== response_3 =====')
    print(response_3)
    print('===== response_3.choices[0].message.content =====')
    print(response_3.choices[0].message.content)

    return response_3.choices[0].message.content


gradio_app = gr.Interface(
    llm_calls,
    inputs=[gr.Dropdown(
            choices=[("Taiwan", "台灣"), ("Japan", "日本"), ("South Korea", "南韓"), ("Czech Republic", "捷克")], label="Country", info="Will use current trends of this country"
        ), gr.Dropdown(
            choices=[("English", "英文"), ("Chinese", "繁體中文")], 
            label="Output Language", info="Will use this language to write"
        )],
    outputs=["textbox"],
    title="Social Media Writer",
    description=f"Generate a social media post based on the trend of the selected country, in the selected language<br />Using model: {LLM_DEPLOYMENT_NAME}"
)


if __name__ == "__main__":
    gradio_app.launch()


