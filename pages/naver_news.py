import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

st.set_page_config(page_title="뉴스수집기", page_icon=":flag-ko:")


def get_news_item(url):
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")
    title = soup.select_one("h2#title_area").text
    media = soup.select_one(".media_end_head_top_logo img")["title"]
    date = soup.select_one(".media_end_head_info_datestamp_time")["data-date-time"]
    content = soup.select_one("#newsct_article").text.replace("\n", "").replace("\t", "").replace("\r", "")
    return (title, media, date, content, url)

def get_naver_news(keyword, startdate, enddate, to_csv=False):
    ret = []
    range = pd.date_range(startdate, enddate, freq='D')
    step = 100 / len(range)
    percent_complete = 0
    my_bar = st.progress(0, "네이버 뉴스 수집 시작")
    
    for d in range:
        page = 1
        print("네이버 뉴스 수집중")
        while True:
            start = (page - 1) * 10 + 1
            url = f"https://s.search.naver.com/p/newssearch/search.naver?de={d.strftime('%Y.%m.%d')}&ds={d.strftime('%Y.%m.%d')}&eid=&field=0&force_original=&is_dts=0&is_sug_officeid=0&mynews=0&news_office_checked=&nlu_query=&nqx_theme=&nso=%26nso%3Dso%3Add%2Cp%3Afrom{d.strftime('%Y%m%d')}to{d.strftime('%Y%m%d')}%2Ca%3Aall&nx_and_query=&nx_search_hlquery=&nx_search_query=&nx_sub_query=&office_category=0&office_section_code=0&office_type=0&pd=3&photo=0&query={keyword}&query_original=&service_area=0&sort=1&spq=0&start={start}&where=news_tab_api&nso=so:dd,p:from{d.strftime('%Y%m%d')}to{d.strftime('%Y%m%d')},a:all"
            res = requests.get(url)
            li = eval(res.text)['contents']
            if len(li) == 0:
                break
            for item in li:
                soup = BeautifulSoup(item, 'html.parser')
                a_tags = soup.select("div.info_group a")
                if len(a_tags) == 2:
                    try:
                        ret.append(get_news_item(a_tags[1]['href']))
                    except:
                        print(a_tags[1]['href'])
            page += 1
        percent_complete += step
        my_bar.progress(int(percent_complete), text=f"{d.strftime('%Y-%m-%d')} ({int(percent_complete)}%) : {len(ret)}건 수집됨")

    df = pd.DataFrame(ret, columns=["title", "media", "date", "content", "url"])
    if to_csv:
        df.to_csv(f"{keyword}_{startdate.replace('.','')}_{enddate.replace('.','')}.csv", index=False)
    return df

with st.sidebar:
    keyword = st.text_input("관련 정보 검색")
    startdate = st.date_input("조회 시작일을 선택해 주세요.")
    enddate = st.date_input("조회 마지막 일을 선택해 주세요.")
    cb_csv = st.checkbox('csv 저장')
    btn = st.button("수집")

if keyword and startdate and enddate and btn:
    df = get_naver_news(keyword, startdate.strftime("%Y%m%d"), enddate.strftime("%Y%m%d"), cb_csv)
    st.dataframe(df)  # Now this is in the main page, not the sidebar
