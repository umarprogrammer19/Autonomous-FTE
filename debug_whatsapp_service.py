from services.whatsapp_service import WhatsAppService

print("Testing WhatsAppService directly...")

result = WhatsAppService.send_message(
    "923182710120",
    "Test message from service layer"
)

print(f"WhatsAppService result: {result}")