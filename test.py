import os
from dotenv import load_dotenv

load_dotenv()

print("Environment Variables:")
for key, value in os.environ.items():
    print(f"{key}: {value}")