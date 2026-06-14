from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.filters import IsAdmin
from app.services.product_service import ProductService
from app.states import AdminProductStates, AdminCategoryStates
from app.keyboards.admin import (
    admin_products_menu_kb,
    admin_categories_kb,
    admin_categories_select_kb,
    admin_products_list_kb,
    admin_product_actions_kb,
    confirm_delete_kb,
    skip_kb,
    cancel_kb,
    photos_done_kb,
    confirm_product_kb,
    admin_panel_kb,
)
from app.utils.helpers import format_price

router = Router(name="admin_products")
router.message.filter(IsAdmin())

SKIP_TEXT = "➡️ O'tkazib yuborish"
CANCEL_TEXT = "❌ Bekor qilish"
DONE_PHOTOS_TEXT = "✅ Rasmlar tugadi"
SAVE_TEXT = "✅ Saqlash"

FIELD_NAMES = {
    "name": "Nomi",
    "description": "Tavsif",
    "price": "Narx",
    "size": "O'lcham",
    "capacity": "Sig'im",
    "delivery_info": "Yetkazib berish ma'lumoti",
}


# ============================================================
# ASOSIY MENYU
# ============================================================

@router.message(F.text == "📦 Mahsulotlar")
async def products_menu(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        "📦 <b>Mahsulotlar boshqaruvi</b>\n\nKerakli amalni tanlang 👇",
        reply_markup=admin_products_menu_kb(),
    )


