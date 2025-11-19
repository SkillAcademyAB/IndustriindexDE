from fastapi import APIRouter

router = APIRouter()


@router.get("/healthcheck")
async def healthcheck_endpoint():
    """
    Simple healthcheck endpoint that returns a string message.
    Use for healthchecks on server from other systems.

    Returns:
        dict: A dictionary containing a message indicating the server is online.
    """
    return {"message": "IndustriIndex Server online!"}
