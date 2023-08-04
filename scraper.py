import requests
from bs4 import BeautifulSoup
import re
from textblob import TextBlob
from nltk.sentiment import SentimentIntensityAnalyzer

# Making a GET request
url_link = "https://www.moneycontrol.com/rss/MCtopnews.xml"
response = requests.get(url_link)
print(response.status_code)

soup = BeautifulSoup(response.content, "xml")

links = [link.text.strip() for link in soup.find_all("link")]

def get_link_content(link):
    try:
        response = requests.get(link)
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        # Extract the text content from HTML
        text = soup.get_text(separator=' ')
        return text
    except Exception as e:
        print(f"Error retrieving content from {link}: {str(e)}")
        return ""
    
data = []
title = soup.select("title")  # Example CSS selector
link = soup.select("link")
description = soup.select("description")
pubdate = soup.select("pubDate")

specific_company_names = [
    "Moneycontrol", "Moneycontrol.com", "Sensex", "Nifty wobbly", "Hind Zinc", "SBI", "Force Motors", 
    "Asian Paints", "Tata Motors", "HUL", "Maruti Suzuki", "ONGC", "Axis Bank", "MM", "Bajaj Auto", 
    "Hero MotoCorp", "World Bank", "Neelkanth Mishra", "Global liquidity tailwinds", 
    "Geosphere Capital Management", "Endurance Technologies IPO", "Subramanian Swamy", "Flipkart", 
    "NV Tiger Tyagarajan", "Jhunjhunwala-partnered", "TFCI", "CNBC-TV18", "Satpal Arora", 
    "Hindustan Zinc", "Hindalco", "Jindal Steel", "JSW Steel", "Tata Steel", "Borosil Glass", "Sensors", 
    "3D printed skin", "wearables", "Pixel", "RBI", "Nomura", "Uber redBus", "ixigo", 
    "RBI_reserve_bank_of_India_RBi"
]

for link, title, description, pubdate in zip(links, title, description, pubdate):
    content = get_link_content(link)
    if content:
        blob = TextBlob(content)
        sentiment = blob.sentiment.polarity

        sentiment_label = ""

        print(f"Sentiment analysis for {link}:")
        if sentiment > 0.14489715077950371:
            sentiment_label = "Positive"
        elif sentiment < 0.14489715077950371:
            sentiment_label = "Negative"
        else:
            sentiment_label = "Neutral"

        title_text = title.text.strip()
        description_text = description.text.strip()

        # Extract company names from title
        title_company_names = [name for name in specific_company_names if re.search(r'\b' + re.escape(name) + r'\b', title_text, re.IGNORECASE)]

        # Extract company names from description
        description_company_names = [name for name in specific_company_names if re.search(r'\b' + re.escape(name) + r'\b', description_text, re.IGNORECASE)]
        company_names = title_company_names + description_company_names
        data.append({
            "title": title_text,
            "link": link.strip(),
            "description": description_text,
            "pubdate": pubdate.text.strip(),
            "company_names": company_names,
            "sentiment": sentiment_label
        })

# Print the collected data
for item in data:
    print("Title:", item["title"])
    print("Link:", item["link"])
    print("Description:", item["description"])
    print("Publication Date:", item["pubdate"])
    print("Company_Names:",item["company_names"])
    print("Sentiment:", item["sentiment"])
    print()

# TODO: Insert data into MySQL database
