"""Matching API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.services.matching_service import MatchingService
from app.exceptions.matching import (
    MatchingException,
    InsufficientStudentsException,
    NoUnmatchedStudentsException
)
from app.schemas.matching import (
    MatchingExecuteRequest,
    MatchingExecuteResponse,
    MatchingStatusResponse,
    MatchingResultsResponse,
    ResetMatchingResponse,
    MatchingStatisticsDetailResponse
)


router = APIRouter(prefix="/matching", tags=["matching"])


@router.post(
    "/execute",
    response_model=MatchingExecuteResponse,
    status_code=status.HTTP_200_OK,
    summary="Execute roommate matching algorithm",
    description="""
Execute the complete roommate matching pipeline:
1. Hard filter by gender and smoking status
2. Draft clustering within each group
3. Calculate individual satisfaction scores
4. Blossom algorithm for optimal pairing
5. Assign sequential room IDs

Set dry_run=true to preview results without saving to database.
    """
)
async def execute_matching(
    request: MatchingExecuteRequest,
    db: AsyncSession = Depends(get_db)
):
    """Execute matching algorithm."""
    try:
        service = MatchingService(db)
        result = await service.execute_matching(dry_run=request.dry_run)

        return MatchingExecuteResponse(**result)

    except InsufficientStudentsException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except NoUnmatchedStudentsException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except MatchingException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Matching error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error during matching: {str(e)}"
        )


@router.get(
    "/status",
    response_model=MatchingStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current matching status",
    description="Get statistics about currently matched and unmatched students."
)
async def get_matching_status(db: AsyncSession = Depends(get_db)):
    """Get matching status."""
    try:
        service = MatchingService(db)
        result = await service.get_matching_status()

        return MatchingStatusResponse(**result)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving matching status: {str(e)}"
        )


@router.get(
    "/results",
    response_model=MatchingResultsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get matching results",
    description="Get paginated list of room assignments with satisfaction scores."
)
async def get_matching_results(
    skip: int = Query(0, ge=0, description="Number of rooms to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of rooms to return"),
    db: AsyncSession = Depends(get_db)
):
    """Get paginated matching results."""
    try:
        service = MatchingService(db)
        result = await service.get_matching_results(skip=skip, limit=limit)

        return MatchingResultsResponse(**result)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving matching results: {str(e)}"
        )


@router.delete(
    "/reset",
    response_model=ResetMatchingResponse,
    status_code=status.HTTP_200_OK,
    summary="Reset all matching data",
    description="Reset all students to unmatched state (clears room assignments and satisfaction scores)."
)
async def reset_matching(db: AsyncSession = Depends(get_db)):
    """Reset all matching data."""
    try:
        service = MatchingService(db)
        result = await service.reset_matching()

        return ResetMatchingResponse(**result)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error resetting matching: {str(e)}"
        )


@router.get(
    "/preview",
    response_model=MatchingExecuteResponse,
    status_code=status.HTTP_200_OK,
    summary="Preview matching results",
    description="Execute matching algorithm without saving to database (equivalent to execute with dry_run=true)."
)
async def preview_matching(db: AsyncSession = Depends(get_db)):
    """Preview matching results without saving."""
    try:
        service = MatchingService(db)
        result = await service.execute_matching(dry_run=True)

        return MatchingExecuteResponse(**result)

    except InsufficientStudentsException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except NoUnmatchedStudentsException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except MatchingException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Matching error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error during matching preview: {str(e)}"
        )


@router.get(
    "/statistics",
    response_model=MatchingStatisticsDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Get detailed matching statistics",
    description="""
Get comprehensive statistics about current matching results including:
- Individual satisfaction scores (average, median, min, max, standard deviation)
- Room-level satisfaction statistics
- Distribution of satisfaction scores by range (0-20, 20-40, 40-60, 60-80, 80-100)
    """
)
async def get_matching_statistics(db: AsyncSession = Depends(get_db)):
    """Get detailed matching statistics."""
    try:
        service = MatchingService(db)
        result = await service.get_detailed_statistics()

        return MatchingStatisticsDetailResponse(**result)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving matching statistics: {str(e)}"
        )