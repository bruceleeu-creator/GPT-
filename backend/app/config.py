from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = str(DATA_DIR / "prices.db")

TARGET_PRODUCTS = [
    "GPT PLUS",
    "ChatGPT",
    "Claude",
    "Gemini",
    "Grok",
    "GPT",
]

PAYMENT_METHODS = {
    "虚拟卡": ["虚拟卡", "卡密", "激活码", "充值码", "充值卡", "礼包卡"],
    "成品号": ["成品号", "账号", "共享号", "独享号", "账号共享", "账号独享", "独立账号", "已激活"],
    "土区代充": ["土区充值", "土耳其", "土耳其区", "土区代充", "土耳其代充"],
    "美区代充": ["美区充值", "美国", "美区代充", "美国代充"],
    "港区代充": ["港区", "香港", "港区代充", "香港代充"],
    "官方直充": ["官方直充", "直充", "代充", "充值达到自己账号", "自己号"],
    "其他": [],
}

REQUEST_DELAY = (3, 7)
TIMEOUT = 30
SCHEDULE_TIME = "02:00"
