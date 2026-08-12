HabotConnect Backend



A Django REST Framework backend for an LSA (Life Skills Assistant) service booking platform.



The project demonstrates practical backend engineering concepts including authentication, role-based authorization, booking workflows, filtering, pagination, database transactions, query optimization, and automated testing.



Tech Stack

Python

Django

Django REST Framework

Django Filter

SQLite for local development/testing

PostgreSQL-compatible Django ORM

Git/GitHub

Project Structure

habotConnect/

├── accounts/

│   ├── models.py

│   ├── permissions.py

│   ├── serializers.py

│   ├── views.py

│   └── tests.py

│

├── booking/

│   ├── models.py

│   ├── permissions.py

│   ├── serializers.py

│   ├── views.py

│   └── tests.py

│

├── habotConnect/

│   ├── settings.py

│   ├── urls.py

│   ├── asgi.py

│   └── wsgi.py

│

├── manage.py

├── requirements.txt

├── .gitignore

└── README.md

User Roles



The application supports three roles:



Customer

Create bookings

View own bookings

Cancel pending bookings

Provider

View assigned bookings

Confirm pending bookings

Complete confirmed bookings

Admin

View bookings

Assign providers to pending bookings

Booking Workflow

PENDING

&#x20;  │

&#x20;  ├── Customer cancels

&#x20;  │       ↓

&#x20;  │   CANCELLED

&#x20;  │

&#x20;  └── Provider confirms

&#x20;          ↓

&#x20;      CONFIRMED

&#x20;          │

&#x20;          └── Provider completes

&#x20;                  ↓

&#x20;              COMPLETED

Booking APIs

Method	Endpoint	Description

POST	/bookings/	Create booking

GET	/bookings/	List bookings

GET	/bookings/{id}/	Retrieve booking

PUT	/bookings/{id}/	Update booking

PATCH	/bookings/{id}/	Partially update booking

DELETE	/bookings/{id}/	Delete booking

Booking Actions

Method	Endpoint	Description

POST	/bookings/{id}/assign\_provider/	Admin assigns provider

POST	/bookings/{id}/confirm/	Provider confirms booking

POST	/bookings/{id}/complete/	Provider completes booking

POST	/bookings/{id}/cancel/	Customer cancels booking

Filtering



Bookings can be filtered by status:



GET /bookings/?status=PENDING



Bookings can also be filtered by date:



GET /bookings/?booking\_date=2026-08-20

Pagination



The booking list API supports Django REST Framework pagination.



Example:



{

&#x20;   "count": 10,

&#x20;   "next": null,

&#x20;   "previous": null,

&#x20;   "results": \[]

}

Database Query Optimization



The booking queryset uses Django's select\_related() for ForeignKey relationships:



.select\_related(

&#x20;   "customer",

&#x20;   "provider"

)



This allows Django to retrieve booking, customer, and provider information using SQL joins instead of performing additional database queries for each related object.



Conceptually:



Without optimization:



Booking

&#x20; ↓

Customer query

Provider query

Customer query

Provider query

...



With select\_related():



Booking

&#x20; ├── Customer

&#x20; └── Provider



Single JOIN-based query

N+1 Query Regression Testing



The project includes a query optimization test to verify that accessing related customer and provider objects does not generate unnecessary additional database queries.



This helps prevent future N+1 query regressions.



Testing



The project includes automated tests covering:



Customer booking creation

Customer booking visibility

Customer booking cancellation

Provider booking confirmation

Admin provider assignment

Status filtering

Booking-date filtering

Query optimization



Run all tests:



python manage.py test



Current status:



8 tests passed



Run booking tests only:



python manage.py test booking

Local Setup

1\. Clone the repository

git clone <YOUR\_GITHUB\_REPOSITORY\_URL>

cd habotConnect

2\. Create a virtual environment



Windows:



python -m venv habot\_env



Activate it:



.\\habot\_env\\Scripts\\Activate.ps1

3\. Install dependencies

pip install -r requirements.txt

4\. Apply migrations

python manage.py migrate

5\. Create a superuser

python manage.py createsuperuser

6\. Run the server

python manage.py runserver



The application will run at:



http://127.0.0.1:8000/

Security



The repository excludes sensitive and generated files such as:



.env

db.sqlite3

\_\_pycache\_\_/

virtual environments



Secrets and production credentials should never be committed to Git.



Current Implementation

Completed



Django project setup



User roles



Booking model



Booking serializer



Booking ViewSet



Customer booking creation



Customer booking visibility



Customer cancellation



Provider confirmation



Provider completion



Admin provider assignment



Filtering



Pagination



Role-based permissions



Transaction handling



select\_related() optimization



N+1 query regression testing



Automated tests



Planned



LSA/provider search API



Double-booking concurrency protection



Mock PaymentService



Payment webhook



Webhook idempotency



CI/CD pipeline



Additional production-level tests



Author



Harish P



Python Backend Developer



Skills

Python

Django

Django REST Framework

PostgreSQL

SQL

JWT

Django ORM

Celery

Redis

Docker

AWS

FastAPI

REST APIs

Microservices

License



This project was developed as a backend engineering assignment and interview project demonstration.

