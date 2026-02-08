from services.email_service import EmailService

print("Testing EmailService directly...")

result = EmailService.send_email(
    "test@example.com",
    "Test Subject from Service Layer",
    "Test Message from Service Layer"
)

print(f"EmailService result: {result}")