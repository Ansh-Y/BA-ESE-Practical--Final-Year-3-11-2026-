from queries import BUSINESS_QUERIES, TEXT_QUERIES, top_terms
from star_schema import build_star_schema

FACT_AND_DIM_TABLES = [
    "dim_date", "dim_product", "dim_customer", "dim_sentiment", "dim_term",
    "fact_sales", "fact_review", "fact_review_term",
]


def print_table(title: str, columns: list[str], rows: list[tuple]) -> None:
    print(f"\n{title}")
    widths = [
        max([len(str(column))] + [len(str(row[i])) for row in rows])
        for i, column in enumerate(columns)
    ]
    line = "  ".join(column.ljust(widths[i]) for i, column in enumerate(columns))
    print(line)
    print("-" * len(line))
    for row in rows:
        print("  ".join(str(value).ljust(widths[i]) for i, value in enumerate(row)))


def run_report(conn, title: str, sql: str) -> None:
    cursor = conn.execute(sql)
    columns = [column[0] for column in cursor.description]
    print_table(title, columns, cursor.fetchall())


def main() -> None:
    conn = build_star_schema()

    print("Star schema row counts")
    for table in FACT_AND_DIM_TABLES:
        count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"  {table}: {count}")

    print("\n=== Business analytics ===")
    for title, sql in BUSINESS_QUERIES.items():
        run_report(conn, title, sql)

    print("\n=== Text mining ===")
    for title, sql in TEXT_QUERIES.items():
        run_report(conn, title, sql)

    print("\nTop terms by product")
    products = [row[0] for row in conn.execute("SELECT name FROM dim_product ORDER BY name")]
    for product in products:
        terms = ", ".join(f"{term} ({frequency})" for term, frequency in top_terms(conn, product, 5))
        print(f"  {product}: {terms}")


if __name__ == "__main__":
    main()
