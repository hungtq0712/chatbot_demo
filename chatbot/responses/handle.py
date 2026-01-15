
import sqlite3
import random
import json
import numpy as np
class Action:
    IMPORT = "IMPORT"
    EXPORT = "EXPORT"
    CHECK = "CHECK"
    NAME= "NAME"
    HI= "HI"
    THANKS= "THANKS"
    GOODBYE= "GOODBYE"
    HELP= "HELP"
    SHOW = "SHOW"
FIELD_VN = {
    "quantity": "số lượng",
    "product": "sản phẩm",
    "manufacturer": "nhà sản xuất"
}
#---- geetting----#
path="responses/intents.json"
with open(path, "r", encoding="utf-8") as f:
    data= json.load(f)
def pick_response(tag: str, data: dict) -> str:
    for intent in data["intents"]:
        if intent["tag"] == tag:
            return random.choice(intent["responses"])
    return ""
def handle_hi():
    return pick_response("hi", data)
def handle_goodbye():
    return pick_response("goodbye", data)
def handle_name():
    return pick_response("name", data)
def handle_thanks():
    return pick_response("thanks", data)
def handle_help():
    return pick_response("help", data)

#---sevice---#
class InventoryService:
    def __init__(self, db_path="inventory.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._init_db()

    def _init_db(self):
        cursor = self.conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product TEXT NOT NULL,
            manufacturer TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            UNIQUE(product, manufacturer)
        )
        """)
        self.conn.commit()

    def import_item(self, product, manufacturer, quantity) -> str:
        cursor = self.conn.cursor()

        # Cập nhật số lượng nếu đã tồn tại
        cursor.execute("""
                       UPDATE inventory
                       SET quantity = quantity + ?
                       WHERE product = ?
                         AND manufacturer = ?
                       """, (quantity, product, manufacturer))

        # Nếu không có dòng nào được cập nhật → chưa tồn tại
        if cursor.rowcount == 0:
            cursor.execute("""
                           INSERT INTO inventory (product, manufacturer, quantity)
                           VALUES (?, ?, ?)
                           """, (product, manufacturer,quantity))

        self.conn.commit()
        return self.check_item_by_manufacturer(product, manufacturer)

    def export_item(self, product, manufacturer, quantity: int):
        cursor = self.conn.cursor()

        cursor.execute("""
        SELECT quantity FROM inventory
        WHERE product=? AND manufacturer=?
        """, (product, manufacturer))
        row = cursor.fetchone()
        if not row :
            raise ValueError("Không có sản phẩm trong kho")

        if not row or row[0] < int(quantity):
            raise ValueError("Không đủ hàng trong kho")

        cursor.execute("""
        UPDATE inventory
        SET quantity = quantity - ?
        WHERE product=? AND manufacturer=?
        """, (quantity, product, manufacturer))

        self.conn.commit()
        return self.check_item_by_manufacturer(product, manufacturer)

    def check_item(self, product):
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT SUM(quantity) FROM inventory
        WHERE product=?
        """, (product,))
        row = cursor.fetchone()
        return row[0] if row and row[0] else 0

    def show(self):
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT product, manufacturer, quantity
        FROM inventory
        """)
        row = cursor.fetchall()
        return row
    def check_item_by_manufacturer(self, product: str, manufacturer: str) -> int:
        cursor = self.conn.cursor()
        cursor.execute("""
                       SELECT quantity
                       FROM inventory
                       WHERE product = ?
                         AND manufacturer = ?
                       """, (product, manufacturer))
        row = cursor.fetchone()
        return row[0] if row else 0

def handle_import(entities, service: InventoryService)->str:
    required = ["quantity", "product", "manufacturer"]
    missing = [e for e in required if e not in entities]

    if missing:
        return f"Thiếu thông tin: {', '.join(FIELD_VN[e] for e in missing)}"

    new_qty = service.import_item(
        entities["product"],
        entities["manufacturer"],
        entities["quantity"]
    )

    return f"Đã nhập {entities['quantity']} sản phẩm,{entities['product']} (NSX {entities['manufacturer']}) ,Tồn kho hiện tại: {new_qty}"

def handle_export(entities, service: InventoryService)->str:
    required = ["quantity", "product","manufacturer"]
    missing = [e for e in required if e not in entities]

    if missing:
        return f"Thiếu thông tin: {', '.join(FIELD_VN[e] for e in missing)}"

    try:
        new_qty = service.export_item(
            entities["product"],
            entities["manufacturer"],
            entities["quantity"]
        )
    except ValueError as e:
        return  f"erro {str(e)}"

    return f"Đã xuất {entities['quantity']} sản phẩm,{entities['product']} (NSX {entities['manufacturer']}) ,Tồn kho hiện tại: {new_qty}"


def handle_check(entities, service: InventoryService)->str:
    if "product" not in entities:
        return "Bạn muốn kiểm tra tồn kho sản phẩm nào?"


    qty = service.check_item(entities["product"])

    return f"Sản phẩm {entities['product']} hiện còn {qty} trong kho"




def handle_show( service: InventoryService)->str:

    rows = service.show()
    if not rows:
        return "Kho hiện đang trống"
    lines = [f"Kho bao gồm:"]
    for product, manufacturer, quantity in rows:
        lines.append(
            f"mặt hàng {product} (NSX {manufacturer}): {quantity} ;"
        )
    return "\n".join(lines)

