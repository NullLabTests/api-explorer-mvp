import os
import markdown
from bs4 import BeautifulSoup

def parse_readme(file_path):
    """
    Parse the README.md file to extract API categories and details.

    Args:
        file_path (str): Path to the README file.

    Returns:
        list: List of dictionaries with 'category' and 'apis'.

    Raises:
        FileNotFoundError: If the file is not found.
        ValueError: If parsing fails.
    """
    try:
        with open(file_path, 'r') as f:
            md = f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"README file not found at {file_path}")

    try:
        html = markdown.markdown(md, extensions=['tables'])
        soup = BeautifulSoup(html, 'html.parser')
    except Exception as e:
        raise ValueError(f"Error parsing markdown: {e}")

    categories = []
    current_cat = None
    for elem in soup.find_all(['h3', 'table']):
        if elem.name == 'h3':
            current_cat = elem.text.strip()
        elif elem.name == 'table' and current_cat:
            apis = []
            trs = elem.find_all('tr')
            if not trs:
                continue
            header_row = trs[0]
            headers = [th.text.strip() for th in header_row.find_all('th')]
            for row in trs[1:]:
                tds = row.find_all('td')
                if len(tds) != len(headers):
                    continue  # skip invalid rows
                # First cell: name and link
                first_td = tds[0]
                a_tag = first_td.find('a')
                if a_tag:
                    name = a_tag.text.strip()
                    link = a_tag['href']
                else:
                    name = first_td.text.strip()
                    link = ''
                # Other cells
                cells = [td.text.strip() for td in tds[1:]]
                api_dict = dict(zip(headers[1:], cells))
                api_dict['name'] = name
                api_dict['link'] = link
                # Rename keys to match current
                api = {
                    'name': api_dict['name'],
                    'description': api_dict.get('Description', ''),
                    'auth': api_dict.get('Auth', '').replace('`', ''),
                    'https': api_dict.get('HTTPS', '') == 'Yes',
                    'cors': api_dict.get('CORS', ''),
                    'link': api_dict['link']
                }
                # If auth empty, set to 'No'
                if not api['auth']:
                    api['auth'] = 'No'
                apis.append(api)
            if apis:
                categories.append({'category': current_cat, 'apis': apis})
    return categories
