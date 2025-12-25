import sys
import os

# Adiciona a pasta root e a pasta backend ao path para encontrar os módulos
base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_path)
sys.path.append(os.path.join(base_path, 'backend'))

from app.main import app

# Vercel handler
handler = app

# Debug: print routes on startup
print("=== ROUTES REGISTERED ===")
for route in app.routes:
    if hasattr(route, 'path'):
        print(f"  {route.methods if hasattr(route, 'methods') else 'N/A'} {route.path}")
print("=" * 50)