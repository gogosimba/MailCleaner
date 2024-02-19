from bs4 import BeautifulSoup
def clean_html(html):
    soup = BeautifulSoup(html, "html.parser")
    for div in soup.find_all('div', {'class': 'unwanted'}):
        div.decompose()
    return soup.get_text()

#elements to remove div id=divRplyFwdMsg, <img>,