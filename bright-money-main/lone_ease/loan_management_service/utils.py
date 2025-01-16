from loan_management_service.constants import (LOAN_BOUNDS,
                                               SUPPORTED_LOAN_TYPES,
                                               USER_INCOME_FOR_LOAN)

class LoanCalculations:
    def __init__(self):
        pass

    def calculate_interest(self, principle_amount, interest_rate, tenure):
        interest = (principle_amount * interest_rate * tenure) / 100
        return interest

    def calculate_emi(self, principal_amount, monthly_rate, tenure):
        emi = (principal_amount * monthly_rate * (1 + monthly_rate) ** tenure) / (
            (1 + monthly_rate) ** tenure - 1
        )
        return int(emi)

    def calculate_compound_interest(self, principal, interest, tenure):
        
        interest = (principal*((1+(interest/12)))**(tenure)) - principal
        return int(interest)