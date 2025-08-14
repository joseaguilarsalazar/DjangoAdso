import os

path = os.path.join(os.getcwd(), '.env')
print("cwd:", os.getcwd())
print(".env exists:", os.path.exists(path))

if os.path.exists(path):
    with open(path, 'rb') as f:
        data = f.read()
    print("bytes length:", len(data))
    # muestra los primeros 200 bytes en repr para ver encoding/BOM
    print(repr(data[:200]))
    # muestra si comienza con BOM
    print("starts with UTF-8 BOM:", data.startswith(b'\xef\xbb\xbf'))
else:
    print(".env not found at", path)
