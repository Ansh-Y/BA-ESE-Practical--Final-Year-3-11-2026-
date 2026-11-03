import unittest

from data import REVIEWS, SALES
from queries import TEXT_QUERIES, top_terms
from star_schema import build_star_schema, to_date_key
from text_mining import sentiment_label, sentiment_score, tokenize


class StarSchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.conn = build_star_schema()

    def count(self, table):
        return self.conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]

    def test_fact_row_counts_match_source(self):
        self.assertEqual(self.count("fact_sales"), len(SALES))
        self.assertEqual(self.count("fact_review"), len(REVIEWS))

    def test_no_orphan_foreign_keys(self):
        self.assertEqual(self.conn.execute("PRAGMA foreign_key_check").fetchall(), [])

    def test_revenue_total_matches_source(self):
        expected = sum(quantity * price for _, _, _, quantity, price in SALES)
        actual = self.conn.execute("SELECT SUM(revenue) FROM fact_sales").fetchone()[0]
        self.assertAlmostEqual(actual, expected, places=2)

    def test_every_review_has_terms(self):
        reviewed = self.conn.execute(
            "SELECT COUNT(DISTINCT review_key) FROM fact_review_term"
        ).fetchone()[0]
        self.assertEqual(reviewed, len(REVIEWS))

    def test_date_dimension_quarter(self):
        quarter = self.conn.execute(
            "SELECT quarter FROM dim_date WHERE date_key = ?", (to_date_key(SALES[-2][0]),)
        ).fetchone()[0]
        self.assertEqual(quarter, 4)

    def test_all_text_queries_run(self):
        for title, sql in TEXT_QUERIES.items():
            with self.subTest(query=title):
                self.assertTrue(self.conn.execute(sql).fetchall())

    def test_top_terms_are_per_product(self):
        terms = [term for term, _ in top_terms(self.conn, "Smart Watch", 3)]
        self.assertTrue(terms)
        self.assertNotIn("bottle", terms)


class TextMiningTests(unittest.TestCase):
    def test_tokenize_removes_stopwords_and_short_words(self):
        self.assertEqual(tokenize("The bottle is great and it is a gift"), ["bottle", "great", "gift"])

    def test_sentiment_score_bounds(self):
        self.assertEqual(sentiment_score(["great", "excellent"]), 1.0)
        self.assertEqual(sentiment_score(["poor", "bad"]), -1.0)
        self.assertEqual(sentiment_score(["great", "poor"]), 0.0)
        self.assertEqual(sentiment_score(["bottle"]), 0.0)

    def test_sentiment_label_thresholds(self):
        self.assertEqual(sentiment_label(0.5), "Positive")
        self.assertEqual(sentiment_label(-0.5), "Negative")
        self.assertEqual(sentiment_label(0.1), "Neutral")


if __name__ == "__main__":
    unittest.main()
