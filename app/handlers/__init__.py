from aiogram import Router

from .admin import get_admin_router
from .user import get_user_router


def setup_routers() -> Router:
    """Barcha routerlarni bog'lash. Admin router birinchi bo'lishi kerak,
    chunki admin filterlar admin foydalanuvchilar uchun ustunlikka ega."""
    root_router = Router(name="root")
    root_router.include_router(get_admin_router())
    root_router.include_router(get_user_router())
    return root_router
