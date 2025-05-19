import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai

# === CONFIGURATION ===
GEMINI_API_KEY = "your_google_gemini_api_key"  # Replace with your Gemini API key
BING_API_KEY = "your_bing_api_key"             # Replace with your Bing Search API key

# === Configure Gemini ===
genai.configure(api_key=GEMINI_API_KEY)

# === Function: Web Search ===
def search_web(query):
    BING_SEARCH_URL = "https://api.bing.microsoft.com/v7.0/search"
    headers = {"Ocp-Apim-Subscription-Key": BING_API_KEY}
    params = {"q": query, "count": 3}  # Get top 3 results
    response = requests.get(BING_SEARCH_URL, headers=headers, params=params)
    response.raise_for_status()

    results = response.json()
    links = [item["url"] for item in results.get("webPages", {}).get("value", [])]
    return links

# === Function: Scrape Content ===
def scrape_content(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        paragraphs = soup.find_all("p")
        content = " ".join([para.get_text() for para in paragraphs])
        return content[:2000]  # limit to 2000 chars
    except Exception as e:
        return f"Error scraping {url}: {e}"

# === Function: Gemini Summarization ===
def summarize_with_gemini(content, query):
    model = genai.GenerativeModel("gemini-pro")  # or "gemini-1.5-flash"
    response = model.generate_content(f"""
        I searched the web and found the following information:
        {content}

        Based on this, answer the following question:
        {query}
    """)
    return response.text

# === Streamlit UI ===
st.title("🌐 Agentic AI with Web Search")
st.write("Enter your query below. The AI will search the web, extract relevant info, and answer your question using Gemini.")

query = st.text_input("🔍 Enter your query:")

if query:
    st.info("🔎 Searching the web...")
    links = search_web(query)

    st.info("📄 Scraping content...")
    full_text = ""
    for link in links:
        st.write(f"Scraping: {link}")
        content = scrape_content(link)
        full_text += content + "\n\n"

    st.info("🤖 Summarizing with Gemini...")
    answer = summarize_with_gemini(full_text, query)

    st.subheader("✅ AI Response:")
    st.write(answer)
