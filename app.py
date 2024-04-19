import streamlit as st
import newspaper
from textblob import TextBlob
from datetime import datetime
from urllib.parse import urlparse
import validators
import requests
import nltk

nltk.download("punkt")  # Download the punkt tokenizer


# DESIGN implement changes to the standard streamlit UI/UX
st.set_page_config(
    page_title="SnapNews",
    page_icon="images/logo_news.png",
)


# Design change spinner color to primary color
st.markdown(
    """<style>.stSpinner > div > div {border-top-color: #9d03fc;}</style>""",
    unsafe_allow_html=True,
)

# Design hide "made with streamlit" footer menu area
hide_streamlit_footer = """<style>#MainMenu {visibility: hidden;}
                        footer {visibility: hidden;}</style>"""

st.markdown(hide_streamlit_footer, unsafe_allow_html=True)


def get_website_name(url):
    try:
        # Extract the website name from the URL
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        if domain.startswith("www."):
            domain = domain[4:]
        return domain
    except Exception as e:
        # Handle any exceptions that might occur during URL parsing
        return ValueError("Error parsing URL: " + str(e))


def generate_summary(article_text, max_words=100):
    # Split the article text into words
    words = article_text.split()
    # Select the first max_words words to form the summary
    summary = " ".join(words[:max_words])
    return summary


def summarize_article(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an HTTPError if the HTTP request returned an unsuccessful status code
    except requests.RequestException:
        return None

    article = newspaper.Article(url)
    article.download()
    article.parse()
    article.nlp()  # Perform natural language processing

    title = article.title
    authors = ", ".join(article.authors)
    if not authors:
        authors = get_website_name(url)  # Set the author field to the website name
    publish_date = (
        article.publish_date.strftime("%B %d, %Y") if article.publish_date else "N/A"
    )

    # Generate summary with approximately 100 words
    # summary = generate_summary(article.text, max_words=100)
    summary = article.summary

    top_image = article.top_image  # Get the top image URL

    analysis = TextBlob(article.text)
    polarity = analysis.sentiment.polarity  # Get the polarity value

    if polarity > 0:
        sentiment = "positive 😊"
    elif polarity < 0:
        sentiment = "negative 😟"
    else:
        sentiment = "neutral 😐"

    return title, authors, publish_date, summary, top_image, sentiment


def get_top_articles(news_source):
    # Dictionary mapping news source names to their URLs
    news_sources = {
        "Indian Express": "https://indianexpress.com/",
        "India Today": "https://www.indiatoday.in/",
        "Times of India": "https://timesofindia.indiatimes.com/",
        "Round Table India ": "https://www.roundtableindia.co.in/category/perspective/gender/",
    }

    source_url = news_sources.get(news_source)
    if source_url:
        paper = newspaper.build(source_url, memoize_articles=False)
        articles = paper.articles[:5]  # Get top 5 articles
        return [article.url for article in articles]
    else:
        return []


import streamlit as st


def main():
    st.image("images/banner.jpg", width=None)
    st.subheader("AI-Summarized news articles :")

    url = st.text_input(
        "Enter URL here",
        placeholder="https://news_link_example.com/search",
        key="url_input",
    )

    if st.button("Summarize Article"):
        if not validators.url(url):
            st.error(
                "Please enter a valid URL or this news agency doesn't allow news parsing"
            )
        else:
            article_info = summarize_article(url)
            if article_info:
                title, authors, publish_date, summary, top_image, sentiment = (
                    article_info
                )

                st.subheader("Summary:")
                st.write(summary)

                st.subheader("Details:")
                st.write(f"Title: {title}")
                st.write(f"Authors: {authors}")
                st.write(f"Publish Date: {publish_date}")
                st.image(top_image, caption="Top Image", use_column_width=True)
                st.write(f"Sentiment: {sentiment}")

                st.subheader("Original Article:")
                st.write(f"You can read the full article [here]({url}).")
            else:
                st.error(
                    "Failed to summarize the article. This news agency doesn't allow news parsing."
                )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    st.header("Select a news source:")
    dropdown_button_key = "dropdown_button"
    news_source = st.selectbox(
        "Choose a news source:",
        ["Indian Express", "Round Table India", "Times of India", "India Today"],
        key=dropdown_button_key,
    )

    if st.button(
        f"Summarize Top 5 Articles from {news_source}", key=f"{news_source}_button"
    ):
        top_articles = get_top_articles(news_source)
        if top_articles:
            for article_url in top_articles:
                article_info = summarize_article(article_url)
                if article_info:
                    title, authors, publish_date, summary, top_image, sentiment = (
                        article_info
                    )
                    st.subheader(f"{title}")
                    st.write(f"URL: {article_url}")
                    st.write(summary)
                    st.image(top_image, caption="Top Image", width=300)
                else:
                    st.error(f"Failed to summarize article: {article_url}")
        else:
            st.error(f"Failed to fetch top articles from {news_source}.")


if __name__ == "__main__":
    main()
