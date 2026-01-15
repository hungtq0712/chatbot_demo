from unittest import case

from sentence_transformers import SentenceTransformer
from sentence_transformers import util

from chatbot.responses.entity_extractor import extract_entities
from chatbot.responses.handle import *
intent_texts = {
    "IMPORT": "Nhập thêm x sản phẩm A thuộc nhà sản xuất B",
    "EXPORT": "Xuất từ kho x sản phẩm A thuộc nhà sản xuất B",
    "CHECK":  "Kiểm tra số lượng sản phẩm A nhà sản xuất B",
    "NAME" : "Bạn tên là gì ?",
    "HI" : " Chào bạn",
    "THANKS" : "Cảm ơn bạn.",
    "GOODBYE" :" Tạm biệt",
    "HELP" : "bạn có thể làm được gì ?",
    "SHOW" : " Liệt kê tất cả mặt hàng trong kho "
}



# 1) Model embedding (chọn model phù hợp ngôn ngữ; ví dụ multilingual)
model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
I = InventoryService()


def dectIntent(user_message):
    # 2) Embed intents và users
    intent_codes = list(intent_texts.keys())
    intent_sentences = [intent_texts[k] for k in intent_codes]

    intent_embeddings = model.encode(intent_sentences, convert_to_tensor=True, normalize_embeddings=True)
    user_embedding = model.encode(user_message, convert_to_tensor=True, normalize_embeddings=True)

    best_code = None
    best_score = float("-inf")

    for j, code in enumerate(intent_codes):
        score = util.cos_sim(user_embedding, intent_embeddings[j]).item()
        # print(f"  {code:<8} similarity = {score:.3f}")

        if score > best_score:
            best_score = score
            best_code = code
    return best_code

def messages_1(user_text :str) -> str:
    new_intent = dectIntent(user_text)
    #print(new_intent)
    match new_intent:
        case Action.IMPORT:
            return handle_import(extract_entities(user_text), I)
        case Action.EXPORT:
            return handle_export(extract_entities(user_text), I)
        case Action.CHECK:
            return handle_check(extract_entities(user_text), I)
        case Action.HI:
            return handle_hi()
        case Action.NAME:
            return handle_name()
        case Action.GOODBYE:
            return handle_goodbye()
        case Action.HELP:
            return handle_help()
        case Action.THANKS:
            return handle_thanks()
        case Action.SHOW:
            return handle_show(I)


def main():
    print("Start")
    a = "Liệt kê tất cả mặt hàng trong kho  "
    for i in range(3):
        print(messages_1(a))

if __name__ == "__main__":
    main()
