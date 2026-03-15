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

    # --- Pre-seeded chargeback from Chase ---
    chargeback = Chargeback(
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
    db.add(chargeback)
    db.commit()
