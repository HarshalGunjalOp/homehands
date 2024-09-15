# Household Services Application

## Project Overview

The **Household Services Application** is a platform designed to provide comprehensive home servicing solutions, connecting customers with service professionals. The platform supports three roles: Admin, Service Professionals, and Customers, each with specific functionalities tailored to their needs.

## Features

### Admin Role

- **Admin Login:** The Admin can log in using a dedicated login form.
- **Dashboard:** Admins can view, manage, and monitor all users (customers and professionals).
- **Service Management:** Admins can create, update, and delete services, including service descriptions, pricing, and banners.
- **Professional Verification:** Admins can verify service professionals by reviewing their profile documents.
- **User Management:** Admins can block/unblock users based on activity, reviews, or fraudulent behavior.

### Service Professional Role

- **Registration & Login:** Service professionals can register and log in to the platform.
- **Profile Management:** Professionals can manage their profiles, including name, experience, and service type.
- **Service Request Management:** View, accept/reject, and close service requests assigned to them.
- **Customer Reviews:** View customer feedback and reviews after completing a service.

### Customer Role

- **Registration & Login:** Customers can register and log in to book services.
- **Search Services:** Search for available services by name or location (e.g., pin code).
- **Service Request:** Create, update, and close service requests.
- **Review Services:** Post reviews and remarks after the service is completed.

## Technologies Used

- **Flask**: Used as the web framework to build the application.
- **Jinja2 Templates**: For dynamic HTML generation.
- **Bootstrap**: For responsive front-end design and styling.
- **SQLite**: Used for data storage.
- **Flask-Login**: Implemented for secure user authentication.
- **Flask-WTF**: Used for form handling and validation.
- **Werkzeug**: For secure password hashing and protection.
- **Flask-SQLAlchemy**: Used for ORM.
- **Re**: Used for password and email validation using regular expressions.

## Project Structure

```text
.
├── app
│   ├── admin.py
│   ├── auth.py
│   ├── customer.py
│   ├── __init__.py
│   ├── models.py
│   ├── professional.py
│   ├── static
│   └── templates
├── app.py
├── package.json
├── package-lock.json
├── project_structure.txt
├── README.md
└── requirements.txt
```

## Database Design

The application has four main models:

1. **Service**:
   - ID, Price, Time Required, Description, Banner, Provider (linked to professional).
2. **Customer**:
   - ID, First Name, Last Name, Username, Email, Password Hash, Profile Picture, Address, Role.
3. **Professional**:
   - ID, First Name, Last Name, Username, Email, Password Hash, Profile Picture, Role.
4. **Request**:
   - ID, Service ID, Customer ID, Professional ID, Date of Request, Date of Completion, Service Status, Remarks.

## Setup and Installation

### Prerequisites

- Python 3.8+

### Steps to Run Locally

1. Clone the repository:

   ```bash
   git clone https://github.com/HarshalGunjalOp/homehands.git
   cd homehands

2. Setup a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`

3. Install the dependencies:

   ```bash
   pip install -r requirements.txt

4. Start the Flask application:

   ```bash
   flask run

5. Open your browser and navigate to `http://localhost:5000` to see the app in action.
