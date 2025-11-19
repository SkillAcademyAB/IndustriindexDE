from fastapi import APIRouter

router = APIRouter()


@router.get("/healthcheck")
async def test_endpoint():
    """
    Simple healthcheck endpoint that returns a string message.
    Use for healthchecks on server from other systems.

    Args: No args
    Returns: Static message: "message": "IndustriIndex Server online!"
    Raises: No errors
    """
    return {"message": "IndustriIndex Server online!"}
