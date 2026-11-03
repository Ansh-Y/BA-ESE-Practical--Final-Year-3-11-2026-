from datetime import date

PRODUCTS = [
    ("P-100", "Wireless Earbuds", "Electronics"),
    ("P-200", "Yoga Mat", "Fitness"),
    ("P-300", "Steel Water Bottle", "Home"),
    ("P-400", "Smart Watch", "Electronics"),
]

CUSTOMERS = [
    ("C-01", "Asha", "North"),
    ("C-02", "Ravi", "South"),
    ("C-03", "Meera", "West"),
    ("C-04", "Kiran", "East"),
]

# date, product_id, customer_id, quantity, unit_price
SALES = [
    (date(2024, 1, 15), "P-100", "C-01", 2, 1999.0),
    (date(2024, 2, 3), "P-200", "C-02", 1, 899.0),
    (date(2024, 2, 20), "P-400", "C-03", 1, 4999.0),
    (date(2024, 4, 11), "P-300", "C-04", 3, 449.0),
    (date(2024, 5, 6), "P-100", "C-03", 1, 1999.0),
    (date(2024, 7, 19), "P-400", "C-01", 2, 4999.0),
    (date(2024, 8, 2), "P-200", "C-04", 4, 899.0),
    (date(2024, 10, 14), "P-300", "C-02", 2, 449.0),
    (date(2024, 11, 25), "P-100", "C-02", 3, 1799.0),
    (date(2024, 12, 9), "P-400", "C-04", 1, 4599.0),
]

# date, product_id, customer_id, rating (1-5), review text
REVIEWS = [
    (date(2024, 1, 22), "P-100", "C-01", 5, "Great sound and comfortable fit. Battery life is excellent."),
    (date(2024, 2, 10), "P-200", "C-02", 2, "The mat is thin and slippery. Disappointed with the grip."),
    (date(2024, 3, 1), "P-400", "C-03", 4, "Nice display and fast sync. Strap feels a bit cheap."),
    (date(2024, 4, 18), "P-300", "C-04", 5, "Keeps water cold for hours. Durable and perfect for travel."),
    (date(2024, 5, 14), "P-100", "C-03", 1, "Broke within a week. Poor quality and bad packaging."),
    (date(2024, 7, 25), "P-400", "C-01", 3, "Average performance. Battery drains fast but features are good."),
    (date(2024, 8, 9), "P-200", "C-04", 4, "Good cushioning and nice texture. Easy to clean."),
    (date(2024, 10, 20), "P-300", "C-02", 2, "Lid leaks and the bottle arrived dented. Very disappointed."),
    (date(2024, 11, 30), "P-100", "C-02", 5, "Amazing bass and great noise cancellation. Love it."),
    (date(2024, 12, 15), "P-400", "C-04", 4, "Excellent health tracking. Setup was easy and the app is good."),
]
