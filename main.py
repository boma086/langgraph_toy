"""Main entry point for the LangGraph toy implementation."""

import uvicorn
from api.app import create_app

def main():
    """Start the web server."""
    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()