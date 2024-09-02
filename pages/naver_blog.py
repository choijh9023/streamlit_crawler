import requests
from bs4 import BeautifulSoup
import pandas as pd

def get_blog_item(url) :
    tmp = url.split("/")
    url = f'https://blog.naver.com/PostView.naver?blogId={tmp[-2]}&logNo={tmp[-1]}'
    res = requests.get(url)
    nick = tmp[-2]
    soup = BeautifulSoup(res.text, "html.parser")
    
    if soup.select_one(".se-title-text") :
        title = soup.select_one(".se-title-text").text
        date = soup.select_one(".se_publishDate").text
        content = soup.select_one(".se-main-container").text
    else :
        title = soup.select_one(".se_title h3").text
        date = soup.select_one(".se_publishDate").text
        content = soup.select(".se_component_wrap")[1].text
        
    title = title.replace("\n", "").replace("\u200b", "").replace("\xa0", "").replace("\t", "").replace("\r","")
    content = content.replace("\n", "").replace("\u200b", "").replace("\xa0", "").replace("\t", "").replace("\r","")
        
    return (title, nick, date, content, url)



def get_naver_blog(keyword, startdate, enddate, to_csv=False) :
    url = f'https://s.search.naver.com/p/review/48/search.naver?ssc=tab.blog.all&api_type=8&query={keyword}&start=1&nx_search_query=&nx_and_query=&nx_sub_query=&ac=1&aq=0&spq=0&sm=tab_opt&nso=so%3Add%2Cp%3Afrom{startdate}to{enddate}&prank=30&ngn_country=KR&lgl_rcode=09170128&fgn_region=&fgn_city=&lgl_lat=37.5278&lgl_long=126.9602&enlu_query=IggCADqCULhpAAAAj0RP67RmqTWRq3DkdYxhcV7F5RKpJAPG1d9ZSyMVgoc%3D&abt=&retry_count=0'

    ret = []

    while True :
        res = requests.get(url)
        res_dic = eval(res.text)
        soup = BeautifulSoup(res_dic['contents'], 'html.parser')
        if res_dic['nextUrl'] == "" :
            break
        url = res_dic['nextUrl']

        for item in soup.select('.title_area > a') :
            try :
                ret.append(get_blog_item(item['href']))
            except :
                print(item['href'])
        
    df = pd.DataFrame(ret, columns=['title', 'nick', 'date', 'content', 'url'])
    if to_csv :
        df.to_csv(f'blog_{keyword}_{startdate}_{enddate}.csv', index=False)
        


import streamlit as st

st.title("네이버 블로그 수집기")

with st.sidebar:
    keyword = st.text_input("검색어를 입력해주세요.")
    startdate = st.date_input("시작일을 선택해주세요.")
    enddate = st.date_input("종료일을 선택해주세요.")
    cb_csv = st.checkbox("CSV로 저장할까요?")
    bnt = st.button("수집하기")

df = get_naver_blog(keyword,startdate.strftime("%Y%m%d"),enddate.strftime("%Y%m%d"),cb_csv)
st.dataframe(df)