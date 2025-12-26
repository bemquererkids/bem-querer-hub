import sys
sys.path.insert(0, '.')

from app.main import app

print("\n=== ROTAS REGISTRADAS ===\n")
for route in app.routes:
    if hasattr(route, 'path'):
        methods = getattr(route, 'methods', set())
        print(f"{methods} {route.path}")
print("\n" + "="*50)
