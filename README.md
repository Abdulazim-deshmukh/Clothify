# Clothify — Django Fashion Store

Clothify is a beginner-friendly full-stack e-commerce project built with **Django, SQLite, HTML and CSS**.

The project demonstrates a complete basic shopping flow without unnecessary third-party payment or email systems.

## Features

### Customer
- Home page and product catalogue
- Product detail page
- Customer registration and login
- Password hashing with Django's password hashers
- Shopping cart
- Quantity update and product removal
- Checkout and delivery details
- Order placement and confirmation page
- FAQs and return policy pages

### Admin
- Admin login using the project's `Admin` model
- Dashboard with product, customer and order counts
- Add, edit and delete products
- View registered customers
- View placed orders

## Tech Stack

- Python
- Django
- SQLite
- HTML
- CSS
- Small vanilla JavaScript enhancement
- Pillow for product image uploads

## Run locally

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Then open `http://127.0.0.1:8000/`.

## Project structure

```text
Clothify-app/
├── Template/
│   ├── admin/
│   ├── Base.html
│   ├── index.html
│   ├── shop.html
│   ├── product_detail.html
│   ├── register.html
│   ├── login.html
│   ├── cart.html
│   ├── checkout.html
│   └── order_success.html
├── clothify/
├── clothifyapp/
│   ├── migrations/
│   └── static/
├── media/
├── db.sqlite3
├── manage.py
└── requirements.txt
```

## Notes

- SQLite is intentionally kept for this learning project.
- Online payment is not included; checkout places the order directly.
- Email/SMTP integration is not included.
- The project uses Django sessions for the custom customer/admin login flow.
- For production deployment, use environment variables for secrets and set `DEBUG = False`.
