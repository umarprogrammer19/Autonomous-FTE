from services.ai_post_service import AIPostService

print("Testing AIPostService directly...")

result = AIPostService.generate_and_post_now()

print(f"AIPostService result: {result}")