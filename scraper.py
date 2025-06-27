import requests
from bs4 import BeautifulSoup
import json
import datetime
import os
import re

# 星座の並び
ZODIAC_NAMES = [
    "やぎ座", "みずがめ座", "うお座", "おひつじ座", "おうし座", "ふたご座",
    "かに座", "しし座", "おとめ座", "てんびん座", "さそり座", "いて座"
]

# get BeautifulSoup
def get_bs(url):
    response = requests.get(url)
    response.encoding = response.apparent_encoding

    if response.status_code != 200:
        raise Exception(f"取得に失敗しました({url})")

    return BeautifulSoup(response.text, 'html.parser')


# LINE占い
def fetch_line_scores():
    url = "https://fortune.line.me/horoscope/"
    soup = get_bs(url)

    spans = soup.find_all("span", class_="zodiac-item_score__value__7j5aD")
    scores = [float(s.get_text(strip=True)) for s in spans]

    zodiac_list = soup.find_all("span", class_="zodiac-item_name__c4Ypu")
    zodiacs = [s.get_text(strip=True) for s in zodiac_list]
    result = {k:v for k,v in zip(zodiacs, scores)}

    return {
        "site": "LINE占い",
        "url": url,
        "scores": [result[i] for i in ZODIAC_NAMES]
    }


# 朝日新聞占い
def fetch_asahi_scores():
    url_base = "https://www.asahi.com/uranai/12seiza/"
    url_list = [
        'capricorn.html', 'aquarius.html', 'pisces.html', 'aries.html', 'taurus.html', 'gemini.html',
        'cancer.html', 'leo.html', 'virgo.html', 'libra.html', 'scorpio.html', 'sagittarius.html'
    ]
    scores = []

    for _url in url_list:
        url = f'{url_base}{_url}'
        soup = get_bs(url)

        # 「総合運」というテキストを含む <span> を探す
        span = soup.find("span", string="総合運")

        # 次の兄弟要素として <img> を取得
        img = span.find_next_sibling("img")

        # alt属性から数字を取り出す
        alt_text = img.get("alt", "")
        match = re.search(r"(\d+)ポイント", alt_text)
        point = int(match.group(1))
        scores.append(point)

    return {
        "site": "朝日新聞",
        "url": url_base,
        "scores": scores
    }

if __name__ == "__main__":
    today = datetime.date.today().isoformat()
    output = [
        fetch_line_scores(),
        fetch_asahi_scores()
    ]
    print(output)

    os.makedirs("data", exist_ok=True)
    with open(f"data/{today}.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"{today} の占いスコアを保存しました。")