@router.callback_query(IsAdmin(), F.data == "ap:menu")
async def back_to_products_menu(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    try:
        await callback.message.edit_text(
            "📦 <b>Mahsulotlar boshqaruvi</b>\n\nKerakli amalni tanlang 👇",
            reply_markup=admin_products_menu_kb(),
        )
    except Exception:
        await callback.message.answer(
            "📦 <b>Mahsulotlar boshqaruvi</b>\n\nKerakli amalni tanlang 👇",
            reply_markup=admin_products_menu_kb(),
        )
    await callback.answer()


@router.callback_query(IsAdmin(), F.data == "ap:categories")
async def show_categories_manage(callback: CallbackQuery, session: AsyncSession) -> None:
    service = ProductService(session)
    categories = await service.get_all_categories()

    try:
        await callback.message.edit_text(
            "📂 <b>Kategoriyalar</b>\n\n"
            "Kategoriyani tanlang yoki yangisini qo'shing:",
            reply_markup=admin_categories_kb(categories, show_add=True),
        )
    except Exception:
        await callback.message.answer(
            "📂 <b>Kategoriyalar</b>\n\n"
            "Kategoriyani tanlang yoki yangisini qo'shing:",
            reply_markup=admin_categories_kb(categories, show_add=True),
        )
    await callback.answer()


@router.callback_query(IsAdmin(), F.data == "ap:list")
async def show_categories_for_products(callback: CallbackQuery, session: AsyncSession) -> None:
    service = ProductService(session)
    categories = await service.get_all_categories()

    try:
        await callback.message.edit_text(
            "📂 Mahsulotni tahrirlash/o'chirish uchun kategoriyani tanlang:",
            reply_markup=admin_categories_kb(categories, show_add=False),
        )
    except Exception:
        await callback.message.answer(
            "📂 Mahsulotni tahrirlash/o'chirish uchun kategoriyani tanlang:",
            reply_markup=admin_categories_kb(categories, show_add=False),
        )
    await callback.answer()


# ============================================================
# KATEGORIYA QO'SHISH
# ============================================================

@router.callback_query(IsAdmin(), F.data == "apcat:add")
async def add_category_start(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(AdminCategoryStates.waiting_name)
    await callback.message.answer(
        "📂 Yangi kategoriya nomini kiriting (masalan: <i>Maxsus tandirlar</i>):",
        reply_markup=cancel_kb(),
    )
    await callback.answer()


@router.message(AdminCategoryStates.waiting_name, F.text == CANCEL_TEXT)
@router.message(AdminCategoryStates.waiting_emoji, F.text == CANCEL_TEXT)
async def cancel_category(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("❌ Bekor qilindi.", reply_markup=admin_panel_kb())


@router.message(AdminCategoryStates.waiting_name)
async def category_name_entered(message: Message, state: FSMContext) -> None:
    await state.update_data(cat_name=message.text.strip())
    await state.set_state(AdminCategoryStates.waiting_emoji)
    await message.answer(
        "🔥 Kategoriya uchun emoji yuboring (masalan: 🍞):",
        reply_markup=cancel_kb(),
    )


@router.message(AdminCategoryStates.waiting_emoji)
async def category_emoji_entered(message: Message, state: FSMContext, session: AsyncSession) -> None:
    data = await state.get_data()
    name = data.get("cat_name")
    emoji = message.text.strip()

    service = ProductService(session)
    category = await service.add_category(name=name, emoji=emoji, slug=f"cat_temp")
    # Slugni id asosida yangilash
    await service.category_repo.update(category.id, slug=f"cat_{category.id}")

    await state.clear()

    categories = await service.get_all_categories()
    await message.answer(
        f"✅ Kategoriya qo'shildi: {emoji} {name}",
        reply_markup=admin_panel_kb(),
    )
    await message.answer(
        "📂 <b>Kategoriyalar</b>\n\nKategoriyani tanlang yoki yangisini qo'shing:",
        reply_markup=admin_categories_kb(categories, show_add=True),
    )


# ============================================================
# KATEGORIYADAGI MAHSULOTLAR RO'YXATI
# ============================================================

@router.callback_query(IsAdmin(), F.data.startswith("apcat:"))
async def show_category_products(callback: CallbackQuery, session: AsyncSession) -> None:
    category_id = int(callback.data.split(":", 1)[1])
    service = ProductService(session)
    category = await service.get_category(category_id)

    if not category:
        await callback.answer("😔 Kategoriya topilmadi", show_alert=True)
        return

    all_products = await service.get_all_for_admin()
    products = [p for p in all_products if p.category_id == category_id]

    if not products:
        text = (
            f"{category.emoji or '🔥'} <b>{category.name}</b>\n\n"
            "📭 Bu kategoriyada hozircha mahsulotlar yo'q.\n\n"
            "Yangi mahsulot qo'shish uchun \"➕ Mahsulot qo'shish\" tugmasidan foydalaning."
        )
    else:
        text = (
            f"{category.emoji or '🔥'} <b>{category.name}</b>\n\n"
            "Mahsulotni tanlang 👇\n\n"
            "✅ - faol, 🚫 - nofaol"
        )

    try:
        await callback.message.edit_text(text, reply_markup=admin_products_list_kb(products, category_id))
    except Exception:
        await callback.message.answer(text, reply_markup=admin_products_list_kb(products, category_id))
    await callback.answer()


# ============================================================
# MAHSULOT TAFSILOTLARI VA AMALLAR
# ============================================================

def build_admin_product_text(product) -> str:
    photos_count = len(product.get_photos())
    video_status = "✅ bor" if product.video_id else "❌ yo'q"
    return (
        f"🔥 <b>{product.name}</b>\n\n"
        f"📝 Tavsif: {product.description or '—'}\n"
        f"💰 Narx: {format_price(product.price)}\n"
        f"📏 O'lcham: {product.size or '—'}\n"
        f"📦 Sig'im: {product.capacity or '—'}\n"
        f"🚚 Yetkazib berish: {product.delivery_info or '—'}\n"
        f"📷 Rasmlar: {photos_count} ta\n"
        f"🎥 Video: {video_status}\n"
        f"📂 Kategoriya: {product.category.name if product.category else '—'}\n"
        f"🔘 Holat: {'✅ Faol' if product.is_active else '🚫 Nofaol'}\n\n"
        "Quyidagi amallardan birini tanlang 👇"
    )


@router.callback_query(IsAdmin(), F.data.startswith("approd:"))
async def show_product_admin_detail(callback: CallbackQuery, session: AsyncSession) -> None:
    product_id = int(callback.data.split(":", 1)[1])
    service = ProductService(session)
    product = await service.get_product(product_id)

    if not product:
        await callback.answer("😔 Mahsulot topilmadi", show_alert=True)
        return

    text = build_admin_product_text(product)

    try:
        await callback.message.edit_text(
            text,
            reply_markup=admin_product_actions_kb(product.id, product.category_id),
        )
    except Exception:
        await callback.message.answer(
            text,
            reply_markup=admin_product_actions_kb(product.id, product.category_id),
        )
    await callback.answer()


@router.callback_query(IsAdmin(), F.data.startswith("aptoggle:"))
async def toggle_product_active(callback: CallbackQuery, session: AsyncSession) -> None:
    product_id = int(callback.data.split(":", 1)[1])
    service = ProductService(session)
    product = await service.get_product(product_id)

    if not product:
        await callback.answer("😔 Mahsulot topilmadi", show_alert=True)
        return

    await service.update_product(product_id, is_active=not product.is_active)
    await callback.answer("✅ Holat o'zgartirildi")

    product = await service.get_product(product_id)
    text = build_admin_product_text(product)
    try:
        await callback.message.edit_text(
            text,
            reply_markup=admin_product_actions_kb(product.id, product.category_id),
        )
    except Exception:
        pass


# ============================================================
# MAHSULOTNI O'CHIRISH
# ============================================================

@router.callback_query(IsAdmin(), F.data.startswith("apdel:"))
async def delete_product_confirm(callback: CallbackQuery) -> None:
    product_id = int(callback.data.split(":", 1)[1])
    try:
        await callback.message.edit_text(
            "❗️ Haqiqatan ham bu mahsulotni o'chirmoqchimisiz?\n\n"
            "Bu amalni qaytarib bo'lmaydi.",
            reply_markup=confirm_delete_kb(product_id),
        )
    except Exception:
        await callback.message.answer(
            "❗️ Haqiqatan ham bu mahsulotni o'chirmoqchimisiz?",
            reply_markup=confirm_delete_kb(product_id),
        )
    await callback.answer()


@router.callback_query(IsAdmin(), F.data.startswith("apdelconfirm:"))
async def delete_product_final(callback: CallbackQuery, session: AsyncSession) -> None:
    product_id = int(callback.data.split(":", 1)[1])
    service = ProductService(session)
    product = await service.get_product(product_id)
    category_id = product.category_id if product else None

    await service.delete_product(product_id)
    await callback.answer("✅ Mahsulot o'chirildi")

    all_products = await service.get_all_for_admin()
    products = [p for p in all_products if p.category_id == category_id] if category_id else []

    try:
        await callback.message.edit_text(
            "✅ Mahsulot o'chirildi.\n\nQolgan mahsulotlar 👇",
            reply_markup=admin_products_list_kb(products, category_id or 0),
        )
    except Exception:
        pass


# ============================================================
# MAYDONNI TAHRIRLASH (nomi, tavsif, narx, o'lcham, sig'im, yetkazib berish)
# ============================================================

@router.callback_query(IsAdmin(), F.data.startswith("apedit:"))
async def edit_field_start(callback: CallbackQuery, state: FSMContext) -> None:
    _, field, product_id_str = callback.data.split(":")
    product_id = int(product_id_str)

    await state.update_data(edit_field=field, edit_product_id=product_id)
    await state.set_state(AdminProductStates.editing_value)

    field_label = FIELD_NAMES.get(field, field)
    hint = ""
    if field == "price":
        hint = "\n\n💡 Faqat raqam kiriting (masalan: 4500000)"

    await callback.message.answer(
        f"✏️ <b>{field_label}</b> uchun yangi qiymat kiriting:{hint}",
        reply_markup=cancel_kb(),
    )
    await callback.answer()


@router.message(AdminProductStates.editing_value, F.text == CANCEL_TEXT)
async def cancel_edit_field(message: Message, state: FSMContext, session: AsyncSession) -> None:
    data = await state.get_data()
    product_id = data.get("edit_product_id")
    await state.clear()

    service = ProductService(session)
    product = await service.get_product(product_id)

    await message.answer("❌ Bekor qilindi.", reply_markup=admin_panel_kb())
    if product:
        await message.answer(
            build_admin_product_text(product),
            reply_markup=admin_product_actions_kb(product.id, product.category_id),
        )


@router.message(AdminProductStates.editing_value)
async def edit_field_value(message: Message, state: FSMContext, session: AsyncSession) -> None:
    data = await state.get_data()
    field = data.get("edit_field")
    product_id = data.get("edit_product_id")

    value: object = message.text.strip()

    if field == "price":
        try:
            value = float(value.replace(" ", "").replace(",", "."))
        except ValueError:
            await message.answer(
                "⚠️ Narxni faqat raqam shaklida kiriting (masalan: 4500000).",
                reply_markup=cancel_kb(),
            )
            return

    service = ProductService(session)
    await service.update_product(product_id, **{field: value})

    await state.clear()
    product = await service.get_product(product_id)

    await message.answer("✅ Muvaffaqiyatli yangilandi!", reply_markup=admin_panel_kb())
    await message.answer(
        build_admin_product_text(product),
        reply_markup=admin_product_actions_kb(product.id, product.category_id),
    )


# ============================================================
# MAHSULOTGA RASM QO'SHISH (mavjud mahsulotga)
# ============================================================

@router.callback_query(IsAdmin(), F.data.startswith("apphoto:"))
async def add_photo_start(callback: CallbackQuery, state: FSMContext) -> None:
    product_id = int(callback.data.split(":", 1)[1])
    await state.update_data(mode="edit_photo", edit_product_id=product_id)
    await state.set_state(AdminProductStates.waiting_photos)

    await callback.message.answer(
        "📷 Mahsulot uchun rasm(lar) yuboring.\n\n"
        f"Tugatgach \"{DONE_PHOTOS_TEXT}\" tugmasini bosing.",
        reply_markup=photos_done_kb(),
    )
    await callback.answer()


# ============================================================
# MAHSULOTGA VIDEO YUKLASH (mavjud mahsulotga)
# ============================================================

@router.callback_query(IsAdmin(), F.data.startswith("apvideo:"))
async def add_video_start(callback: CallbackQuery, state: FSMContext) -> None:
    product_id = int(callback.data.split(":", 1)[1])
    await state.update_data(mode="edit_video", edit_product_id=product_id)
    await state.set_state(AdminProductStates.waiting_video)

    await callback.message.answer(
        "🎥 Mahsulot uchun video yuboring:",
        reply_markup=cancel_kb(),
    )
    await callback.answer()


# ============================================================
# YANGI MAHSULOT QO'SHISH (FSM)
# ============================================================

@router.callback_query(IsAdmin(), F.data == "ap:add")
async def add_product_start(callback: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
    service = ProductService(session)
    categories = await service.get_all_categories()

    if not categories:
        await callback.answer(
            "⚠️ Avval kategoriya qo'shing! (📂 Kategoriyalar bo'limidan)",
            show_alert=True,
        )
        return

    await state.set_state(AdminProductStates.choosing_category)
    await callback.message.answer(
        "📂 Yangi mahsulot uchun kategoriyani tanlang:",
        reply_markup=admin_categories_select_kb(categories),
    )
    await callback.answer()


@router.callback_query(IsAdmin(), AdminProductStates.choosing_category, F.data.startswith("apaddcat:"))
async def add_product_category_chosen(callback: CallbackQuery, state: FSMContext) -> None:
    category_id = int(callback.data.split(":", 1)[1])
    await state.update_data(new_category_id=category_id, mode="new_product")
    await state.set_state(AdminProductStates.waiting_name)

    await callback.message.answer(
        "✏️ Mahsulot nomini kiriting (masalan: <i>Katta novvoy tandiri</i>):",
        reply_markup=cancel_kb(),
    )
    await callback.answer()


# ---- Umumiy bekor qilish (yangi mahsulot FSM) ----

NEW_PRODUCT_STATES = [
    AdminProductStates.waiting_name,
    AdminProductStates.waiting_description,
    AdminProductStates.waiting_price,
    AdminProductStates.waiting_size,
    AdminProductStates.waiting_capacity,
    AdminProductStates.waiting_delivery_info,
    AdminProductStates.waiting_photos,
    AdminProductStates.waiting_video,
    AdminProductStates.confirm,
]


@router.message(F.text == CANCEL_TEXT, AdminProductStates.waiting_name)
@router.message(F.text == CANCEL_TEXT, AdminProductStates.waiting_description)
@router.message(F.text == CANCEL_TEXT, AdminProductStates.waiting_price)
@router.message(F.text == CANCEL_TEXT, AdminProductStates.waiting_size)
@router.message(F.text == CANCEL_TEXT, AdminProductStates.waiting_capacity)
@router.message(F.text == CANCEL_TEXT, AdminProductStates.waiting_delivery_info)
@router.message(F.text == CANCEL_TEXT, AdminProductStates.waiting_photos)
@router.message(F.text == CANCEL_TEXT, AdminProductStates.waiting_video)
@router.message(F.text == CANCEL_TEXT, AdminProductStates.confirm)
async def cancel_product_flow(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("❌ Bekor qilindi.", reply_markup=admin_panel_kb())


@router.message(AdminProductStates.waiting_name)
async def product_name_entered(message: Message, state: FSMContext) -> None:
    if not message.text or len(message.text.strip()) < 2:
        await message.answer("⚠️ Iltimos, to'g'ri nom kiriting.", reply_markup=cancel_kb())
        return

    await state.update_data(new_name=message.text.strip())
    await state.set_state(AdminProductStates.waiting_description)
    await message.answer(
        "📝 Mahsulot tavsifini kiriting (yoki o'tkazib yuboring):",
        reply_markup=skip_kb(),
    )


@router.message(AdminProductStates.waiting_description)
async def product_description_entered(message: Message, state: FSMContext) -> None:
    value = None if message.text == SKIP_TEXT else message.text.strip()
    await state.update_data(new_description=value)
    await state.set_state(AdminProductStates.waiting_price)
    await message.answer(
        "💰 Mahsulot narxini kiriting (so'mda, masalan: 4500000) yoki o'tkazib yuboring:",
        reply_markup=skip_kb(),
    )


@router.message(AdminProductStates.waiting_price)
async def product_price_entered(message: Message, state: FSMContext) -> None:
    if message.text == SKIP_TEXT:
        price = None
    else:
        try:
            price = float(message.text.strip().replace(" ", "").replace(",", "."))
        except ValueError:
            await message.answer(
                "⚠️ Narxni faqat raqam shaklida kiriting yoki o'tkazib yuboring.",
                reply_markup=skip_kb(),
            )
            return

    await state.update_data(new_price=price)
    await state.set_state(AdminProductStates.waiting_size)
    await message.answer(
        "📏 Mahsulot o'lchamini kiriting (masalan: 100x100x150 sm) yoki o'tkazib yuboring:",
        reply_markup=skip_kb(),
    )


@router.message(AdminProductStates.waiting_size)
async def product_size_entered(message: Message, state: FSMContext) -> None:
    value = None if message.text == SKIP_TEXT else message.text.strip()
    await state.update_data(new_size=value)
    await state.set_state(AdminProductStates.waiting_capacity)
    await message.answer(
        "📦 Mahsulot sig'imini kiriting (masalan: 15-20 ta non) yoki o'tkazib yuboring:",
        reply_markup=skip_kb(),
    )


@router.message(AdminProductStates.waiting_capacity)
async def product_capacity_entered(message: Message, state: FSMContext) -> None:
    value = None if message.text == SKIP_TEXT else message.text.strip()
    await state.update_data(new_capacity=value)
    await state.set_state(AdminProductStates.waiting_delivery_info)
    await message.answer(
        "🚚 Yetkazib berish ma'lumotini kiriting (masalan: Toshkent bo'ylab bepul) "
        "yoki o'tkazib yuboring:",
        reply_markup=skip_kb(),
    )


@router.message(AdminProductStates.waiting_delivery_info)
async def product_delivery_entered(message: Message, state: FSMContext) -> None:
    value = None if message.text == SKIP_TEXT else message.text.strip()
    await state.update_data(new_delivery_info=value, new_photos=[])
    await state.set_state(AdminProductStates.waiting_photos)
    await message.answer(
        "📷 Mahsulot rasmlarini yuboring (bir nechtasi mumkin).\n\n"
        f"Tugatgach \"{DONE_PHOTOS_TEXT}\" tugmasini bosing.",
        reply_markup=photos_done_kb(),
    )


@router.message(AdminProductStates.waiting_video)
async def video_received(message: Message, state: FSMContext, session: AsyncSession) -> None:
    data = await state.get_data()
    mode = data.get("mode")

    if message.text == SKIP_TEXT:
        video_id = None
    elif message.video:
        video_id = message.video.file_id
    else:
        await message.answer(
            "⚠️ Iltimos, video yuboring yoki o'tkazib yuboring.",
            reply_markup=skip_kb() if mode == "new_product" else cancel_kb(),
        )
        return

    if mode == "edit_video":
        product_id = data.get("edit_product_id")
        service = ProductService(session)
        if video_id:
            await service.set_video(product_id, video_id)
        await state.clear()

        product = await service.get_product(product_id)
        await message.answer("✅ Video yuklandi!" if video_id else "❌ Bekor qilindi.", reply_markup=admin_panel_kb())
        await message.answer(
            build_admin_product_text(product),
            reply_markup=admin_product_actions_kb(product.id, product.category_id),
        )
        return

    # Yangi mahsulot flow - tasdiqlash
    await state.update_data(new_video=video_id)
    await show_product_confirmation(message, state)


@router.message(AdminProductStates.waiting_photos)
async def photo_received(message: Message, state: FSMContext, session: AsyncSession) -> None:
    data = await state.get_data()
    mode = data.get("mode")

    if message.text == DONE_PHOTOS_TEXT:
        if mode == "edit_photo":
            product_id = data.get("edit_product_id")
            await state.clear()
            service = ProductService(session)
            product = await service.get_product(product_id)
            await message.answer("✅ Rasmlar saqlandi!", reply_markup=admin_panel_kb())
            await message.answer(
                build_admin_product_text(product),
                reply_markup=admin_product_actions_kb(product.id, product.category_id),
            )
            return
        else:
            # Yangi mahsulot - video bosqichiga o'tish
            await state.set_state(AdminProductStates.waiting_video)
            await message.answer(
                "🎥 Mahsulot uchun video yuboring (yoki o'tkazib yuboring):",
                reply_markup=skip_kb(),
            )
            return

    if not message.photo:
        await message.answer(
            "⚠️ Iltimos, rasm yuboring yoki tugatish tugmasini bosing.",
            reply_markup=photos_done_kb(),
        )
        return

    file_id = message.photo[-1].file_id

    if mode == "edit_photo":
        product_id = data.get("edit_product_id")
        service = ProductService(session)
        await service.add_photo(product_id, file_id)
        await message.answer(
            f"✅ Rasm qo'shildi! Yana rasm yuborishingiz mumkin yoki \"{DONE_PHOTOS_TEXT}\" tugmasini bosing.",
            reply_markup=photos_done_kb(),
        )
    else:
        photos = data.get("new_photos", [])
        photos.append(file_id)
        await state.update_data(new_photos=photos)
        await message.answer(
            f"✅ Rasm qabul qilindi ({len(photos)} ta). Yana yuborishingiz mumkin "
            f"yoki \"{DONE_PHOTOS_TEXT}\" tugmasini bosing.",
            reply_markup=photos_done_kb(),
        )


async def show_product_confirmation(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    await state.set_state(AdminProductStates.confirm)

    photos_count = len(data.get("new_photos", []))
    has_video = "✅ bor" if data.get("new_video") else "❌ yo'q"
    price = data.get("new_price")

    text = (
        "🆕 <b>Yangi mahsulot ma'lumotlari</b>\n\n"
        f"📛 Nomi: {data.get('new_name')}\n"
        f"📝 Tavsif: {data.get('new_description') or '—'}\n"
        f"💰 Narx: {format_price(price)}\n"
        f"📏 O'lcham: {data.get('new_size') or '—'}\n"
        f"📦 Sig'im: {data.get('new_capacity') or '—'}\n"
        f"🚚 Yetkazib berish: {data.get('new_delivery_info') or '—'}\n"
        f"📷 Rasmlar: {photos_count} ta\n"
        f"🎥 Video: {has_video}\n\n"
        "Ma'lumotlar to'g'ri bo'lsa, saqlang 👇"
    )

    await message.answer(text, reply_markup=confirm_product_kb())


@router.message(AdminProductStates.confirm, F.text == SAVE_TEXT)
async def save_new_product(message: Message, state: FSMContext, session: AsyncSession) -> None:
    data = await state.get_data()
    service = ProductService(session)

    product = await service.add_product(
        category_id=data.get("new_category_id"),
        name=data.get("new_name"),
        description=data.get("new_description"),
        price=data.get("new_price"),
        size=data.get("new_size"),
        capacity=data.get("new_capacity"),
        delivery_info=data.get("new_delivery_info"),
    )

    photos = data.get("new_photos", [])
    if photos:
        product.set_photos(photos)

    video = data.get("new_video")
    if video:
        product.video_id = video

    await session.flush()

    await state.clear()
    await message.answer(
        f"✅ Yangi mahsulot qo'shildi: <b>{product.name}</b>",
        reply_markup=admin_panel_kb(),
    )
