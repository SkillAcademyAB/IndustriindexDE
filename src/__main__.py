from fastapi import FastAPI
from src.controllers.diagnostics import router as test_router

app = FastAPI(
    title="IndustriindexDE API",
    description="A REST API for IndustriindexDE",
    version="0.1.0",
)

# Include routers
app.add_api_route("/", lambda: {"message": "Welcome to IndustriindexDE API"})
app.include_router(test_router, tags=["diagnostics"])


def main():
    """
    Main entry point for the application.
    """
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
