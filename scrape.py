#https://cfo.economictimes.indiatimes.com/rss/topstories

import requests
from bs4 import BeautifulSoup
import pandas as pd
import spacy
import re
import nltk
import mysql.connector
from urllib.request import urlopen
from textblob import TextBlob
from nltk.sentiment import SentimentIntensityAnalyzer
from fuzzywuzzy import fuzz


url_link = "https://www.moneycontrol.com/rss/latestnews.xml"

# https://www.moneycontrol.com/rss/latestnews.xml
#r = requests.get('https://cfo.economictimes.indiatimes.com/rss/topstories')
# https://www.moneycontrol.com/rss/MCtopnews.xml
response = requests.get(url_link)
print("***********************",url_link)
print(response.status_code)

soup = BeautifulSoup(response.content, "xml")

links = [link.text.strip() for link in soup.find_all("link")]


def get_link_content(link):
    try:
        response = urlopen(link)
        response.raise_for_status()
        html = response.read()
        soup = BeautifulSoup(html, 'html.parser')
        # Extract the text content from HTML
        text = soup.get_text(separator=' ')
        return text
    except Exception as e:
        print(f"Error retrieving content from {link}: {str(e)}")
        return ""
    
# def extract_company_names(content, company_names_list):
#     company_names = []
#     for name in company_names_list:
#         regex = re.compile(r'\b' + re.escape(name) + r'\b', re.IGNORECASE)
#         if regex.search(content):
#             company_names.append(name)
#     return company_names

# def main():
#     link = "https://example.com"  # Replace with the link you want to scrape
#     company_names_list = ["company1", "company2", "company3"]  # Replace with your list of company names

#     content = get_link_content(link)
#     if content:
#         extracted_company_names = extract_company_names(content, company_names_list)
#         if extracted_company_names:
#             print("Extracted Company Names:")
#             for name in extracted_company_names:
#                 print(name)
#         else:
#             print("No company names found in the link content.")
#     else:
#         print("Failed to retrieve content from the link.")

# if __name__ == "__main__":
#     main()

    
df = pd.read_excel("C:/Users/accti/Downloads/List Of Companies v0 (1).xlsx")
company_names = df["Security Name"].str.lower().tolist()
company_names_ID = df["Security Id"].str.lower().tolist()
industry_names = df["Industry"].str.lower().tolist()

    
data = []
title = soup.select("title")  # Example CSS selector
link = soup.select("link")
description = soup.select("description")
pubdate = soup.select("pubDate")
#sentiment = sentiment



#nlp = spacy.load("en_core_web_sm")

for link, title, description, pubdate in zip(links, title, description, pubdate):
    content = get_link_content(link)
    if content:
        blob = TextBlob(content)
        sentiment = blob.sentiment.polarity

        sentiment_label = ""

        print(f"Sentiment analysis for {link}:")
        if sentiment > 0.1:            #0.14489715077950371
            sentiment_label = "Positive"
        elif sentiment < 0.1:
            sentiment_label = "Negative"
        else:
            sentiment_label = "Neutral"


        title_text = title.text.strip()
        description_text = description.text.strip()

        # title_company_names = [name.lower() for name in company_names if re.search(r'\b' + re.escape(name.lower()) + r'\b', title.text.lower())]
        # description_company_names = [name.lower() for name in company_names if re.search(r'\b' + re.escape(name.lower()) + r'\b', description.text.lower())]
        def process_company_name(name):
            return re.sub(r"[-_=$]", " ", name.lower())
        
        processed_company_names = [process_company_name(name) for name in company_names]
        #print("********************************",processed_company_names)

        link_company_names = [name for name in processed_company_names if fuzz.token_set_ratio(process_company_name(link), name) >= 75]
        title_company_names = [name for name in processed_company_names if fuzz.token_set_ratio(process_company_name(title_text), name) >= 75]
        description_company_names = [name for name in processed_company_names if fuzz.token_set_ratio(process_company_name(description_text), name) >= 75]


        #title_company_names = [name for name in company_names if fuzz.partial_ratio(title_text.lower(), name.lower()) >= 80]
        #print("**********************",title_company_names)
        #description_company_names = [name for name in company_names if fuzz.partial_ratio(description_text.lower(), name.lower()) >= 80]
        #print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@",description_company_names)
        # title_company_names = [name for name in company_names if re.search(r'\b' + re.escape(name) + r'\b', title_text, re.IGNORECASE)]
        # #print("***************77777777777777777********************",title_company_names)
        # description_company_names = [name for name in company_names if re.search(r'\b' + re.escape(name) + r'\b', description_text, re.IGNORECASE)]
        # #print("***************7070707070********************",description_company_names)
        company = list(set( link_company_names + title_company_names + description_company_names))
        # company = [name for name in (title_company_names + description_company_names) if name]
        # print("____________8181811_________________",company)
        # if not company:  # Check if the company list is empty
        #     company_names_str = "TBD"  # Set an empty string for company_names_str
        # else:
        #     company_names_str = ", ".join(company)
        company_names_str = ", ".join(company)
        print("Matched Company Names:", company_names_str)

        industry = []
        for name in company:
            try:
                idx = processed_company_names.index(name)
                industry_name = industry_names[idx]
                industry.append(industry_name)
            except ValueError:
                industry.append("Unknown")
        

        #industry = [industry_names[company_names.index(name)] for name in company]
        industry_str = ", ".join(industry)
        print("Corresponding Industry Names:", industry_str)
        print("____________________",sentiment_label,sentiment)

        data.append({
        "title": title.text.strip(),
        "link": link.strip(),
        "description": description.text.strip(),
        "pubdate":pubdate.text.strip(),
        "company":company_names_str,
        "sentiment_label":sentiment_label,
        "industry": industry_str
    })

    #print("^^^^^^^^^^^^^^^^80^^^^^^^^^^^^^^^^^^",data)


