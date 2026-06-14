from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.product_service import ProductService
from app.keyboards.user import categories_kb, products_kb, product_detail_kb, main_menu_kb
from app.utils.helpers import format_price

router = Router(name="user_catalog")


def build_product_caption(product) -> str:
    lines = [f"🔥 <b>{product.name}</b>", ""]

    if product.description:
        lines.append(product.description)
        lines.append("")

    lines.append(f"💰 <b>Narx:</b> {format_price(product.price)}")

    if product.size:
        lines.append(f"📏 <b>O'lcham:</b> {product.size}")

    if product.capacity:
        lines.append(f"📦 <b>Sig'im:</b> {product.capacity}")

    if product.delivery_info:
        lines.append(f"🚚 <b>Yetkazib berish:</b> {product.delivery_info}")

    return "\n".join(lines)


@router.message(F.text == "🔥 Tandirlar")
async def show_categories(message: Message, session: AsyncSession) -> None:
    service = ProductService(session)
    categories = await service.get_categories()

    if not categories:
        await message.answer(
            "😔 Hozircha kategoriyalar mavjud emas. Tez orada qo'shiladi.",
            reply_markup=main_menu_kb(),
        )
        return

    await message.answer(
        "🔥 <b>Tandirlar katalogi</b>\n\nKerakli kategoriyani tanlang 👇",
        reply_markup=categories_kb(categories),
    )


@router.callback_query(F.data.startswith("cat:"))
async def show_products(callback: CallbackQuery, session: AsyncSession) -> None:
    cat_value = callback.data.split(":", 1)[1]
    service = ProductService(session)

    if cat_value == "back":
        categories = await service.get_categories()
        await callback.message.edit_text(
            "🔥 <b>Tandirlar katalogi</b>\n\nKerakli kategoriyani tanlang 👇",
            reply_markup=categories_kb(categories),
        )
        await callback.answer()
        return

    if cat_value == "all":
        products = await service.get_all_products()
        back_callback = "cat:back"
        title = "📋 <b>Barcha tandirlar</b>\n\nMahsulotni tanlang 👇"
    else:
        category_id = int(cat_value)
        category = await service.get_category(category_id)
        products = await service.get_products_by_category(category_id)
        back_callback = "cat:back"
        cat_name = category.name if category else ""
        title = f"🔥 <b>{cat_name}</b>\n\nMahsulotni tanlang 👇"

    if not products:
        await callback.answer("😔 Bu kategoriyada hozircha mahsulotlar yo'q", show_alert=True)
        return

    try:
        await callback.message.edit_text(title, reply_markup=products_kb(products, back_callback))
    except Exception:
        await callback.message.answer(title, reply_markup=products_kb(products, back_callback))
    await callback.answer()


@router.callback_query(F.data.startswith("prod:"))
async def show_product_detail(callback: CallbackQuery, session: AsyncSession) -> None:
    product_id = int(callback.data.split(":", 1)[1])
    service = ProductService(session)
    product = await service.get_product(product_id)

    if not product:
        await callback.answer("😔 Mahsulot topilmadi", show_alert=True)
        return

    await callback.answer()

    photos = product.get_photos()

    # Rasmlarni yuborish (agar mavjud bo'lsa)
    if len(photos) > 1:
        media = [InputMediaPhoto(media=p) for p in photos[:10]]
        await callback.message.answer_media_group(media)
    elif len(photos) == 1:
        await callback.message.answer_photo(photos[0])

    # Videoni yuborish (agar mavjud bo'lsa)
    if product.video_id:
        await callback.message.answer_video(product.video_id)

    # Determine back callback - go back to category's product list
    if product.category_id:
        back_callback = f"cat:{product.category_id}"
    else:
        back_callback = "cat:back"

    caption = build_product_caption(product)
    await callback.message.answer(
        caption,
        reply_markup=product_detail_kb(product.id, back_callback),
    )
