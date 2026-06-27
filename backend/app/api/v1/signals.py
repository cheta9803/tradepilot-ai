from fastapi import APIRouter

router = APIRouter(prefix='/signals', tags=['signals'])

@router.get('/')
def get_signals():
    return {'message': 'signals endpoint'}
