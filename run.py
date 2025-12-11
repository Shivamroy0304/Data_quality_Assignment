"""
Entry point for running the workflow engine API.

Run with:
    python -m uvicorn app.main:app --reload
"""

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
