
import traceback
import streamlit as st
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
import requests
from bs4 import BeautifulSoup
from pypdf import PdfReader
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()

# 1. 부동산 투자 분석 프롬프트 
SUMMARIZE_PROMPT = """
당신은 부동산 투자 분석 전문가입니다.

아래 분양공고 또는 부동산 정보를 분석하여 다음 형식으로 답변하세요.

1. 한줄평
2. 실거주 적합도 (1~10점)
3. 투자 적합도 (1~10점)
4. 장점 3가지
5. 단점 3가지
6. 주의사항
7. 종합의견

========
{content}
========
"""

def init_page():

    st.set_page_config(
        page_title="부동산 투자 분석기",
        page_icon="🏠"
    )

    st.header("🏠 AI 부동산 투자 분석기")

    st.sidebar.title("Options")

def select_model(temperature = 0):
    models = ("gpt-5.5", "gpt-5.4-mini")
    model = st.sidebar.radio("Choose a model:", models)
    if model == 'gpt-5.5':
        return ChatOpenAI(temperature = temperature, model = 'gpt-5.5')
    else:
        return ChatOpenAI(temperature = temperature, model = 'gpt-5.4-mini')

def get_pdf_content(file):

    reader = PdfReader(file)

    text = ""

    for page in reader.pages:

        page_text = page.extract_text()

        if page_text:
            text += page_text

    return text

def init_chain():
    llm = select_model()
    prompt = ChatPromptTemplate.from_messages([
        ('user', SUMMARIZE_PROMPT)])
    chain = prompt | llm | StrOutputParser()
    return chain

def get_content(url):

    with st.spinner('웹 사이트 정보 찾는중...'):

        response = requests.get(url)

        html = BeautifulSoup(
            response.text,
            "html.parser"
        )

        if html.main:
            return html.main.get_text(
                separator=" ",
                strip=True
            )

        elif html.article:
            return html.article.get_text(
                separator=" ",
                strip=True
            )

        elif html.body:
            return html.body.get_text(
                separator=" ",
                strip=True
            )

        return ""
def main():

    init_page()

    chain = init_chain()

    uploaded_file = st.file_uploader(
        "분양공고 PDF 업로드",
        type=["pdf"]
    )

    url = st.text_input(
        "부동산 관련 URL"
    )

    content = None

    if uploaded_file:

        content = get_pdf_content(
            uploaded_file
        )

    elif url:

        content = get_content(url)

    if content:

        st.markdown("## 투자 분석 결과")

        result = chain.invoke(
            {"content": content[:15000]}
        )

        st.markdown(result)

        with st.expander("원문 보기"):

            st.write(content[:5000])

main()
