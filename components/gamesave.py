import os
import pickle
from components import treasure, skill, dbrequests


def save_char(pc, maze, db, tileset, audio):
    filename = "./save/%s/character.pd" % pc.char_sheet.id
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "wb") as f:
        f.seek(0)
        pickle.dump(pc.char_sheet.attributes, f)
        pickle.dump(pc.char_sheet.pools, f)
        pickle.dump(pc.char_sheet.attacks, f)
        pickle.dump(pc.char_sheet.defences, f)
        pickle.dump(pc.char_sheet.skills, f)
        pickle.dump(pc.char_sheet.profs, f)
        pickle.dump(pc.char_sheet.de_buffs, f)
        pickle.dump(pc.char_sheet.modifiers, f)
        # Pickling equipped list
        equipped = pc.char_sheet.equipped
        for socket in equipped:
            for itm in socket:
                if itm is None:
                    continue
                for key in itm.props.keys():
                    if 'image_' in key or 'sound_' in key:
                        itm.props[key] = None
        pickle.dump(equipped, f)
        # Pickling inventory list
        inventory = pc.char_sheet.inventory
        for itm in inventory:
            if itm is None:
                continue
            for key in itm.props.keys():
                if 'image_' in key or 'sound_' in key:
                    itm.props[key] = None
        pickle.dump(inventory, f)
        # Pickling hotbar list
        hotbar = pc.char_sheet.hotbar
        for itm in hotbar:
            if itm is None:
                continue
            for key in itm.props.keys():
                if 'image_' in key or 'sound_' in key:
                    itm.props[key] = None
        pickle.dump(pc.char_sheet.hotbar, f)
        pickle.dump(pc.location, f)

        pc_obj_vars = {
            'id': pc.char_sheet.id,
            'name': pc.char_sheet.name,
            'type': pc.char_sheet.type,
            'level': pc.char_sheet.level,
            'attr_rate': pc.char_sheet.attr_rate,
            'hp': pc.char_sheet.hp,
            'mp': pc.char_sheet.mp,
            'food': pc.char_sheet.food,
            'exp_rate': pc.char_sheet.exp_rate,
            'exp_rate_multiplier': pc.char_sheet.exp_rate_multiplier,
            'experience': pc.char_sheet.experience,
            'exp_next_lvl': pc.char_sheet.exp_next_lvl,
            'exp_prev_lvl': pc.char_sheet.exp_prev_lvl,
            'gold_coins': pc.char_sheet.gold_coins
        }
        pickle.dump(pc_obj_vars, f)
        f.truncate()

    restore_media(pc, db.cursor, tileset, audio)

    dbrequests.char_save(db, pc.char_sheet.id, pc.location[1], maze.stage_dict['label'], pc.location[0]['label'], pc.char_sheet.level,
                         pc.char_sheet.name, pc.char_sheet.type, pc.char_portrait_index)


def load_char(pc, db_cursor, tileset, audio):
    filename = "./save/%s/character.pd" % pc.char_sheet.id
    if not os.path.exists(filename):
        return
    with open(filename, "rb") as f:
        pc.char_sheet.attributes = pickle.load(f)
        pc.char_sheet.pools = pickle.load(f)
        pc.char_sheet.attacks = pickle.load(f)
        pc.char_sheet.defences = pickle.load(f)
        pc.char_sheet.skills = pickle.load(f)
        pc.char_sheet.profs = pickle.load(f)
        pc.char_sheet.de_buffs = pickle.load(f)
        pc.char_sheet.modifiers = pickle.load(f)
        # Pickling equipped list
        pc.char_sheet.equipped = pickle.load(f)
        # Pickling inventory list
        pc.char_sheet.inventory = pickle.load(f)
        # Pickling hotbar list
        pc.char_sheet.hotbar = pickle.load(f)
        pc.location = pickle.load(f)
        pc_obj_vars = pickle.load(f)

        pc.char_sheet.id = pc_obj_vars['id']
        pc.char_sheet.name = pc_obj_vars['name']
        pc.char_sheet.type = pc_obj_vars['type']
        pc.char_sheet.level = pc_obj_vars['level']
        pc.char_sheet.attr_rate = pc_obj_vars['attr_rate']
        pc.char_sheet.hp = pc_obj_vars['hp']
        pc.char_sheet.mp = pc_obj_vars['mp']
        pc.char_sheet.food = pc_obj_vars['food']
        pc.char_sheet.exp_rate = pc_obj_vars['exp_rate']
        pc.char_sheet.exp_rate_multiplier = pc_obj_vars['exp_rate_multiplier']
        pc.char_sheet.experience = pc_obj_vars['experience']
        pc.char_sheet.exp_next_lvl = pc_obj_vars['exp_next_lvl']
        pc.char_sheet.exp_prev_lvl = pc_obj_vars['exp_prev_lvl']
        pc.char_sheet.gold_coins = pc_obj_vars['gold_coins']

    restore_media(pc, db_cursor, tileset, audio)


def restore_media(pc, db_cursor, tileset, audio):
    equipped = pc.char_sheet.equipped
    for socket in equipped:
        for itm in socket:
            if itm is None:
                continue
            treasure.images_update(db_cursor, itm.props, tileset)
            treasure.sounds_update(db_cursor, itm.props, audio)

    inventory = pc.char_sheet.inventory
    for itm in inventory:
        if itm is None:
            continue
        treasure.images_update(db_cursor, itm.props, tileset)
        treasure.sounds_update(db_cursor, itm.props, audio)

    hotbar = pc.char_sheet.hotbar
    for itm in hotbar:
        if itm is None:
            continue
        if 'treasure_id' in itm.props:
            treasure.images_update(db_cursor, itm.props, tileset)
            treasure.sounds_update(db_cursor, itm.props, audio)
        elif 'skill_id' in itm.props:
            skill.images_update(db_cursor, itm.props, tileset)
            skill.sounds_update(db_cursor, itm.props, audio)
