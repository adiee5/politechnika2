from src.models import Apartment, Bill, Parameters, Tenant, Transfer, ApartmentSettlement


class Manager:
    def __init__(self, parameters: Parameters):
        self.parameters = parameters 

        self.apartments = {}
        self.tenants = {}
        self.transfers = []
        self.bills = []
       
        self.load_data()

    def load_data(self):
        self.apartments = Apartment.from_json_file(self.parameters.apartments_json_path)
        self.tenants = Tenant.from_json_file(self.parameters.tenants_json_path)
        self.transfers = Transfer.from_json_file(self.parameters.transfers_json_path)
        self.bills = Bill.from_json_file(self.parameters.bills_json_path)

    def check_tenants_apartment_keys(self) -> bool:
        for tenant in self.tenants.values():
            if tenant.apartment not in self.apartments:
                return False
        return True
    
    def get_apartment_costs(self, apartment_key, year:int =None, month:int =None):
        if apartment_key not in self.apartments.keys():
            return None
        s=0.0
        for bill in self.bills:
            if bill.apartment==apartment_key \
                and (year==None or bill.settlement_year==year) \
                and (month==None or bill.settlement_month==month):
                    s+=bill.amount_pln
        return s

    def apartment_settlement_from(self, apartment_key, year, month):
        bills=self.get_apartment_costs(apartment_key, year, month)
        if bills==None:
            return None # The apartment doesn't exist
        rent=0
        for tenant in self.tenants.values():
            if tenant.apartment==apartment_key:
                rent+=tenant.rent_pln
        return ApartmentSettlement(
            apartment=apartment_key,
            year=year,
            month=month,
            total_bills_pln=bills,
            total_rent_pln=rent,
            total_due_pln=bills+rent
            )