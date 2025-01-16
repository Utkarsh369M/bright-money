# Loan Management Service

### Requirements

- Python 3.6.8
- Django==3.2.11
- django-extensions==3.1.0
- celery==5.1.2
- django-celery-results==2.2.0
- redis==4.3.6
- ipython==7.13.0
- requests==2.27.1
- pytest==7.0.1

### Steps to Run

1. Clone the GitHub repository:
   ```bash
   git clone https://github.com/Utkarsh369M/bright-money.git
   ```
2. Navigate to the project directory:
   ```bash
   cd bright-money/loan_management
   ```
3. Apply database migrations:
   ```bash
   python manage.py migrate
   ```
4. Start the server:
   ```bash
   python manage.py runserver
   ```
5. Run tests:
   ```bash
   python manage.py test
   ```

---

### Entities and Models

#### UserInformation:
- **name**: Name of the user
- **email**: Email of the user
- **annual_income**: Annual income of the user
- **aadhar_id**: Unique identifier (Aadhar ID)
- **credit_score**: Credit score of the user
- **user_uuid**: Unique UUID generated for each registered user

#### UserTransactionInformation:
- **aadhar_id**: Aadhar ID of the user
- **registration_date**: Transaction registration date
- **amount**: Transaction amount
- **transaction_type**: Type of transaction (CREDIT or DEBIT)

#### LoanInfo:
- **loan_id**: Unique UUID for the loan
- **user_uuid**: Foreign key to UserInformation’s `user_uuid`
- **loan_type**: Type of loan applied (currently supports Credit Card loans)
- **loan_amount**: Loan amount in rupees
- **annual_interest_rate**: Annual rate of interest
- **term_period**: Repayment term in months
- **disbursement_date**: Loan disbursement date

#### EMIDetails:
- **loan_id**: Foreign key to LoanInfo’s `loan_id`
- **amount_due**: EMI due each month in rupees
- **amount_paid**: EMI paid each month in rupees
- **installment_date**: Date of EMI installment

#### BillingDetails:
- **user_uuid**: Foreign key to UserInformation’s `user_uuid`
- **billing_date**: Date of the billing cycle
- **due_date**: Due date for payment (15 days after billing date)
- **min_due**: Minimum due for the billing cycle

#### DuePayments:
- **user_uuid**: Foreign key to UserInformation’s `user_uuid`
- **billing_id**: Foreign key to BillingDetails’ `id`
- **amount_due**: Outstanding amount
- **amount_paid**: Amount paid

---

### API Endpoints

#### 1. Register User
- **URL**: `/api/register-user/`
- **Method**: POST
- **Request Body**:
  ```json
  {
      "aadhar_id": 123456789,
      "name": "Utkarsh",
      "email": "utkarsh@test.com",
      "annual_income": 1500000
  }
  ```
- **Description**:
  - Registers a user and calculates their credit score asynchronously using Celery.
  - Generates a unique `user_uuid` for the user.
- **Response**:
  ```json
  {
      "message": "User successfully registered",
      "data": {
          "user_uuid": "c9577b41-daaf-4276-9403-ba825fd1058c"
      },
      "success": "True"
  }
  ```

#### 2. Apply Loan
- **URL**: `/api/apply-loan/`
- **Method**: POST
- **Request Body**:
  ```json
  {
      "user_uuid": "c9577b41-daaf-4276-9403-ba825fd1058c",
      "loan_type": "CREDIT_CARD",
      "loan_amount": 5000,
      "interest_rate": 15,
      "term_period": 12,
      "disbursement_date": "2023-07-19"
  }
  ```
- **Description**:
  - Applies for a loan if the user's credit score is ≥450 and annual income is ≥1,50,000.
  - Calculates EMI details and generates a unique `loan_id`.
- **Response**:
  ```json
  {
      "message": "Loan applied successfully",
      "data": {
          "EMI_details": [
              {"amount_due": 450.0, "installment_date": "2023-08-01"},
              {"amount_due": 450.0, "installment_date": "2023-09-01"}
          ],
          "loan_id": "398ed9c2-287d-4bd7-b753-f26526d30ed9"
      },
      "success": "True"
  }
  ```

#### 3. Make Payment
- **URL**: `/api/make-payment/`
- **Method**: POST
- **Request Body**:
  ```json
  {
      "loan_id": "398ed9c2-287d-4bd7-b753-f26526d30ed9",
      "amount": 1000
  }
  ```
- **Description**:
  - Processes payments for EMIs.
  - Recalculates EMIs if the payment exceeds the due amount.
- **Response**:
  ```json
  {
      "message": "Payment processed successfully",
      "data": {
          "amount_paid": 1000,
          "remaining_due": 450.0
      },
      "success": "True"
  }
  ```

#### 4. Get Statement
- **URL**: `/api/get-statement/?loan_id=398ed9c2-287d-4bd7-b753-f26526d30ed9`
- **Method**: GET
- **Description**:
  - Fetches past transactions and upcoming EMIs for the given loan.
- **Response**:
  ```json
  {
      "message": "Success",
      "data": {
          "past_transactions": [
              {"amount_paid": 450.0, "installment_date": "2023-08-01"}
          ],
          "upcoming_transactions": [
              {"amount_due": 450.0, "installment_date": "2023-09-01"}
          ]
      },
      "success": "True"
  }
  ```

---

### EMI Calculations

The EMI is calculated using the formula:

```
EMI = P x [R x (1+R)^n] / [(1+R)^n - 1]
```
Where:
- **P** = Principal loan amount
- **R** = Monthly interest rate (annual interest rate / 12 / 100)
- **n** = Repayment tenure in months

---

### Cron Job for Billing

A daily cron job runs to:
- Identify users whose billing cycle ends that day.
- Calculate the minimum due using the formula:
  ```
  Min Due = (Principal Balance * 3%) + (Daily APR Accrued)
  ```
- Update the billing table with the due date (15 days from billing date).
- Ensure atomicity to avoid race conditions.

