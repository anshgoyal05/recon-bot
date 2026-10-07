from sqlmodel import Session, select
from app.models.database import engine, init_db
from app.models.master import HsnRate, Supplier, SystemSettings

def seed_database():
    init_db()
    with Session(engine) as session:
        # 1. System Settings
        existing_settings = session.exec(select(SystemSettings).where(SystemSettings.id == "default")).first()
        if not existing_settings:
            settings_obj = SystemSettings(
                id="default",
                company_name="Precision Auto Components Pvt Ltd",
                company_gstin="27AAACP1234M1ZG",
                company_state_code="27",
                company_state="Maharashtra",
                qty_tolerance_pct=2.0,
                price_tolerance_inr=0.01,
                price_tolerance_pct=0.5,
                tax_roundoff_tolerance_inr=1.0,
            )
            session.add(settings_obj)
        else:
            existing_settings.company_gstin = "27AAACP1234M1ZG"
            session.add(existing_settings)

        # 2. Versioned HSN Master
        # India's GST slabs changed in 2025 for specific auto parts and metal items
        hsn_definitions = [
            # Fasteners: Screws, bolts, nuts
            {"hsn_code": "7318", "desc": "Screws, bolts, nuts, washers of iron/steel", "rate": 18.0, "from": "2017-07-01", "to": None, "cat": "Fasteners"},
            # Auto components: parts of motor vehicles (rationalized in 2025)
            {"hsn_code": "8708", "desc": "Parts and accessories of motor vehicles", "rate": 28.0, "from": "2017-07-01", "to": "2024-12-31", "cat": "Auto Parts"},
            {"hsn_code": "8708", "desc": "Parts and accessories of motor vehicles (2025 rationalized)", "rate": 18.0, "from": "2025-01-01", "to": None, "cat": "Auto Parts"},
            # Fabricated articles of iron or steel
            {"hsn_code": "7326", "desc": "Articles of iron or steel (fabricated / stamped)", "rate": 18.0, "from": "2017-07-01", "to": None, "cat": "Fabrication"},
            # Cast iron articles
            {"hsn_code": "7325", "desc": "Cast articles of iron or steel", "rate": 18.0, "from": "2017-07-01", "to": None, "cat": "Castings"},
            # Bearings and transmission shafts
            {"hsn_code": "8483", "desc": "Transmission shafts, cranks, bearing housings", "rate": 18.0, "from": "2017-07-01", "to": None, "cat": "Transmission"},
            # Valves and cocks
            {"hsn_code": "8481", "desc": "Taps, cocks, valves for pipes or tanks", "rate": 18.0, "from": "2017-07-01", "to": None, "cat": "Valves"},
            # Rubber seals / gaskets
            {"hsn_code": "4016", "desc": "Articles of vulcanised rubber (gaskets, seals)", "rate": 18.0, "from": "2017-07-01", "to": None, "cat": "Rubber Goods"},
            # Job work manufacturing services
            {"hsn_code": "9988", "desc": "Manufacturing services on physical inputs (job work)", "rate": 12.0, "from": "2017-07-01", "to": None, "cat": "Job Work"},
            # Ferrous scrap
            {"hsn_code": "7204", "desc": "Ferrous waste and scrap; remelting scrap ingots", "rate": 18.0, "from": "2017-07-01", "to": None, "cat": "Raw Materials"},
            # Nil rated / agricultural inputs
            {"hsn_code": "0101", "desc": "Live animals and nil rated agricultural inputs", "rate": 0.0, "from": "2017-07-01", "to": None, "cat": "Exempt"},
        ]

        for h in hsn_definitions:
            existing_hsn = session.exec(
                select(HsnRate).where(
                    HsnRate.hsn_code == h["hsn_code"],
                    HsnRate.effective_from == h["from"]
                )
            ).first()
            if not existing_hsn:
                session.add(
                    HsnRate(
                        hsn_code=h["hsn_code"],
                        description=h["desc"],
                        rate_percent=h["rate"],
                        effective_from=h["from"],
                        effective_to=h["to"],
                        category=h["cat"],
                    )
                )

        # 3. Supplier Master
        suppliers_data = [
            {
                "name": "Tata AutoComp Systems Ltd",
                "gstin": "27AAACT1234F1ZR",
                "state_code": "27",
                "state_name": "Maharashtra",
                "email": "ap.vendor@tataautocomp.example.com",
                "phone": "+91 20 6608 5000",
            },
            {
                "name": "Bharat Forge Ltd",
                "gstin": "27AAACB1234A1ZJ",
                "state_code": "27",
                "state_name": "Maharashtra",
                "email": "billing@bharatforge.example.com",
                "phone": "+91 20 6704 2777",
            },
            {
                "name": "Sundram Fasteners Ltd",
                "gstin": "33AAACS1234D1Z3",
                "state_code": "33",
                "state_name": "Tamil Nadu",
                "email": "accounts@sundramfasteners.example.com",
                "phone": "+91 44 2852 1870",
            },
            {
                "name": "JBM Auto Ltd",
                "gstin": "06AAACJ1234G1Z3",
                "state_code": "06",
                "state_name": "Haryana",
                "email": "invoices@jbmgroup.example.com",
                "phone": "+91 129 409 0200",
            },
            {
                "name": "Motherson Automotive Technologies",
                "gstin": "27AAACM1234E1Z0",
                "state_code": "27",
                "state_name": "Maharashtra",
                "email": "supplychain@motherson.example.com",
                "phone": "+91 120 675 2100",
            },
        ]

        for s in suppliers_data:
            existing_sup = session.exec(select(Supplier).where(Supplier.gstin == s["gstin"])).first()
            if not existing_sup:
                session.add(
                    Supplier(
                        name=s["name"],
                        gstin=s["gstin"],
                        state_code=s["state_code"],
                        state_name=s["state_name"],
                        email=s["email"],
                        phone=s["phone"],
                    )
                )

        session.commit()
    print("Database initialized and seeded successfully.")

if __name__ == "__main__":
    seed_database()
