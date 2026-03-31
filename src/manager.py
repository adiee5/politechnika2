from src.models import Apartment, Bill, Parameters, Tenant, Transfer, ApartmentSettlement, TenantSettlement


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

    def tenant_settlements_of(self, apartment_key, year, month):
        a=self.apartment_settlement_from(apartment_key, year, month)
        if a==None:
            return None # The apartment doesn't exist
        
        tenant_count=0
        for t in self.tenants.values():
            if t.apartment==apartment_key:
                tenant_count+=1
        
        l=[]
        for tid, t in self.tenants.items():
            if t.apartment==apartment_key:
                l.append(TenantSettlement(
                    apartment_settlement=apartment_key,
                    tenant=tid,
                    month=month,
                    year=year,
                    rent_pln=t.rent_pln,
                    bills_pln=a.total_bills_pln/tenant_count,
                    total_due_pln=t.rent_pln+a.total_bills_pln/tenant_count,
                    balance_pln=0
                ))
        return l
