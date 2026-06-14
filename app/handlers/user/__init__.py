from aiogram import Router

from . import start, catalog, info, order


def get_user_router() -> Router:
    router = Router(name="user")
    router.include_router(start.router)
    router.include_router(catalog.router)
    router.include_router(order.router)
    router.include_router(info.router)
    return router
