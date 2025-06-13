# Import necessary libraries to run the code
import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
import re


def get_first_paragraph(wikipedia_url):
        """Funtion that will scrape the first paragraph of the wikipedia url passed as argument"""
        
        
        try:
            """Unfortunately some urls return an error code, therefore use a try/except to skip those ones"""
            
            # open a request for the url and parse the code
            r = requests.get(wikipedia_url)
            soup = BeautifulSoup(r.text, "html.parser")

            for p in soup.find_all("p"):
                if p.contents and p.contents[0].name == "b":
                    first_paragraph = p
                    break

            first_paragraph = first_paragraph.text
            
            # cleaning the ouptut with some detected patterns
            pattern = r'\((.*?)ⓘ\)|\[.*?\]'
            first_paragraph = re.sub(pattern, '', first_paragraph)

            pattern = r'(\xa0)'
            first_paragraph = re.sub(pattern, ' ', first_paragraph)

            # returning the paragraph or void if error
            return first_paragraph
        
        except Exception:
            return ""


def get_leaders(root_url):
    """ Funtion that uses the root url to:
        - create requests to manage cookies, retrieve countries and get leaders urls
        - loop through all countries - leaders url to create a dataframe
        - call first paragraph function to add these to the dataframe
    """


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

# Set root url for the requests
root_url = 'https://country-leaders.onrender.com'

# call the get leaders function
leaders_per_country = get_leaders(root_url)

# save the output to json and csv
leaders_per_country.to_csv('leaders_data.csv', index = False)
leaders_per_country.to_json('leaders_data.json', orient='index')



