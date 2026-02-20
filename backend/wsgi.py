# Alternative WSGI entry point for deployment platforms
# This file provides multiple ways to import the FastAPI app

import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Try importing from app.main (standard structure)
    from app.main import app
    application = app
except ImportError as e:
    print(f"Failed to import from app.main: {e}")
    try:
        # Try importing directly (alternative structure)
        import app.main
        application = app.main.app
    except ImportError as e2:
        print(f"Failed to import app.main: {e2}")
        # Last resort - create a minimal app
        from fastapi import FastAPI
        application = FastAPI(title="Postify Backend")
        
        @application.get("/")
        async def root():
            return {"message": "Postify Backend - Import Error", "error": str(e)}

# For direct execution
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(application, host="0.0.0.0", port=8000)
