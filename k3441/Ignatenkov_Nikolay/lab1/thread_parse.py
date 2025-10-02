import threading
import requests
from bs4 import BeautifulSoup
from sqlmodel import Session
from api.models.connection import engine
from api.models.models import Book

USER_ID = 1
URLS = [
    "https://books.toscrape.com/catalogue/category/books_1/index.html",
    "https://books.toscrape.com/catalogue/category/books_2/index.html"
]

def parse_and_save(url):
    try:
        response = requests.get(url)
        html = response.text

        soup = BeautifulSoup(html, "html.parser")
        books = soup.select("article.product_pod")

        with Session(engine) as session_db:
            for book_tag in books:
                title = book_tag.h3.a["title"]
                author_tag = book_tag.select_one(".product_price ~ p")
                author = author_tag.text if author_tag else "Неизвестен"

                book = Book(
                    user_id=USER_ID,
                    title=title,
                    author=author,
                    description=f"Описание"
                )
                session_db.add(book)
            session_db.commit()
        print(f"Парсинг закончен {url}")
    except Exception as e:
        print(f"Ошибка: {e}")

threads = [threading.Thread(target=parse_and_save, args=(url,)) for url in URLS]

if __name__ == "__main__":
    for t in threads:
        t.start()
    for t in threads:
        t.join()
