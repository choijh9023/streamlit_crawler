import streamlit as st 
import datetime as dt
import requests
import pandas as pd


def get_stockprice(code, sdt, edt) :
  URL = "https://m.stock.naver.com/front-api/external/chart/domestic/info?symbol={0}&requestType=1&startTime={1}&endTime={2}&timeframe=day".format(code, sdt, edt)
  print(URL)
  res = requests.get(URL)
  li = eval(res.text.replace("\n","").replace("\t",""))
  return pd.DataFrame(columns=li[0],data=li[1:])


st.set_page_config(page_title='멀티페이지 예제(메인)', page_icon=":shark:")
st.title('주식 차트')

with st.sidebar:
  sd = st.date_input("조회 시작일을 선택해 주세요", dt.datetime(2024, 1, 1))
  ed = st.date_input("조회 종료일을 선택해 주세요", dt.datetime(2024, 1, 1))
  code = st.text_input('종목코드를 입력해주세요.')

if sd and ed and code :
    df = get_stockprice(code, sd.strftime('%Y%m%d'), ed.strftime('%Y%m%d'))
    st.dataframe(df)
    
    st.line_chart(df['종가'])
    st.bar_chart(df['거래량'])



