# scripts/test_email.py
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.email import send_invitation_email

result = send_invitation_email("vedantgonbare18@gmail.com", "test-token-123")
print(result)
