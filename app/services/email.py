# app/services/email.py
import resend
from app.core.config import settings

resend.api_key = settings.RESEND_API_KEY


def send_invitation_email(to_email: str, token: str) -> dict:
    """
    Send an invitation email to a prospective student.
    """
    signup_link = f"{settings.FRONTEND_BASE_URL}/register?invite={token}"

    response = resend.Emails.send(
        {
            "from": "ResearchPulse <onboarding@resend.dev>",
            "to": [to_email],
            "subject": "You've been invited to ResearchPulse",
            "html": f"""
            <p>Hi,</p>
            <p>Your professor has invited you to join their research workspace on ResearchPulse.</p>
            <p><a href="{signup_link}">Click here to create your account</a></p>
            <p>If you weren't expecting this invitation, you can safely ignore this email.</p>
        """,
        }
    )
    return response
