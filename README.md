# HabotConnect Backend

A production-oriented **Django REST Framework backend** for an LSA (Life Skills Assistant) service booking platform.

HabotConnect demonstrates practical backend engineering concepts including **JWT authentication, role-based authorization, booking workflows, provider assignment, availability validation, filtering, pagination, database transactions, query optimization, automated testing, and Git/GitHub practices**.

---

## 📌 Project Overview

HabotConnect manages the lifecycle of service bookings between **Customers** and **Providers**, with an **Admin** responsible for assigning providers.

The backend enforces role-specific access and booking state transitions at the API level.

### Core Workflow

```text
Customer
   │
   │ Create Booking
   ▼
PENDING
   │
   ├─────────────── Customer Cancels ───────────────► CANCELLED
   │
   │ Admin Assigns Provider
   ▼
Provider
   │
   │ Confirm
   ▼
CONFIRMED
   │
   │ Complete
   ▼
COMPLETED
```

---

## 👥 User Roles

| Role         | Responsibilities                                                              |
| ------------ | ----------------------------------------------------------------------------- |
| **Customer** | Create bookings, view own bookings, cancel pending bookings                   |
| **Provider** | View assigned bookings, confirm pending bookings, complete confirmed bookings |
| **Admin**    | Assign providers and manage provider assignment workflow                      |

Authorization is enforced **server-side** using Django REST Framework permission classes.

---

## ✨ Implemented Features

### Authentication & Authorization

* Custom User model
* JWT authentication
* Role-based authorization
* Customer, Provider and Admin roles
* Server-side permission enforcement

### Booking Management

* Create booking
* View authorized bookings
* Customer booking cancellation
* Provider booking confirmation
* Provider booking completion
* Admin provider assignment
* Provider role validation
* Provider availability validation
* Booking status management

### API Features

* RESTful API design
* DRF ViewSets
* DRF Serializers
* Custom ViewSet actions
* Filtering by booking status
* Filtering by booking date
* Pagination

### Database & Performance

* Django ORM
* Database transactions
* `transaction.atomic()`
* `IntegrityError` handling
* `select_related()` optimization
* N+1 query regression testing

### Testing & Engineering

* Automated Django tests
* 8 tests passing
* Query-count regression testing
* Git/GitHub version control
* README documentation
* Dependency management using `requirements.txt`
* `.gitignore` for local development artifacts

---

# 🏗️ Architecture

```text
                    Client / Postman
                           │
                           ▼
              Django REST Framework
                           │
                           ▼
                       ViewSets
                           │
                           ▼
                      Serializers
                           │
                           ▼
                      Django ORM
                           │
                           ▼
                     Database
```

Cross-cutting components:

```text
JWT Authentication
        │
        ▼
Role-Based Permissions
        │
        ▼
Booking Business Rules
        │
        ├── Filtering
        ├── Pagination
        ├── Transactions
        └── Query Optimization
```

---

# 📂 Project Structure

```text
habotConnect/
│
├── accounts/
│   ├── models.py
│   ├── permissions.py
│   └── ...
│
├── booking/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── permissions.py
│   ├── tests.py
│   └── ...
│
├── habotConnect/
│   ├── settings.py
│   ├── urls.py
│   └── ...
│
├── manage.py
├── requirements.txt
├── README.md
└── .gitignore
```

### `accounts/`

Responsible for:

* Custom User model
* User roles
* Authentication-related configuration
* Permission logic

### `booking/`

Responsible for:

* Booking model
* Booking serializer
* Booking ViewSet
* Booking business rules
* Booking permissions
* Automated tests

### `habotConnect/`

Contains the main Django project configuration including:

* Settings
* URL routing
* DRF configuration

---

# 🗄️ Data Model

The current implementation primarily uses the following entities:

```text
                 User
                  │
          ┌───────┴────────┐
          │                │
       Customer          Provider
          │                │
          │                │
          └───────┬────────┘
                  │
                  ▼
               Booking
```

## User

The custom User model supports:

```text
CUSTOMER
PROVIDER
ADMIN
```

## Booking

The Booking model contains information such as:

```text
customer
provider
service
booking_date
booking_time
status
notes
created_at
updated_at
```

The customer and provider relationships use Django `ForeignKey` relationships.

---

# 🔐 Authentication & Authorization

The API uses **JWT authentication**.

Authentication and authorization are treated as separate concerns.

### Authentication

Determines:

> "Who is making this request?"

### Authorization

Determines:

> "Is this user allowed to perform this action?"

For example:

```text
Customer
   │
   ├── Create Booking       ✓
   ├── Cancel Own Booking  ✓
   ├── Confirm Booking     ✗
   └── Assign Provider     ✗
```

```text
Provider
   │
   ├── Confirm Booking     ✓
   ├── Complete Booking   ✓
   ├── Cancel Booking      ✗
   └── Assign Provider     ✗
```

