from bs4 import BeautifulSoup


def parse_html(html: str):
    soup = BeautifulSoup(html, 'html.parser')

    meta = soup.find(name='meta', attrs={'name': 'description'})

    h1 = soup.h1.get_text() if soup.h1 else None
    title = soup.title.get_text() if soup.title else None
    description = meta.get('content') if meta else None

    return h1, title, description
