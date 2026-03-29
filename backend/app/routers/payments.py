from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session as DBSession

from app.auth import get_current_user
from app.config import settings
from app.database import get_db
from app.models import Ticket, Payment, PaymentStatus, User
from app.schemas import CheckoutSessionResponse, PaymentResponse

router = APIRouter(prefix="/api/payments", tags=["Payments"])

# Stripe is optional - works in test mode without real keys
try:
    import stripe
    stripe.api_key = settings.STRIPE_SECRET_KEY
    HAS_STRIPE = True
except ImportError:
    HAS_STRIPE = False


@router.post("/checkout/{ticket_id}", response_model=CheckoutSessionResponse)
def create_checkout_session(
    ticket_id: int,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    payment = ticket.payment
    if not payment:
        raise HTTPException(status_code=400, detail="No payment record for this ticket")

    if payment.status == PaymentStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Payment already completed")

    if not HAS_STRIPE or settings.STRIPE_SECRET_KEY == "sk_test_placeholder":
        # Mock mode for demo - auto-complete payment
        payment.status = PaymentStatus.COMPLETED
        payment.stripe_payment_id = f"mock_pi_{ticket_id}"
        db.commit()
        return CheckoutSessionResponse(
            checkout_url=f"{settings.FRONTEND_URL}/payment/success?ticket_id={ticket_id}",
            session_id=f"mock_cs_{ticket_id}",
        )

    # Real Stripe checkout
    checkout_session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{
            "price_data": {
                "currency": payment.currency,
                "product_data": {"name": f"Ticket #{ticket_id}"},
                "unit_amount": int(payment.amount * 100),
            },
            "quantity": 1,
        }],
        mode="payment",
        success_url=f"{settings.FRONTEND_URL}/payment/success?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{settings.FRONTEND_URL}/payment/cancel",
        metadata={"ticket_id": str(ticket_id), "payment_id": str(payment.id)},
    )

    payment.stripe_checkout_session_id = checkout_session.id
    db.commit()

    return CheckoutSessionResponse(
        checkout_url=checkout_session.url,
        session_id=checkout_session.id,
    )


@router.post("/webhook")
async def stripe_webhook(request: Request, db: DBSession = Depends(get_db)):
    if not HAS_STRIPE:
        raise HTTPException(status_code=501, detail="Stripe not configured")

    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        raise HTTPException(status_code=400, detail="Invalid webhook signature")

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        payment_id = session["metadata"].get("payment_id")
        if payment_id:
            payment = db.query(Payment).filter(Payment.id == int(payment_id)).first()
            if payment:
                payment.status = PaymentStatus.COMPLETED
                payment.stripe_payment_id = session.get("payment_intent")
                db.commit()

    elif event["type"] == "charge.refunded":
        charge = event["data"]["object"]
        payment_intent = charge.get("payment_intent")
        if payment_intent:
            payment = db.query(Payment).filter(
                Payment.stripe_payment_id == payment_intent
            ).first()
            if payment:
                payment.status = PaymentStatus.REFUNDED
                db.commit()

    return {"status": "ok"}


@router.post("/refund/{ticket_id}", response_model=PaymentResponse)
def refund_ticket(
    ticket_id: int,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    payment = ticket.payment
    if not payment or payment.status != PaymentStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="No completed payment to refund")

    if HAS_STRIPE and payment.stripe_payment_id and not payment.stripe_payment_id.startswith("mock_"):
        stripe.Refund.create(payment_intent=payment.stripe_payment_id)

    payment.status = PaymentStatus.REFUNDED
    db.commit()
    db.refresh(payment)
    return payment
