# API Explorer MVP [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) [![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/) [![Streamlit](https://img.shields.io/badge/Streamlit-1.0+-FF4B4B.svg)](https://streamlit.io/) [![GitHub Stars](https://img.shields.io/github/stars/NullLabTests/api-explorer-mvp)](https://github.com/NullLabTests/api-explorer-mvp/stargazers) [![GitHub Forks](https://img.shields.io/github/forks/NullLabTests/api-explorer-mvp)](https://github.com/NullLabTests/api-explorer-mvp/network) [![GitHub Issues](https://img.shields.io/github/issues/NullLabTests/api-explorer-mvp)](https://github.com/NullLabTests/api-explorer-mvp/issues)

MVP web app to browse, search, and test 1000+ public APIs from the [public-apis](https://github.com/public-apis/public-apis) repository. Built with Streamlit for a simple, interactive UI/UX. Perfect for developers exploring free APIs for projects!

## Features
- **API Browsing**: Categorized list of APIs (e.g., Animals, Weather, Finance) parsed from the latest public-apis README.
- **Search Functionality**: Quick search by API name or description across all categories.
- **Interactive Tester**: Select an API, autofill endpoint, choose method (GET/POST/PUT/etc.), add params/body/auth (API key support), and test live requests with JSON output or error handling.
- **Responsive UI**: Clean, terminal-friendly text output, but shines in a browser via Streamlit.
- **Extensible**: Easy to add more features like API favorites or export.

## Screenshot
![API Explorer UI](https://raw.githubusercontent.com/NullLabTests/api-explorer-mvp/main/screenshot.png)
*(Browsing categories, searching for "dog" APIs, and testing a GET request to Dog CEO API.)*

## Installation
1. Clone the repo:
   ```
   git clone https://github.com/NullLabTests/api-explorer-mvp.git
   cd api-explorer-mvp
   ```
2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage
1. Run the app:
   ```
   streamlit run app.py
   ```
2. Open your browser to the provided URL (usually http://localhost:8501).
3. **Browse**: Use the sidebar to select a category and view APIs in a table.
4. **Search**: Enter a term in the search box to filter APIs.
5. **Test an API**:
   - Select an API from the dropdown (autofills the link).
   - Choose method, add params/body/API key if needed.
   - Click "Test" to see the response.

Example: Test the Dog CEO API with endpoint `https://dog.ceo/api/breeds/list/all` (GET, no auth).

## Troubleshooting
- **Parsing Errors**: Ensure `data/README.md` is present (it's the source data from public-apis).
- **Request Failures**: Some APIs require keys or have rate limits—check their docs.
- **Streamlit Email Prompt**: If it asks for an email on first run, you can skip or enter a dummy one (it's for analytics opt-in).
- If issues, check the console output or open a GitHub issue.

## Contributing
Contributions welcome! Fork the repo, make changes, and submit a PR. Ideas:
- Add support for more auth types (OAuth).
- Improve search with fuzzy matching.
- Integrate API usage examples.

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines (feel free to add one if needed).

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Built by [Hermes Agent] with ❤️ for open-source APIs. Star the repo if you find it useful!