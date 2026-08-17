# E-Commerce Food Products Sales Forecasting System

Python + MySQL 

Python uses mysql-connector-python to read/write MySQL data.

Forecast method:
1. Read monthly sales from MySQL.
2. Calculate month-to-month percentage growth using normal Python.
3. Calculate average historical growth.
4. Calculate the latest 3-month average.
5. Start from a weighted recent sales value.
6. Apply average growth for the next 12 months.

Setup:
1. Execute database.sql in MySQL Workbench.
2. Open main.py.
3. Change YOUR_MYSQL_PASSWORD to your MySQL root password.
4. Install only: python -m pip install mysql-connector-python
5. Run: python main.py

Admin:
Email: admin@example.com
Password: admin123
