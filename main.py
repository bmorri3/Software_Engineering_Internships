import os
import re
import subprocess

import requests
from bs4 import BeautifulSoup


def remove_emojis(text):
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"
                               u"\U0001F300-\U0001F5FF"
                               u"\U0001F680-\U0001F6FF"
                               u"\U0001F1E0-\U0001F1FF"
                               u"\U00002702-\U000027B0"
                               u"\U000024C2-\U0001F251"
                               "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text)


def split_location(location, max_length=20):
    if len(location) <= max_length:
        return location


    words = location.split()
    split_location = ''
    current_length = 0

    for word in words:
        if current_length + len(word) > max_length:
            split_location += '<br>'
            current_length = 0
        elif current_length > 0:
            split_location += ' '
            current_length += 1

        split_location += word
        current_length += len(word)

    return split_location

def scrape_internships(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')

    table = soup.find('table')

    internships = []

    if table is not None:
        for row in table.find_all('tr'):
            row_data = []
            for cell in row.find_all('td'):
                a_tag = cell.find('a')
                if a_tag and a_tag.has_attr('href'):
                    url = a_tag['href']

                    if os.getenv('Format') in url:
                        company_name = url.split('/')[-1]
                        row_data.append(company_name)
                    else:
                        row_data.append(url)
                else:
                    cell_text = remove_emojis(cell.get_text(strip=True))
                    row_data.append(cell_text)
            if len(row_data) > 2:
                row_data[2] = split_location(row_data[2])

            link = row_data[3] if len(row_data) > 3 else ""
            if link and link.startswith("http"):
                internships.append(row_data)
    else:
        print(f"No table found on the page: {url}")

    return internships


def create_markdown_table(data):
    if not data or not data[0]:
        return "No data available."

    headers = ["Company", "Role", "Location", "Links", "Date Posted"]
    markdown = "| " + " | ".join(headers) + " |\n"
    markdown += "| " + " | ".join(["---"] * len(headers)) + " |\n"

    for row in data:
        row = [cell.replace('\n', '<br>') for cell in row]

        row[2] = row[2].replace(',', '<br>')

        row[3] = f'<a href="{row[3]}">Link</a>' if row[3].startswith('http') else row[3]

        markdown += "| " + " | ".join(row) + " |\n"

    return markdown


if __name__ == "__main__":
    intro_text = """
# Software Engineering Internships
    
Welcome to the Software Engineering Internships repository! This repository serves as a resource for students and aspiring software engineers seeking internship opportunities in the tech industry. Our goal is to provide an up-to-date and easily accessible collection of internship positions across various companies located in the **USA, Canada and Remote Only**.
    
# About This Repository
This repository is the result of an automated web scraping project that aims to compile information about available software engineering internships. We understand how challenging and time-consuming it can be to search for internships, and this project is here to simplify that process.
    
# What You'll Find Here
In this repository, you will find a detailed list of software engineering internships, including details such as:
    
Company: The name of the company offering the internship.
    
Role: Specific title or role of the internship position.
    
Location: Geographical location or remote availability.
    
Application: Direct links to the application or job posting.
    
Date Posted: The date when the internship opportunity was listed.
    
# How It Works
Our script runs daily to scrape and update the list of internships from a reputable source. The gathered data is then formatted into a Markdown table in the README.md file for easy viewing.
    
# Contributing
We welcome contributions to this project! If you have suggestions for additional sources to scrape, improvements to the script, or any other contributions, please feel free to open an issue or submit a pull request.
    
# Disclaimer
Please note that while we strive to keep the information accurate and up-to-date, we rely on external sources. Always verify the details on the respective company's website or contact point.
    
# License
This project is open source and available under <https://unlicense.org> .
    
    """
    urls = [
        'https://www.indeed.com/q-software-engineer-internship-jobs.html',
        'https://www.glassdoor.com/Job/software-engineer-internship-jobs-SRCH_KO0,28.htm',
        'https://www.linkedin.com/jobs/search/?currentJobId=3917554987&keywords=software%20engineer%20internship',
        'https://www.builtin.com/jobs/internships',  # Tech internship listing website
        'https://www.acm.org/careers/students/internships',  # Association for Computing Machinery internship listings
        'https://www.ieee.org/careers/internships',  # Institute of Electrical and Electronics Engineers internship listings        
    ]
        
    scraped_data = []
    for url in urls:
        scraped_data.extend(scrape_internships(url))

    markdown_table = create_markdown_table(scraped_data)
    complete_readme = intro_text + "\n " + markdown_table

    with open('README.md', 'w', encoding='utf-8') as file:
        file.write(complete_readme)

    subprocess.run(["git", "add", "README.md"])
    subprocess.run(["git", "commit", "-m", "Updated dataset"])
    subprocess.run(["git", "push"])
