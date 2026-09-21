import asyncio
from app.services.intent_classifier import classify_intent

async def main():
    result = classify_intent("What documents do I need for a new ration card in Kerala?")
    print("Intent output:")
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
