# Import necessary libraries to run the code
import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
import re


def get_first_paragraph(wikipedia_url):
        
        try:

            r = requests.get(wikipedia_url)
            #response.raise_for_status()
            soup = BeautifulSoup(r.text, "html.parser")

            for p in soup.find_all("p"):
                if p.contents and p.contents[0].name == "b":
                    first_paragraph = p
                    break

            first_paragraph = first_paragraph.text
            
            pattern = r'\((.*?)ⓘ\)|\[.*?\]'
            first_paragraph = re.sub(pattern, '', first_paragraph)

            pattern = r'(\xa0)'
            first_paragraph = re.sub(pattern, ' ', first_paragraph)

        
            return first_paragraph
        
        except Exception:
            return ""


def get_leaders(root_url):

    cookies = requests.get(f"{root_url}/cookie")
    countries = requests.get(f"{root_url}/countries", cookies=cookies.cookies).json()

    data = []

    for c in countries:
        leaders = requests.get(f"{root_url}/leaders", cookies=cookies.cookies, params={"country": c}).json()

        for l in leaders:
            data.append({
                "country": c,
                "last_name": l.get("last_name"),
                "first_name": l.get("first_name"),
                "wikipedia_url": l.get("wikipedia_url")
            })       

    leaders_per_country = pd.DataFrame(data)
    leaders_per_country["first_paragraph"] = leaders_per_country["wikipedia_url"].apply(get_first_paragraph)
    
    

    return leaders_per_country

root_url = 'https://country-leaders.onrender.com'
leaders_per_country = get_leaders(root_url)
leaders_per_country.to_csv('leaders_data.csv', index = False)
leaders_per_country.to_json('leaders_data.json', orient='index')



