from aiogram import Router

from . import panel, products, orders, stats, broadcast


def get_admin_router() -> Router:
    router = Router(name="admin")
    router.include_router(panel.router)
    router.include_router(products.router)
    router.include_router(orders.router)
    router.include_router(stats.router)
    router.include_router(broadcast.router)
    return router
