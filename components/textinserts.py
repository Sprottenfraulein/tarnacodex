def insert(realm, pc, text):
    new_text = text
    new_text = new_text.replace('$ch', pc.char_sheet.name.capitalize())
    new_text = new_text.replace('$ty', pc.char_sheet.type.capitalize())
    if pc.location is not None:
        new_text = new_text.replace('$cn', pc.location[0]['label'])
    else:
        new_text = new_text.replace('$cn', 'Dream gate')
    return new_text
