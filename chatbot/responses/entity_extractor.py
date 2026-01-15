import spacy
from spacy.matcher import Matcher

nlp = spacy.load("xx_ent_wiki_sm")
matcher = Matcher(nlp.vocab)

# quantity
matcher.add(
    "QUANTITY",
    [[{"LIKE_NUM": True}]]
)

# product: "sản phẩm A"
matcher.add(
    "PRODUCT",
    [[
        {"LOWER": "sản"},
        {"LOWER": "phẩm"},
        {"TEXT":{"REGEX": r"^[a-zA-Z0-9_]+$"}}
    ]]
)

# manufacturer: "nhà sản xuất X"
matcher.add(
    "MANUFACTURER",
    [[
        {"LOWER": "nhà"},
        {"LOWER": "sản"},
        {"LOWER": "xuất"},
        {"TEXT":{"REGEX": r"^[a-zA-Z0-9_]+$"}}
    ]]
)




def extract_entities(text):
    entities = {}
    doc = nlp(text)
    for match_id, start, end in matcher(doc):
        label = nlp.vocab.strings[match_id]
        span = doc[start:end]

        if label == "QUANTITY":
            entities["quantity"] = span.text

        elif label == "PRODUCT":
            entities["product"] = span.text.replace("sản phẩm ", "")

        elif label == "MANUFACTURER":
            entities["manufacturer"] = span.text.replace("nhà sản xuất ", "")

    return entities