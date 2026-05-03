import os
import markdown
from bs4 import BeautifulSoup
import streamlit as st
import pandas as pd
import requests
import json

def test_api(method, endpoint, params_json, body_json, auth_type, api_key, key_name, auth_location):
    try:
        param_dict = json.loads(params_json) if params_json else {}
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON in query params")
    headers = {}
    body = None
    if method in ["POST", "PUT"]:
        try:
            body = json.loads(body_json) if body_json else {}
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON in request body")
    if auth_type == "API Key" and api_key:
        if auth_location == "Header":
            headers[key_name] = api_key
        else:
            param_dict[key_name] = api_key
    response = requests.request(method, endpoint, params=param_dict, json=body, headers=headers)
    return response

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
# API Tester
st.header("API Tester")

# Dictionary for API lookup
api_dict = {api['name']: api for cat in data for api in cat['apis']}

selected_api = st.selectbox("Select API to Test", sorted(api_dict.keys()))

default_endpoint = api_dict.get(selected_api, {'link': ''})['link']

endpoint = st.text_input("Endpoint URL", value=default_endpoint)

method = st.selectbox("HTTP Method", ["GET", "POST", "PUT", "DELETE"])

params_json = st.text_area("Query Params (JSON)")

body_json = ""

if method in ["POST", "PUT"]:
    body_json = st.text_area("Request Body (JSON)")

auth_type = st.selectbox("Authentication Type", ["None", "API Key"])

api_key = ""
key_name = "api_key"
auth_location = "Query Param"

if auth_type == "API Key":
    api_key = st.text_input("API Key", type="password")  # Secure input
    key_name = st.text_input("Key Name", value="api_key")
    auth_location = st.selectbox("Location", ["Query Param", "Header"])

if st.button("Test"):
    if not endpoint:
        st.error("Endpoint URL is required.")
    elif not endpoint.startswith(("http://", "https://")):
        st.error("Invalid URL scheme. Must be http or https.")
    else:
        try:
            response = test_api(method, endpoint, params_json, body_json, auth_type, api_key, key_name, auth_location)
            try:
                st.json(response.json())
            except json.JSONDecodeError:
                st.text("Non-JSON response received:\n" + response.text)
        except (ValueError, requests.RequestException) as e:
            st.error(str(e))
        except Exception as e:
            st.error(f"Unexpected error: {str(e)}")

# Note: For production, to mitigate SSRF, consider implementing an allowlist of domains or using a proxy service.
