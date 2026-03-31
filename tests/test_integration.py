from src.models import Apartment, Tenant, Bill
from src.manager import Manager
from src.models import Parameters


def test_load_data():
    parameters = Parameters()
    manager = Manager(parameters)
    assert isinstance(manager.apartments, dict)
    assert isinstance(manager.tenants, dict)
    assert isinstance(manager.transfers, list)
    assert isinstance(manager.bills, list)

    for apartment_key, apartment in manager.apartments.items():
        assert isinstance(apartment, Apartment)
        assert apartment.key == apartment_key

def test_tenants_in_manager():
    parameters = Parameters()
    manager = Manager(parameters)
    assert len(manager.tenants) > 0
    names = [tenant.name for tenant in manager.tenants.values()]
    for tenant in ['Jan Nowak', 'Adam Kowalski', 'Ewa Adamska']:
        assert tenant in names

def test_if_tenants_have_valid_apartment_keys():
    parameters = Parameters()
    manager = Manager(parameters)
    assert manager.check_tenants_apartment_keys() == True

    manager.tenants['tenant-1'].apartment = 'invalid-key'
    assert manager.check_tenants_apartment_keys() == False
    
def test_apartment_costs():
    manager = Manager(Parameters())
    assert manager.get_apartment_costs('apart-polanka', 2025, 1)==760.0+150.0
    assert manager.get_apartment_costs('apart-polanka', 2025, 2)==0.0
    assert manager.get_apartment_costs('uam', 2025, 1)==None

def test_apartment_settlement():
    manager = Manager(Parameters())

    apset=manager.apartment_settlement_from('apart-polanka', 2025, 1)

    assert apset.total_due_pln==apset.total_bills_pln+apset.total_rent_pln
    assert apset.total_bills_pln==760.0+150.0
    assert apset.total_rent_pln==1400.0+1500.0+1300.0
    assert apset.apartment=='apart-polanka'

    apset2=manager.apartment_settlement_from('apart-polanka', 2025, 2)

    assert apset2.total_bills_pln==0.0
    assert apset2.apartment==apset.apartment
    assert apset2.total_rent_pln==apset.total_rent_pln # they should be equal, since they are stil the same apartment
    assert apset2.total_due_pln==apset2.total_rent_pln
    assert apset2.year==2025

    assert manager.apartment_settlement_from("uam", 2025, 1)==None

def test_tenant_settlement():
    manager=Manager(Parameters())

    tensets=manager.tenant_settlements_of("apart-polanka", 2025, 1)

    assert len(tensets)==3
    for t in tensets:
        assert t.tenant in manager.tenants.keys()
        assert t.apartment_settlement=="apart-polanka"
        assert t.month==1
        assert t.rent_pln==manager.tenants[t.tenant].rent_pln
        assert t.bills_pln==\
            manager.apartment_settlement_from('apart-polanka', 2025, 1)\
            .total_bills_pln/3
        assert t.total_due_pln==t.rent_pln+t.bills_pln
        # I don't know what's the purpose of the .balance_pln member

    manager.apartments['apart-test']= Apartment(
        key="apart-test",
        name="Test Apartment",
        location="Test Location",
        area_m2=50.0,
        rooms={
            "room-1": {"name": "Living Room", "area_m2": 30.0},
            "room-2": {"name": "Bedroom", "area_m2": 20.0}
        }
    )

    manager.tenants['tenant-test']= Tenant(
        name='Test Tenant',
        apartment='apart-test',
        room='room-1',
        rent_pln=1500.0,
        deposit_pln=3000.0,
        date_agreement_from='2024-01-01',
        date_agreement_to='2024-12-31'
    )

    manager.bills.append(Bill(**{
        "amount_pln": 150.00,
        "date_due": "2025-02-12",
        "settlement_year": 2025,
        "settlement_month": 1,
        "apartment": "apart-test",
        "type": "electricity"
    }))

    tensets2=manager.tenant_settlements_of("apart-test", 2025, 1)

    assert len(tensets2)==1

    assert tensets2[0].bills_pln==\
        manager.apartment_settlement_from("apart-test", 2025, 1).total_bills_pln
    assert tensets2[0].rent_pln==1500.0
    assert tensets2[0].tenant in manager.tenants.keys()
    assert tensets2[0].total_due_pln==1500.0+150.0

    manager.apartments['apart-test2']= Apartment(
        key="apart-test",
        name="Test Apartment 2",
        location="Mountains",
        area_m2=50.0,
        rooms={
            "room": {"name": "Crying Room", "area_m2": 30.0}
        }
    )
    manager.bills.append(Bill(**{
        "amount_pln": 760.00,
        "date_due": "2025-02-15",
        "settlement_year": 2025,
        "settlement_month": 1,
        "apartment": "apart-test2",
        "type": "rent"
    }))

    assert len(manager.tenant_settlements_of("apart-test2", 2025, 1))==0
    assert manager.tenant_settlements_of("apart-test4", 2025, 1)==None
