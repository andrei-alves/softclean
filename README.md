# SoftClean

#### Video Demo:  https://youtu.be/NxbI-WMlAko
#### Description:
This project consists of a web based application writen in the Flask python framework. The app was designed to serve as a management system for a upholstery cleanning business. It has basically five principal functionalities: (1) Registring of customers; (2) Registring of service orders; (3) Registring of services offered; (4) Registring of staff members; and (5) Dashboard visualisation of services scheduled. For each functionality there is a web page. In each page there are subfeatures that helps managing the entries registered in the database.

## Project Files Description

The root directory of the project contains 3 files besides this README. The main file of the project is app.py, here is the flask application per se. There is also a helpers.py file containing an auxiliary function. And last is the database file.

### app.py
The app.py contains the bulk of the application. In it there are 22 functions that controls all the features of the system.

### helpers.py
This file contains only one function that is used as a decorator in all other functions of the app.py and helps guarantee that only loged in users access the app pages.

### database.db
The database.db file consists of the system database. In it are six tables that stores all the data handled by the software. The tables are the following: (1) users: The users table stores in four columms (id, username, hash, permission) the information of the system users; (2) customers: The customers tables stores in nine columms (id, name, phone, phone2, address, address_number, address_complement, neighborhood, city) the information of the customers; (3) The services table stores in four columms (id, type, description, price) the information of the services offered by the business. (4) The orders table is the core table and stores the information of the service orders in eleven columms (id, customer_id, register_date, execution_date, time, amount, discount, status, payment, payment_status, technician); (5) The services_ordered table stores in six columms (id, order_id, service, quantity, price_un, discount_un) the information of the individual services ordered in each service order; and (6) The staff table stores the information of the staff members in three columms (id, name, role).

## Project Folders Description

The project contains three subfolders /flask_session, /static, /templates.

### /flask_session
This folder is automatically created by the flask framework for storing the users sessions. The sessions are configured for lasting three hours.

### /static
This folder contains some icons and images that are used in the project. Also there is a CSS file that takes care of removing the defauld decoration (spin arrows) of the number input fields.

### /templates
This folder contains the HTML files that are rendered by the application. There are thirteen in all. Following are described the basic layout of the main files: (1) The customer.html renders a bootstrap modal and a table that receives the all the customers entries; (2) The index.html renders a table with two rows and six columms that displays the services scheduled in the current and next week; (3) The orders.html renders a bootstrap modal and a table with all the orders registered; (4) The services.html renders a bootstrap modal and a table with all the services offered by the business; and (5) The staff.html also renders a bootstrat modal and a table with all the staff members registered.
