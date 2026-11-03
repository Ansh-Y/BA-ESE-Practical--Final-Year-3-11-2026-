from __future__ import annotations

import sqlite3
from collections import Counter
from datetime import date

from data import CUSTOMERS, PRODUCTS, REVIEWS, SALES
from text_mining import sentiment_label, sentiment_score, tokenize

SENTIMENT_LABELS = ["Positive", "Neutral", "Negative"]

SCHEMA = """
CREATE TABLE dim_date (
    date_key INTEGER PRIMARY KEY,
    full_date TEXT NOT NULL,
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    month INTEGER NOT NULL,
    month_name TEXT NOT NULL,
    weekday TEXT NOT NULL
);

CREATE TABLE dim_product (
    product_key INTEGER PRIMARY KEY,
    product_id TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    category TEXT NOT NULL
);

CREATE TABLE dim_customer (
    customer_key INTEGER PRIMARY KEY,
    customer_id TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    region TEXT NOT NULL
);

CREATE TABLE dim_sentiment (
    sentiment_key INTEGER PRIMARY KEY,
    label TEXT NOT NULL UNIQUE
);

CREATE TABLE dim_term (
    term_key INTEGER PRIMARY KEY,
    term TEXT NOT NULL UNIQUE
);

CREATE TABLE fact_sales (
    sales_key INTEGER PRIMARY KEY,
    date_key INTEGER NOT NULL REFERENCES dim_date(date_key),
    product_key INTEGER NOT NULL REFERENCES dim_product(product_key),
    customer_key INTEGER NOT NULL REFERENCES dim_customer(customer_key),
    quantity INTEGER NOT NULL,
    unit_price REAL NOT NULL,
    revenue REAL NOT NULL
);

CREATE TABLE fact_review (
    review_key INTEGER PRIMARY KEY,
    date_key INTEGER NOT NULL REFERENCES dim_date(date_key),
    product_key INTEGER NOT NULL REFERENCES dim_product(product_key),
    customer_key INTEGER NOT NULL REFERENCES dim_customer(customer_key),
    sentiment_key INTEGER NOT NULL REFERENCES dim_sentiment(sentiment_key),
    rating INTEGER NOT NULL,
    word_count INTEGER NOT NULL,
    sentiment_score REAL NOT NULL,
    review_text TEXT NOT NULL
);

CREATE TABLE fact_review_term (
    review_key INTEGER NOT NULL REFERENCES fact_review(review_key),
    term_key INTEGER NOT NULL REFERENCES dim_term(term_key),
    frequency INTEGER NOT NULL,
    PRIMARY KEY (review_key, term_key)
);
"""


def to_date_key(day: date) -> int:
    return day.year * 10000 + day.month * 100 + day.day


def _key_map(conn: sqlite3.Connection, table: str, business_col: str, key_col: str) -> dict:
    return dict(conn.execute(f"SELECT {business_col}, {key_col} FROM {table}").fetchall())


def _load_dim_date(conn: sqlite3.Connection, days: set[date]) -> None:
    rows = [
        (
            to_date_key(day),
            day.isoformat(),
            day.year,
            (day.month - 1) // 3 + 1,
            day.month,
            day.strftime("%B"),
            day.strftime("%A"),
        )
        for day in sorted(days)
    ]
    conn.executemany(
        "INSERT INTO dim_date (date_key, full_date, year, quarter, month, month_name, weekday) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        rows,
    )


def _load_sales(conn: sqlite3.Connection, products: dict, customers: dict) -> None:
    rows = [
        (
            to_date_key(day),
            products[product_id],
            customers[customer_id],
            quantity,
            unit_price,
            round(quantity * unit_price, 2),
        )
        for day, product_id, customer_id, quantity, unit_price in SALES
    ]
    conn.executemany(
        "INSERT INTO fact_sales (date_key, product_key, customer_key, quantity, unit_price, revenue) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        rows,
    )


def _load_reviews(conn: sqlite3.Connection, products: dict, customers: dict, sentiments: dict) -> None:
    for day, product_id, customer_id, rating, text in REVIEWS:
        tokens = tokenize(text)
        score = sentiment_score(tokens)
        cursor = conn.execute(
            "INSERT INTO fact_review (date_key, product_key, customer_key, sentiment_key, "
            "rating, word_count, sentiment_score, review_text) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                to_date_key(day),
                products[product_id],
                customers[customer_id],
                sentiments[sentiment_label(score)],
                rating,
                len(text.split()),
                score,
                text,
            ),
        )
        review_key = cursor.lastrowid
        for term, frequency in Counter(tokens).items():
            conn.execute("INSERT OR IGNORE INTO dim_term (term) VALUES (?)", (term,))
            term_key = conn.execute("SELECT term_key FROM dim_term WHERE term = ?", (term,)).fetchone()[0]
            conn.execute(
                "INSERT INTO fact_review_term (review_key, term_key, frequency) VALUES (?, ?, ?)",
                (review_key, term_key, frequency),
            )


def build_star_schema() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA)

    conn.executemany(
        "INSERT INTO dim_product (product_id, name, category) VALUES (?, ?, ?)", PRODUCTS
    )
    conn.executemany(
        "INSERT INTO dim_customer (customer_id, name, region) VALUES (?, ?, ?)", CUSTOMERS
    )
    conn.executemany(
        "INSERT INTO dim_sentiment (label) VALUES (?)", [(label,) for label in SENTIMENT_LABELS]
    )
    days = {row[0] for row in SALES} | {row[0] for row in REVIEWS}
    _load_dim_date(conn, days)

    products = _key_map(conn, "dim_product", "product_id", "product_key")
    customers = _key_map(conn, "dim_customer", "customer_id", "customer_key")
    sentiments = _key_map(conn, "dim_sentiment", "label", "sentiment_key")

    _load_sales(conn, products, customers)
    _load_reviews(conn, products, customers, sentiments)
    conn.commit()
    return conn