```text
Admin
   │
   └── Assign Provider     ✓
```

Permissions are enforced on the backend rather than relying on frontend restrictions.

---

# 🔌 API Endpoints

## Booking APIs

### Create Booking

```http
POST /bookings/
```

**Role:** Customer

Example request:

```json
{
    "service": "Tutoring",
    "booking_date": "2026-08-20",
    "booking_time": "10:00",
    "notes": "Morning session"
}
```

---

### List Bookings

```http
GET /bookings/
```

Returns bookings visible to the authenticated user according to their role.

---

### Retrieve Booking

```http
GET /bookings/{id}/
```

---

### Assign Provider

```http
POST /bookings/{id}/assign_provider/
```

**Role:** Admin

The assignment process validates:

* Booking status
* Provider existence
* Provider role
* Provider availability

---

### Confirm Booking

```http
POST /bookings/{id}/confirm/
```

**Role:** Provider

A provider can confirm an assigned pending booking.

---

### Complete Booking

```http
POST /bookings/{id}/complete/
```

**Role:** Provider

Only confirmed bookings can be completed.

---

### Cancel Booking

```http
POST /bookings/{id}/cancel/
```

**Role:** Customer

Customers can cancel their own pending bookings.

---

# 🔄 Booking State Management

The booking lifecycle is:

```text
                ┌──────────────┐
                │    PENDING   │
                └──────┬───────┘
                       │
             ┌─────────┴─────────┐
             │                   │
       Customer Cancel      Provider Confirm
             │                   │
             ▼                   ▼
       ┌───────────┐       ┌────────────┐
       │ CANCELLED │       │ CONFIRMED  │
       └───────────┘       └──────┬─────┘
                                  │
                              Complete
                                  │
                                  ▼
                           ┌────────────┐
                           │ COMPLETED  │
                           └────────────┘
```

The API validates the current booking state before allowing state-changing operations.

---

# 🔎 Filtering

The booking endpoint supports filtering by status and booking date.

### Filter by status

```http
GET /bookings/?status=PENDING
```

### Filter by booking date

```http
GET /bookings/?booking_date=2026-08-20
```

Filtering is implemented using:

```python
DjangoFilterBackend
```

and configured filter fields.

---

# 📄 Pagination

Booking list APIs use pagination to avoid returning an unnecessarily large dataset.

Example response:

```json
{
    "count": 10,
    "next": "...",
    "previous": null,
    "results": [
        {
            "id": 1,
            "status": "PENDING"
        }
    ]
}
```

Pagination helps control:

* Response size
* Database workload
* Serialization overhead
* API response time

---

# ⚡ N+1 Query Optimization

One of the important performance optimizations implemented in HabotConnect is prevention of the **N+1 query problem**.

## The Problem

Suppose the API retrieves 100 bookings.

Without optimization:

```text
1 query → Fetch bookings

Booking 1 → Customer query
          → Provider query

Booking 2 → Customer query
          → Provider query

Booking 3 → Customer query
          → Provider query

...

Booking 100 → Customer query
            → Provider query
```

This can result in a large number of database queries.

---

## The Solution

The Booking query uses:

```python
.select_related(
    "customer",
    "provider"
)
```

Because `customer` and `provider` are `ForeignKey` relationships, `select_related()` can use SQL joins to retrieve the related objects efficiently.

Conceptually:

```text
                  Database
                     │
                     ▼
              Booking Query
                     │
             ┌───────┴───────┐
             ▼               ▼
          Customer        Provider
             │               │
             └───────┬───────┘
                     ▼
                API Response
```

### Why this matters

Instead of repeatedly querying the database for related objects, the required relationships are fetched efficiently as part of the main query.

This reduces:

* Database round trips
* Query overhead
* API latency
* Database load

---

# 🧪 N+1 Regression Testing

The optimization is also protected by an automated query-count test.

The test verifies that accessing related:

```text
customer
provider
```

does not unexpectedly generate additional queries.

This is important because an optimization can accidentally be removed during a future refactor.

The regression test acts as a safety net.

---

# 💳 Database Transactions

Provider assignment involves multiple validation steps.

The general flow is:

```text
Request
   │
   ▼
Validate Input
   │
   ▼
Check Provider
   │
   ▼
Check Provider Role
   │
   ▼
Check Availability
   │
   ▼
transaction.atomic()
   │
   ▼
Assign Provider
   │
   ▼
Save Booking
   │
   ▼
Commit
```

Transactions provide an all-or-nothing boundary around database changes.

This helps prevent partially applied updates when an operation fails.

---

# ⚠️ Error Handling

The implementation also handles:

```python
IntegrityError
```

Application-level validation is important, but it is not the only protection.

The database can still reject an operation because of integrity constraints.

The backend therefore handles database-level errors explicitly rather than allowing uncontrolled database exceptions to become API failures.

---

# 🧪 Testing

Current test status:

