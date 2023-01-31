def insert(realm, pc, text):
    new_text = text
    new_text = new_text.replace('$ch', pc.char_sheet.name.capitalize())
    new_text = new_text.replace('$ty', pc.char_sheet.type.capitalize())
    return new_text
