import os
import markdown
from bs4 import BeautifulSoup
import streamlit as st
import pandas as pd
import requests
import json

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
    # Iterate through all h3 and table elements
    for elem in soup.find_all(['h3', 'table']):
        if elem.name == 'h3':
            # Set current category from h3 text
            current_cat = elem.text.strip()
        elif elem.name == 'table' and current_cat:
            # Initialize list for APIs in this category
            apis = []
            # Get all table rows
            trs = elem.find_all('tr')
            if not trs:
                continue
            # Extract headers from first row
            header_row = trs[0]
            headers = [th.text.strip() for th in header_row.find_all('th')]
            # Process each data row
            for row in trs[1:]:
                tds = row.find_all('td')
                if len(tds) != len(headers):
                    continue  # skip invalid rows
                # Extract name and link from first cell
                first_td = tds[0]
                a_tag = first_td.find('a')
                if a_tag:
                    name = a_tag.text.strip()
                    link = a_tag['href']
                else:
                    name = first_td.text.strip()
                    link = ''
                # Extract other cells
                cells = [td.text.strip() for td in tds[1:]]
                api_dict = dict(zip(headers[1:], cells))
                api_dict['name'] = name
                api_dict['link'] = link
                # Map to standardized keys
                api = {
                    'name': api_dict['name'],
                    'description': api_dict.get('Description', ''),
                    'auth': api_dict.get('Auth', '').replace('`', ''),
                    'https': api_dict.get('HTTPS', '') == 'Yes',
                    'cors': api_dict.get('CORS', ''),
                    'link': api_dict['link']
                }
                # Set default auth if empty
                if not api['auth']:
                    api['auth'] = 'No'
                apis.append(api)
            # Add category if there are APIs
            if apis:
                categories.append({'category': current_cat, 'apis': apis})
    return categories

def get_categories(data):
    """Extract list of category names from parsed data."""
    return [d['category'] for d in data]

def search_apis(data, query):
    """Search APIs by name or description."""
    results = []
    for cat in data:
        for api in cat['apis']:
            if query.lower() in api.get('name', '').lower() or query.lower() in api.get('description', '').lower():
                results.append(api)
    return results

def get_apis_for_category(data, category):
    """Get list of APIs for a specific category."""
    for cat in data:
        if cat['category'] == category:
            return cat['apis']
    return []

# Main app
st.title("Public API Explorer")

readme_path = os.environ.get('README_PATH', 'data/README.md')

try:
    data = parse_readme(readme_path)
except Exception as e:
    st.error(f"Failed to parse README: {e}")
    data = []

categories = get_categories(data)

st.sidebar.title("Navigation")

if not categories:
    st.sidebar.write("No categories available.")
else:
    selected_cat = st.sidebar.selectbox("Select Category", categories)
    search = st.sidebar.text_input("Search APIs")

    if search:
        results = search_apis(data, search)
        st.dataframe(pd.DataFrame(results))
    else:
        apis = get_apis_for_category(data, selected_cat)
        st.dataframe(pd.DataFrame(apis))
st.header("API Tester")
selected_api = st.selectbox("Select API to Test", [api['name'] for cat in data for api in cat['apis']])
endpoint = st.text_input("Endpoint URL")
params = st.text_area("Params (JSON)")

if st.button("Test"):
    try:
        param_dict = json.loads(params) if params else {}
        response = requests.get(endpoint, params=param_dict)
        st.json(response.json())
    except Exception as e:
        st.error(str(e))