```text
8 Tests
8 Passed
0 Failed
```

### Test Coverage

| Test                      | Purpose                            |
| ------------------------- | ---------------------------------- |
| Customer booking creation | Verifies customer booking creation |
| Customer visibility       | Verifies booking access rules      |
| Customer cancellation     | Verifies cancellation workflow     |
| Provider confirmation     | Verifies provider confirmation     |
| Admin assignment          | Verifies provider assignment       |
| Status filtering          | Verifies status filtering          |
| Date filtering            | Verifies booking-date filtering    |
| N+1 regression            | Verifies query optimization        |

### Development Workflow

```text
Write Code
    ↓
Run Tests
    ↓
Fix Issues
    ↓
Run Full Test Suite
    ↓
Commit
    ↓
Push to GitHub
```

---

# 🛠️ Technology Stack

| Technology                           | Purpose                       |
| ------------------------------------ | ----------------------------- |
| **Python**                           | Backend programming language  |
| **Django**                           | Web framework                 |
| **Django REST Framework**            | REST API development          |
| **Django ORM**                       | Database interaction          |
| **Django Filters**                   | API filtering                 |
| **JWT**                              | Authentication                |
| **SQLite**                           | Development/testing database  |
| **PostgreSQL-compatible ORM design** | Production database readiness |
| **Git**                              | Version control               |
| **GitHub**                           | Source-code hosting           |
| **Django Tests**                     | Automated testing             |

---

# 🚀 Local Setup

## 1. Clone the repository

```bash
git clone https://github.com/harishpochina2296/habotconnect-backendd.git
```

```bash
cd habotconnect-backendd
```

---

## 2. Create a virtual environment

### Windows

```bash
python -m venv venv
```

Activate:

```bash
venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv venv
```

```bash
source venv/bin/activate
```

---

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Apply migrations

```bash
python manage.py migrate
```

---

## 5. Create a superuser

```bash
python manage.py createsuperuser
```

Follow the prompts.

---

## 6. Run the development server

```bash
python manage.py runserver
```

The development server will be available at:

```text
http://127.0.0.1:8000/
```

---

# 🧪 Running Tests

Run the complete test suite:

```bash
python manage.py test
```

Expected current result:

```text
8 tests passed
```

The tests cover booking workflows, role-specific behavior, filtering and N+1 query regression protection.

---

# 🔮 Future Roadmap

The following features are **planned improvements and are not part of the current implemented scope**.

### Provider / LSA Search

A dedicated provider search API with additional filtering capabilities.

### Stronger Double-Booking Protection

Introduce stronger database-level concurrency protection using appropriate transaction isolation and row-level locking where applicable.

### Payment Integration

Potential future architecture:

```text
Booking
   │
   ▼
PaymentService
   │
   ▼
Payment Provider
   │
   ▼
Webhook
```

### Webhook Idempotency

Protect webhook processing from duplicate delivery.

### CI/CD

Introduce automated:

```text
GitHub
   ↓
CI Pipeline
   ↓
Tests
   ↓
Quality Checks
   ↓
Build
   ↓
Deployment
```

### Deployment

Deploy the Django backend using a production-ready infrastructure and PostgreSQL database.

### Additional Production Testing

Expand testing around:

* Concurrency
* Authentication failures
* Permission boundaries
* Edge cases
* Database constraints
* API error responses

---

# 🔒 Production Considerations

For a production deployment, I would additionally focus on:

* PostgreSQL
* Environment-based configuration
* Secret management
* HTTPS
* Structured logging
* Monitoring
* API rate limiting
* CI/CD
* Database backups
* Stronger concurrency protection
* Production deployment configuration

These are **future production enhancements**, not claims about the current implementation.

---

# 📈 Engineering Highlights

The main engineering concepts demonstrated in this project are:

### 1. Role-Based Authorization

Different users have different capabilities.

### 2. State-Based Business Logic

Booking actions depend on the current booking status.

### 3. Transaction Safety

Multi-step database operations use transaction boundaries.

### 4. Query Optimization

`select_related()` prevents unnecessary database queries for ForeignKey relationships.

### 5. Regression Testing

Query-count testing protects the N+1 optimization from future regressions.

### 6. API Scalability

Filtering and pagination prevent unnecessarily large API responses.

### 7. Maintainability

The project separates accounts, booking logic, configuration and tests.


---

# 👨‍💻 Author

**Harish P.**

Python Backend Developer

### Technical Focus

```text
Python
Django
Django REST Framework
REST APIs
PostgreSQL / SQL
Django ORM
JWT Authentication
Celery
Redis
Git / GitHub
Docker
AWS Basics
FastAPI Basics
Microservices
```

---

# 🔗 Repository

**GitHub:**

https://github.com/harishpochina2296/habotconnect-backend

---

# 📄 License

This project was developed as a Python/Django Backend Developer assignment and portfolio project.
