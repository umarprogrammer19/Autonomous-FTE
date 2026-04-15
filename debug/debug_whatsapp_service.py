from src.services.whatsapp_service import WhatsAppService

print("Testing WhatsAppService directly...")

result = WhatsAppService.send_message(
    "923075799968",
    "Test message from service layer"
)

print(f"WhatsAppService result: {result}")