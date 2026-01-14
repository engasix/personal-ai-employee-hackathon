import os
import subprocess
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# print("Environment Variables:")
# for key, value in os.environ.items():
#     print(f"{key}: {value}")


VAULT_PATH = Path(os.getenv('VAULT_PATH', './vault'))

cmd = [
        'ls',
        '-ltrah'
    ]

# Execute Claude Code
process = subprocess.Popen(
    cmd,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    cwd=str(VAULT_PATH)
)

stdout, stderr = process.communicate(timeout=300)

print(f"STDOUT: {stdout}")
