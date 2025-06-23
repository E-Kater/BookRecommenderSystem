from app.models.schemas import Item

fake_items_db = {}


def get_item(item_id: int):
    return fake_items_db.get(item_id)


def create_item(item: Item):
    item_id = len(fake_items_db) + 1
    fake_items_db[item_id] = item
    return item
