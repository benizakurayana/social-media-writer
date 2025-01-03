import os
from pytrends.request import TrendReq
from pytrends.request import TrendReq
from googleapiclient.discovery import build


# 定義取得trending searches的function
def get_trending_searches(country_name, hl, tz=None):
    """
    :param country_name: Country name (e.g. "taiwan", "south_korea", "czech_republic", "united_states")
    :param language: Language code (e.g. "zh-TW", "zh-CN", "en-US", "en-GB", "ja-JP", "ko-KR")
    :param timezone: Timezone offset (optional, timezone offset in minutes, e.g. 0 for UTC, -300 for eastern US, 480 for Taiwan)
    :return: Trending searches
    """
    try:
        pytrends = TrendReq(hl=hl, tz=tz)
        trending_df = pytrends.trending_searches(pn=country_name)
        return trending_df[0].astype(str).tolist()[:10]
    except Exception as e:
        return f"Error fetching trends: {str(e)}"


# 定義google搜尋並製作提供給LLM的內容的function
def google_res(search_keyword):
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    GOOGLE_ENGINE_ID = os.getenv('GOOGLE_ENGINE_ID')
    # 初始化服務
    service = build("customsearch", "v1", developerKey=GOOGLE_API_KEY)
    # 執行搜索並獲取標題和摘要
    res = service.cse().list(q=search_keyword, cx=GOOGLE_ENGINE_ID).execute()
    results = []
    for item in res.get('items', []):
        title = item.get('title')
        snippet = item.get('snippet')
        results.append({'title': title, 'snippet': snippet})
    # 做成提供給LLM的內容
    content = "以下為已發生的事實：\n"
    for result in results:
        content += f"標題：{result['title']}\n摘要：{result['snippet']}\n\n"
    
    return content


# 定義function call可用的function清單。在此放兩個function，看LLM是否能正確選擇需要的function
FUNCTIONS = [{
    "type":"function",
    "function": {
        "name": "get_trending_searches",  # 函式名稱
        "description": "Fetch trending searches",  # 函式說明
        "parameters": {
            "type": "object",
            "properties": {
                "country_name": {  # 參數名稱
                    "type": "string",  # 資料型別
                    "description": 'Country name(e.g. "taiwan", "south_korea", "czech_republic", "united_states")',  # 參數說明
                },
                "hl": {  # 參數名稱
                    "type": "string",  # 資料型別
                    "description": 'Language code(e.g. "zh-TW", "zh-CN", "en-US", "en-GB", "ja-JP")',  # 參數說明
                },
                "tz": {  # 參數名稱
                    "type": "string",  # 資料型別
                    "description": 'Timezone offset(e.g. 0 for UTC, -300 for eastern US, 480 for Taiwan)', # 參數說明
                },
            },
            "required": ["country_name", "hl", "tz"], # 必要參數
        },
    }
},
{
    "type":"function",
    "function": {
        "name": "google_res",  # 函式名稱
        "description": "Google search",  # 函式說明
        "parameters": {
            "type": "object",
            "properties": {
                "search_keyword": {  # 參數名稱
                    "type": "string",  # 資料型別
                    "description": 'keyowrd to search',  # 參數說明
                }
            },
            "required": ["search_keyword"],  # 必要參數
        },
    }
}]

