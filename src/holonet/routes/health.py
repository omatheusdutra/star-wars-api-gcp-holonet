from fastapi import APIRouter, Depends

from holonet.deps import correlation_id_dependency

router = APIRouter(tags=["health"])


@router.get("/health")
def health(correlation_id: str = Depends(correlation_id_dependency)):
    return {
        "status": "ok",
        "source": {"name": "holonet", "url": "internal"},
        "cache": {"hit": False, "ttl": 0},
        "correlation_id": correlation_id,
    }


@router.get("/v1/health")
def health_v1(correlation_id: str = Depends(correlation_id_dependency)):
    return {
        "status": "ok",
        "source": {"name": "holonet", "url": "internal"},
        "cache": {"hit": False, "ttl": 0},
        "correlation_id": correlation_id,
    }


@router.get("/v1/meta")
def meta(correlation_id: str = Depends(correlation_id_dependency)):
    return {
        "name": "Holonet Galactic Console",
        "version": "v1",
        "status": "ok",
        "source": {"name": "holonet", "url": "internal"},
        "cache": {"hit": False, "ttl": 0},
        "correlation_id": correlation_id,
    }
