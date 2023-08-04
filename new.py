# ...

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

        link_text = link.text.strip()  # Get the text content of the link
        title_text = title.text.strip()
        description_text = description.text.strip()

        def process_company_name(name):
            return re.sub(r"[-_=$]", " ", name.lower())
        
        processed_company_names = [process_company_name(name) for name in company_names]

        link_company_names = [name for name in processed_company_names if fuzz.token_set_ratio(process_company_name(link_text), name) >= 80]
        title_company_names = [name for name in processed_company_names if fuzz.token_set_ratio(process_company_name(title_text), name) >= 80]
        description_company_names = [name for name in processed_company_names if fuzz.token_set_ratio(process_company_name(description_text), name) >= 80]

        company = list(set(link_company_names + title_company_names + description_company_names))
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
        

        industry_str = ", ".join(industry)
        print("Corresponding Industry Names:", industry_str)
        print("____________________", sentiment_label, sentiment)

        data.append({
            "title": title.text.strip(),
            "link": link.strip(),
            "description": description.text.strip(),
            "pubdate": pubdate.text.strip(),
            "company": company_names_str,
            "sentiment_label": sentiment_label,
            "industry": industry_str
        })

# ...
