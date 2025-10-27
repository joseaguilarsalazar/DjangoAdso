import os

def read_env_file(path):
    print("\n=== READING .env FILE RAW ===")
    with open(path, 'rb') as f:
        data = f.read()
    print("Total bytes:", len(data))
    print("Raw preview (first 300 bytes):", repr(data[:300]))
    print("Starts with BOM:", data.startswith(b'\xef\xbb\xbf'))
    print("\nFull decoded text:")
    try:
        text = data.decode('utf-8')
        print(text)
        return text
    except Exception as e:
        print("Decode error:", e)
        return None

def inspect_lines(text):
    print("\n=== CHECKING FOR BROKEN LINES ===")
    for i, line in enumerate(text.splitlines(), 1):
        status = "OK"
        if "=" not in line or line.strip().startswith("#") or not line.strip():
            status = "⚠ MISSING '=' or Possibly Truncated"
        print(f"{i:02}: {line}  --> {status}")

def show_env_values():
    print("\n=== CURRENT os.environ VALUES ===")
    important_keys = [k for k in os.environ.keys() if "DB" in k or "DJ" in k or "evo" in k]
    for key in sorted(important_keys):
        print(f"{key} = {os.environ[key]}")

path = os.path.join(os.getcwd(), '.env')
print("cwd:", os.getcwd())
print(".env exists:", os.path.exists(path))

if os.path.exists(path):
    text = read_env_file(path)
    if text:
        inspect_lines(text)
else:
    print("No .env found.")

show_env_values()

print("\n=== END ===")
