from aiogram.fsm.state import State, StatesGroup


class OrderStates(StatesGroup):
    """Buyurtma berish FSM holatlari"""
    waiting_name = State()
    waiting_phone = State()


class AdminProductStates(StatesGroup):
    """Mahsulot qo'shish/tahrirlash FSM holatlari"""
    choosing_category = State()
    waiting_name = State()
    waiting_description = State()
    waiting_price = State()
    waiting_size = State()
    waiting_capacity = State()
    waiting_delivery_info = State()
    waiting_photos = State()
    waiting_video = State()
    confirm = State()

    # Tahrirlash uchun
    editing_field = State()
    editing_value = State()


class AdminCategoryStates(StatesGroup):
    waiting_name = State()
    waiting_emoji = State()


class AdminBroadcastStates(StatesGroup):
    """Reklama yuborish FSM holatlari"""
    choosing_type = State()
    waiting_text = State()
    waiting_photo = State()
    waiting_video = State()
    waiting_button_text = State()
    waiting_button_url = State()
    waiting_forward = State()
    confirm = State()


class AdminOrderStates(StatesGroup):
    waiting_note = State()
