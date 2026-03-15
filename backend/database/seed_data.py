from datetime import datetime
from sqlalchemy.orm import Session
from database.models import Customer, Order, Payment, Chargeback


def run_seed(db: Session):
    if db.query(Customer).first():
        return

    # --- Customer: John Smith (the chargeback subject) ---
    john = Customer(
        name="John Smith",
        email="john.smith@email.com",
        phone="(555) 234-5678",
        address="742 Evergreen Terrace, Springfield, IL 62704",
        account_created_at=datetime(2024, 3, 10),
    )

    # --- Customer: Jane Doe (extra data for realism) ---
    jane = Customer(
        name="Jane Doe",
        email="jane.doe@email.com",
        phone="(555) 987-6543",
        address="123 Oak Street, Chicago, IL 60601",
        account_created_at=datetime(2024, 6, 22),
    )

    db.add_all([john, jane])
    db.flush()

    # --- Orders for John Smith ---
    order1 = Order(
        customer_id=john.customer_id,
        amount=1249.99,
        item_description='Samsung 65" QLED 4K Smart TV - Model QN65Q80C',
        order_date=datetime(2026, 2, 15),
        shipping_status="delivered",
        tracking_number="1Z999AA10123456784",
        delivery_date=datetime(2026, 2, 18),
    )
    order2 = Order(
        customer_id=john.customer_id,
        amount=89.99,
        item_description="Logitech MX Master 3S Wireless Mouse",
        order_date=datetime(2025, 11, 20),
        shipping_status="delivered",
        tracking_number="1Z999AA10123456700",
        delivery_date=datetime(2025, 11, 23),
    )
    order3 = Order(
        customer_id=john.customer_id,
        amount=349.99,
        item_description="Sony WH-1000XM5 Noise Canceling Headphones",
        order_date=datetime(2025, 8, 5),
        shipping_status="delivered",
        tracking_number="1Z999AA10123456701",
        delivery_date=datetime(2025, 8, 8),
    )

    # --- Orders for Jane Doe ---
    order4 = Order(
        customer_id=jane.customer_id,
        amount=599.99,
        item_description="Apple iPad Air M2 - 256GB",
        order_date=datetime(2026, 1, 10),
        shipping_status="delivered",
        tracking_number="1Z999AA10123456790",
        delivery_date=datetime(2026, 1, 13),
    )

    db.add_all([order1, order2, order3, order4])
    db.flush()

    # --- Payments for John Smith ---
    payments = [
        Payment(
            order_id=order1.order_id,
            customer_id=john.customer_id,
            card_last_four="4532",
            amount=1249.99,
            status="completed",
            payment_date=datetime(2026, 2, 15),
            bank_name="Chase",
        ),
        Payment(
            order_id=order2.order_id,
            customer_id=john.customer_id,
            card_last_four="4532",
            amount=89.99,
            status="completed",
            payment_date=datetime(2025, 11, 20),
            bank_name="Chase",
        ),
        Payment(
            order_id=order3.order_id,
            customer_id=john.customer_id,
            card_last_four="4532",
            amount=349.99,
            status="completed",
            payment_date=datetime(2025, 8, 5),
            bank_name="Chase",
        ),
        Payment(
            order_id=order4.order_id,
            customer_id=jane.customer_id,
            card_last_four="8821",
            amount=599.99,
            status="completed",
            payment_date=datetime(2026, 1, 10),
            bank_name="Bank of America",
        ),
    ]
    db.add_all(payments)

    # --- Customer: Michael Chen (lost shipment victim) ---
    michael = Customer(
        name="Michael Chen",
        email="m.chen@email.com",
        phone="(555) 444-7890",
        address="88 Pine Avenue, San Jose, CA 95112",
        account_created_at=datetime(2025, 9, 1),
    )

    # --- Customer: Sarah Williams (double-charged) ---
    sarah = Customer(
        name="Sarah Williams",
        email="sarah.w@email.com",
        phone="(555) 321-0987",
        address="450 Elm Boulevard, Austin, TX 78701",
        account_created_at=datetime(2025, 1, 15),
    )

    db.add_all([michael, sarah])
    db.flush()

    # --- Order for Michael Chen (lost in transit — no delivery confirmation) ---
    order5 = Order(
        customer_id=michael.customer_id,
        amount=799.99,
        item_description="Apple AirPods Max - Space Gray",
        order_date=datetime(2026, 1, 25),
        shipping_status="lost",
        tracking_number="1Z999AA10123456805",
        delivery_date=None,
    )

    # --- Orders for Sarah Williams (duplicate charge) ---
    order6 = Order(
        customer_id=sarah.customer_id,
        amount=429.99,
        item_description="Bose QuietComfort Ultra Earbuds",
        order_date=datetime(2026, 2, 5),
        shipping_status="delivered",
        tracking_number="1Z999AA10123456810",
        delivery_date=datetime(2026, 2, 8),
    )

    db.add_all([order5, order6])
    db.flush()

    payments += [
        Payment(
            order_id=order5.order_id,
            customer_id=michael.customer_id,
            card_last_four="7291",
            amount=799.99,
            status="completed",
            payment_date=datetime(2026, 1, 25),
            bank_name="Chase",
        ),
        Payment(
            order_id=order6.order_id,
            customer_id=sarah.customer_id,
            card_last_four="3156",
            amount=429.99,
            status="completed",
            payment_date=datetime(2026, 2, 5),
            bank_name="Bank of America",
        ),
        # Duplicate/erroneous charge for Sarah (same order, same amount, same day)
        Payment(
            order_id=order6.order_id,
            customer_id=sarah.customer_id,
            card_last_four="3156",
            amount=429.99,
            status="completed",
            payment_date=datetime(2026, 2, 5),
            bank_name="Bank of America",
        ),
    ]
    db.add_all(payments)

    # --- Pre-seeded chargeback #1: John Smith (DEFEND — strong evidence) ---
    chargeback1 = Chargeback(
        case_id="CB-2026-0314",
        bank_name="Chase",
        cardholder_name="John Smith",
        card_last_four="4532",
        transaction_amount=1249.99,
        transaction_date=datetime(2026, 2, 15),
        reason_code="10.4 - Other Fraud (Card Not Present)",
        cardholder_statement=(
            "I did not make this purchase. I do not recognize this "
            "transaction to Acme Electronics."
        ),
        status="new",
        created_at=datetime(2026, 3, 14),
    )

    # --- Pre-seeded chargeback #2: Michael Chen (ACCEPT — package lost, no delivery proof) ---
    chargeback2 = Chargeback(
        case_id="CB-2026-0220",
        bank_name="Chase",
        cardholder_name="Michael Chen",
        card_last_four="7291",
        transaction_amount=799.99,
        transaction_date=datetime(2026, 1, 25),
        reason_code="13.3 - Not as Described or Defective (Goods Not Received)",
        cardholder_statement=(
            "I ordered AirPods Max from Acme Electronics on January 25 but never "
            "received the package. Tracking shows it was lost in transit. I contacted "
            "the merchant but they refused to refund or reship."
        ),
        status="new",
        created_at=datetime(2026, 2, 20),
    )

    # --- Pre-seeded chargeback #3: Sarah Williams (ACCEPT — duplicate charge) ---
    chargeback3 = Chargeback(
        case_id="CB-2026-0301",
        bank_name="Bank of America",
        cardholder_name="Sarah Williams",
        card_last_four="3156",
        transaction_amount=429.99,
        transaction_date=datetime(2026, 2, 5),
        reason_code="12.1 - Processing Error (Late Presentment / Duplicate)",
        cardholder_statement=(
            "I was charged twice for the same purchase of Bose QuietComfort Ultra "
            "Earbuds on February 5th. I only made one order but my statement shows "
            "two charges of $429.99 from Acme Electronics."
        ),
        status="new",
        created_at=datetime(2026, 3, 1),
    )

    db.add_all([chargeback1, chargeback2, chargeback3])
    db.commit()
