# PenLedger: A Django Inventory & Sales Tracker

**Project Status:** Live / Deployed

## Project Overview

This pen tracker is a full-stack web application built with Django, designed for the niche business of refurbishing and selling vintage fountain pens. It replaces manual spreadsheet tracking with a database system that provides a comprehensive overview of inventory, costs, and profitability. The application is designed to be my small business dashboard, tracking each pen's lifecycle from acquisition to final sale.

The front-end is styled with custom CSS for a clean, modern and responsive user experience. The back-end is deployed on a self-hosted Ubuntu server using a Gunicorn/Nginx stack.

## Technologies Used

-   **Backend:** Python, Django, Gunicorn
-   **Frontend:** HTML, CSS, JavaScript
-   **Database:** PostgreSQL (Production), SQLite (Development)
-   **Deployment:** Ubuntu Server, Nginx, Systemd
-   **Visualizations:** Chart.js

## Key Features

-   **CRUD Functionality:** Complete Create, Read, Update, and Delete capabilities for all key business entities: pens, parts, sales, and general expenses.
-   **Financial Dashboard:** The homepage provides an overview of business health, with KPIs and a cumulative line graph showing Revenue vs. Net Profit for the current UK tax year.
-   **Historical Reporting:** A dedicated reports section allows for viewing financial summaries for any previous tax year, with the ability to download detailed sales and expense data as a CSV file for accounting.
-   **Cost Tracking:** The system tracks not only the acquisition cost of a pen but also the specific cost of any spare parts used during refurbishment, providing true net profit calculation.
-   **Inventory Management:** The parts inventory supports tracking multiple batches of the same part at different purchase prices and automatically decrements stock as parts are used.
-   **Watchlist:** A separate module for tracking desired pens.
-   **Secure Authentication:** A complete login/logout system.

## Screenshots

Here are a few key pages from the application:

**Main Dashboard:**
![Main Dashboard](path/to/your/dashboard_image.png)

**Pen Inventory:**
![Pen Inventory](path/to/your/pen_inventory_image.png)

**Parts Inventory:**
![Parts Inventory](path/to/your/parts_inventory_image.png)

**Expenses:**
![Expenses List](path/to/your/expenses_image.png)

**All Sales:**
![All Sales List](path/to/your/all_sales_image.png)

**Reports:**
![Reports Page](path/to/your/reports_image.png)

**Watchlist:**
![Watchlist Page](path/to/your/watchlist_image.png)

## How to Run Locally

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/wsj20/marketplace-notifier.git
    cd pen-tracker
    ```
2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```
3.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Create a local `.env` file:**
    In the project root, create a file named `.env` and add the following for local development:
    ```env
    SECRET_KEY=temp_local_secret_key
    DEBUG=True
    DATABASE_URL=sqlite:///db.sqlite3
    ALLOWED_HOSTS=127.0.0.1,localhost
    ```
5.  **Run migrations and create a superuser:**
    ```bash
    python manage.py migrate
    python manage.py createsuperuser
    ```
6.  **Run the development server:**
    ```bash
    python manage.py runserver
    ```
    The app will be available at `http://127.0.0.1:8000`.

## Contact

Created by Will Clarke
-   [LinkedIn](https://www.linkedin.com/in/will-clarke-cs/)
-   [GitHub](https://github.com/wsj20)