#Perform sentiment analysis on each link
# for link in links:
#     content = get_link_content(link)
#     if content:
#         blob = TextBlob(content)
#         #print("____________________________-
#         # ",blob)
#         sentiment = blob.sentiment.polarity
#         print("*************************",sentiment)
#         print(f"Sentiment analysis for {link}:")
#         if sentiment > 0.14489715077950371:
#             print("Positive sentiment")
#         elif sentiment < 0.14489715077950371:
#             print("Negative sentiment")
#         else:
#             print("Neutral sentiment")
#         print()


# for title, link, description,pubdate,sentiment in zip(title, link, description, pubdate,sentiment):
#     data.append({
#         "title": title.text.strip(),
#         "link": link.text.strip(),
#         "description": description.text.strip(),
#         "pubdate":pubdate.text.strip(),
#         "sentiment":sentiment
#        # "sentiment":sentiment
#     })

#     print("^^^^^^^^^^^^^^^^80^^^^^^^^^^^^^^^^^^",data)

   
# conn = mysql.connector.connect(
#     host="127.0.0.1",
#     user="root",
#     password="",
#     database="mydatabase"
# )

# cursor = conn.cursor()

# print("====================DATA 94 SAVED==========================")

# insert_query = "INSERT INTO scraped_data (title, link, description, pubdate,sentiment,company,industry) VALUES (%s,%s,%s,%s, %s, %s, %s) ON DUPLICATE KEY UPDATE title = VALUES(title), description = VALUES(description), pubdate = VALUES(pubdate), sentiment = VALUES(sentiment),company = VALUES(company),industry = VALUES(industry)"

# print("====================DATA 98 SAVED==========================")

# for item in data:
#     values = (item["title"], item["link"], item["description"], item["pubdate"],item["sentiment_label"],item["company"],item["industry"])
#     print(" v      A      L         U         E         S",values)
#     cursor.execute(insert_query, values)

# print("====================DATA 104 SAVED==========================")

# conn.commit()
# cursor.close()
# conn.close()

# print("====================DATA SAVED==========================")


#ALTER TABLE scraped_data MODIFY id INT AUTO_INCREMENT;
#TRUNCATE TABLE scraped_data;




#scraped_data = []


# for i in range(len(title)):
#     titles = title[i].text
#     links = link[i].text
#     descs = desc[i].text
#     #pubdates = pubdate[i].text

#     #print(":::::::::;;;;;;;;;;;;;;;;;;;;;;",pubdates)
#     scraped_data.append((titles, links, descs))

    #print("QQQQQQQQQQQQQQQQQQQQQQQQQQQQQ",titles)

    # = {'title':titles,'link':links,'desc':descs}

   # data_dic.update({'pubdate':pubdates})

    #print("**********************************",data_dic)


    # insert_query = "INSERT INTO scraped_data (title, link, description) VALUES (%s, %s, %s)"
    #data_dic = {'title':titles,'link':links,'desc':descs}
    #print("**********************************",data_dic)
#data = (titles, links, descs)

# cursor.execute(truncate_query)


# cursor.executemany(insert_query,scraped_data)

# conn.commit()
# conn.close()
               



# Truncate the table before inserting data
# truncate_query = "TRUNCATE TABLE scraped_data"


