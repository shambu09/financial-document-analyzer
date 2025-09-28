from app.main import app  # re-export app for uvicorn entrypoint

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080, reload=True)