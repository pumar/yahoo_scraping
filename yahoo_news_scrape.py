# -*- coding: utf-8 -*-


from bs4 import BeautifulSoup
import pandas as pd
import requests

url_lemma = "https://news.yahoo.co.jp/search/?p=%E8%A6%B3%E5%85%89+%E8%AA%B2%E9%A1%8C&ei=UTF-8&b="

urls = [url_lemma + str(i) for i in range(1,992,10)]


def extract_text(url,prev_text = ""):
    first_page = 0
    if prev_text == "":
        first_page = 1
    
    response = requests.get(url, proxies=proxies)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    text = (soup.find('div',class_="articleMain").text).split("\n")
    
    text = list(filter(lambda x: ("画像" not in x), text))
    text = list(map(lambda x: x.strip(),text))
    text = list(filter(None, text))
    
    p_ind = 0
    
    for index,paragraph in enumerate(text):
        if paragraph[-3:] == "ページ":
            p_ind = 1
            page_numbering = paragraph.strip()[:-3]
            current_page = page_numbering.split("/")[0]
            final_page = page_numbering.split("/")[1]
            
        """
        if "次ページは" in paragraph:
            ### Recursive call inside a nested multi-page article
            p_ind = 1
            text = text[:index]
            next_url = (soup.find("div",class_="textCenter marT10")).find('a').get('href')
            prev_text += extract_text(next_url," ".join(text))
        """
    if p_ind == 0:
        for index,paragraph in enumerate(text):
            
            if "関連記事" in paragraph:
                ### In case of single page article
                text = text[:index]
                meta_data = (soup.find("div",class_="hd").text).split("\n")
                meta_data = list(filter(None,meta_data))
                title = meta_data[0].strip()
                date = url.split("a=")[1][:8]
                return " ".join(text),title,date
            
            if paragraph[-3:] == "ページ":
                ### Last page of a multiple page article (recursion floor)
                text = text[:index -2]
                return " ".join(text)
    
    if first_page == 1:
        ### Final return in the recursion (First page)
        meta_data = (soup.find("div",class_="hd").text).split("\n")
        meta_data = list(filter(None,meta_data))
        title = meta_data[0].strip()
        date = url.split("a=")[1][:8]
        return [prev_text,title,date]
    ### String return in the middle of recursion
    return prev_text

#%%

contents = list()
for url in urls:
    
    response = requests.get(url, proxies=proxies)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    frame = soup.find("div",class_="cl")
    
    articles = frame.find_all("h2",class_="t")
    
    for article in articles:
        article_url = article.find('a').get('href')
        try:
            temp = (extract_text(article_url))
            if type(temp) == list:
                contents.append(temp)
        except:
            pass
    if len(contents) > 10:
        break
#%%


df = pd.DataFrame(contents,columns=["タイトル","日付","テキスト"])

df.to_csv('yahoo_news.csv',index=False,encoding='utf-8')

#%%


text,title,date = extract_text("https://headlines.yahoo.co.jp/article?a=20191210-59766653-business-ind")
print(len(text))
