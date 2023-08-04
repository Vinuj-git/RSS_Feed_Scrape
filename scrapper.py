import requests
from bs4 import BeautifulSoup
import pandas as pd
import spacy
import re
import nltk
import mysql.connector
from urllib.request import urlopen
from textblob import TextBlob
from transformers import pipeline

# Making a GET request
url_link = "https://www.moneycontrol.com/rss/MCtopnews.xml"
response = requests.get(url_link)
print(response.status_code)

soup = BeautifulSoup(response.content, "xml")

links = [link.text.strip() for link in soup.find_all("link")]

def get_link_content(link):
    try:
        response = urlopen(link)
        html = response.read()
        soup = BeautifulSoup(html, 'html.parser')
        # Extract the text content from HTML
        text = soup.get_text(separator=' ')
        return text
    except Exception as e:
        print(f"Error retrieving content from {link}: {str(e)}")
        return ""
    
df = pd.read_excel("C:/Users/accti/Downloads/List Of Companies v0 (1).xlsx")
company_names = df["Security Name"].tolist()

data = []
for link in links:
    response_content = get_link_content(link)
    if response_content:
        blob = TextBlob(response_content)
        sentiment = blob.sentiment.polarity

        sentiment_label = ""
        if sentiment > 0.14489715077950371:
            sentiment_label = "Positive"
        elif sentiment < 0.14489715077950371:
            sentiment_label = "Negative"
        else:
            sentiment_label = "Neutral"

        soup_content = BeautifulSoup(response_content, "html.parser")
        
        # Check if the title is present in the page content
        if soup_content.title:
            title_text = soup_content.title.text.strip()
        else:
            title_text = ""

        # Check if the "meta" tag with "name" attribute set to "description" is present
        description_meta_tag = soup_content.find("meta", attrs={"name": "description"})
        if description_meta_tag:
            description_text = description_meta_tag["content"].strip()
        else:
            description_text = ""

        # Extract company names from the title and description
        title_company_names = [name for name in company_names if re.search(r'\b' + re.escape(name) + r'\b', title_text, re.IGNORECASE)]
        description_company_names = [name for name in company_names if re.search(r'\b' + re.escape(name) + r'\b', description_text, re.IGNORECASE)]

        # Combine the company names from title and description
        related_words = list(set(title_company_names + description_company_names))

        related_words_str = ", ".join(related_words)

        data.append({
            "title": title_text,
            "link": link.strip(),
            "description": description_text,
            "related_words": related_words_str,
            "sentiment_label": sentiment_label
        })

# Create a DataFrame from the collected data
df_result = pd.DataFrame(data)

# Save the DataFrame to a CSV file
df_result.to_csv("scraped_data.csv", index=False)

print("Data scraped and saved to scraped_data.csv")
