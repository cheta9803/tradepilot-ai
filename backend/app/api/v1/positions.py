from fastapi import APIRouter

router = APIRouter(prefix='/positions', tags=['positions'])

@router.get('/')
def list_positions():
    return {'message': 'positions endpoint'}
