import markdown
from bs4 import BeautifulSoup

md = """
### Test Category

Text | text
"""

html = markdown.markdown(md, extensions=['tables'])
soup = BeautifulSoup(html, 'html.parser')
print(soup.prettify())
