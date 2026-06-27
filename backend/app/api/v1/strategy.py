from fastapi import APIRouter

router = APIRouter(prefix='/strategy', tags=['strategy'])

@router.get('/')
def get_strategies():
    return {'message': 'strategies endpoint'}
