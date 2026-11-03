import sqlite3

BUSINESS_QUERIES = {
    "Revenue by category and quarter": """
        SELECT p.category, d.year, d.quarter, ROUND(SUM(f.revenue), 2) AS revenue
        FROM fact_sales f
        JOIN dim_product p ON p.product_key = f.product_key
        JOIN dim_date d ON d.date_key = f.date_key
        GROUP BY p.category, d.year, d.quarter
        ORDER BY d.year, d.quarter, p.category
    """,
    "Top products by revenue": """
        SELECT p.name, SUM(f.quantity) AS units, ROUND(SUM(f.revenue), 2) AS revenue
        FROM fact_sales f
        JOIN dim_product p ON p.product_key = f.product_key
        GROUP BY p.name
        ORDER BY revenue DESC
    """,
    "Revenue by customer region": """
        SELECT c.region, COUNT(*) AS orders, ROUND(SUM(f.revenue), 2) AS revenue
        FROM fact_sales f
        JOIN dim_customer c ON c.customer_key = f.customer_key
        GROUP BY c.region
        ORDER BY revenue DESC
    """,
}

TEXT_QUERIES = {
    "Rating and sentiment by product": """
        SELECT p.name, COUNT(*) AS reviews,
               ROUND(AVG(f.rating), 2) AS avg_rating,
               ROUND(AVG(f.sentiment_score), 3) AS avg_sentiment
        FROM fact_review f
        JOIN dim_product p ON p.product_key = f.product_key
        GROUP BY p.name
        ORDER BY avg_rating DESC
    """,
    "Sentiment distribution": """
        SELECT s.label, COUNT(*) AS reviews
        FROM fact_review f
        JOIN dim_sentiment s ON s.sentiment_key = f.sentiment_key
        GROUP BY s.label
        ORDER BY reviews DESC, s.label
    """,
}

TOP_TERMS_SQL = """
    SELECT t.term, SUM(ft.frequency) AS frequency
    FROM fact_review_term ft
    JOIN fact_review f ON f.review_key = ft.review_key
    JOIN dim_product p ON p.product_key = f.product_key
    JOIN dim_term t ON t.term_key = ft.term_key
    WHERE p.name = ?
    GROUP BY t.term
    ORDER BY frequency DESC, t.term
    LIMIT ?
"""


def top_terms(conn: sqlite3.Connection, product_name: str, limit: int = 5) -> list[tuple]:
    return conn.execute(TOP_TERMS_SQL, (product_name, limit)).fetchall()
