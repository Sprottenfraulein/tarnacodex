import os, shutil
import pickle
from components import treasure, skill, dbrequests


def save_char(wins_dict, pc, maze, db, tileset, audio):
    filename = "./save/%s/character.pd" % pc.char_sheet.id
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "wb") as f:
        f.seek(0)
        pickle.dump(pc.char_sheet.attributes, f)
        pickle.dump(pc.char_sheet.pools, f)
        pickle.dump(pc.char_sheet.attacks, f)
        pickle.dump(pc.char_sheet.defences, f)
        # Pickling inventory list
        skills = pc.char_sheet.skills
        for itm in skills:
            if itm is None:
                continue
            for key in itm.props.keys():
                if 'image_' in key or 'sound_' in key:
                    itm.props[key] = None
        pickle.dump(skills, f)
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
                if itm.props['use_skill'] is not None:
                    for key in itm.props['use_skill'].props.keys():
                        if 'image_' in key or 'sound_' in key:
                            itm.props['use_skill'].props[key] = None
        pickle.dump(equipped, f)
        # Pickling inventory list
        inventory = pc.char_sheet.inventory
        for itm in inventory:
            if itm is None:
                continue
            for key in itm.props.keys():
                if 'image_' in key or 'sound_' in key:
                    itm.props[key] = None
            if itm.props['use_skill'] is not None:
                for key in itm.props['use_skill'].props.keys():
                    if 'image_' in key or 'sound_' in key:
                        itm.props['use_skill'].props[key] = None
        pickle.dump(inventory, f)
        # Pickling hotbar list
        hotbar = pc.char_sheet.hotbar
        for itm in hotbar:
            if itm is None:
                continue
            for key in itm.props.keys():
                if 'image_' in key or 'sound_' in key:
                    itm.props[key] = None
            if 'treasure_id' in itm.props and itm.props['use_skill'] is not None:
                for key in itm.props['use_skill'].props.keys():
                    if 'image_' in key or 'sound_' in key:
                        itm.props['use_skill'].props[key] = None
        pickle.dump(pc.char_sheet.hotbar, f)
        pickle.dump(pc.location, f)
        pickle.dump(pc.char_portrait_index, f)

        pc_obj_vars = {
            'id': pc.char_sheet.id,
            'stage_entry': pc.stage_entry,
            'tradepost_level': pc.tradepost_level,
            'hardcore_char': pc.hardcore_char,
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

        wins_offsets = {}
        for win in ('charstats', 'hotbar','inventory','pools', 'skillbook', 'trade'):
            wins_offsets[win] = wins_dict[win].offset_x, wins_dict[win].offset_y
        pickle.dump(wins_offsets, f)

        f.truncate()

    restore_char_media(pc, db.cursor, tileset, audio)

    dbrequests.char_save(db, pc.char_sheet.id, pc.hardcore_char, maze.stage_index, maze.stage_dict['label'],
                         pc.location[0]['label'], pc.char_sheet.level, pc.char_sheet.name, pc.char_sheet.type,
                         pc.char_portrait_index)


def load_char(wins_dict, pc, db_cursor, tileset, audio):
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
        pc.char_portrait_index = pickle.load(f)
        pc_obj_vars = pickle.load(f)
        wins_offsets = pickle.load(f)
        for win in ('charstats', 'hotbar', 'inventory', 'pools', 'skillbook', 'trade'):
            wins_dict[win].offset_x, wins_dict[win].offset_y = wins_offsets[win]

        pc.char_sheet.id = pc_obj_vars['id']
        pc.hardcore_char = pc_obj_vars['hardcore_char']
        pc.stage_entry = pc_obj_vars['stage_entry']
        pc.tradepost_level = pc_obj_vars['tradepost_level']
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

    restore_char_media(pc, db_cursor, tileset, audio, cooldown_reset=True)


def chapter_wipe(db, pc):
    filename = "./save/%s/dung" % pc.char_sheet.id
    if not os.path.exists(filename):
        return
    shutil.rmtree(filename, ignore_errors=True)
    dbrequests.chapter_progress_reset(db, pc.char_sheet.id)


def char_wipe(db, char_id):
    filename = "./save/%s" % char_id
    if not os.path.exists(filename):
        return
    shutil.rmtree(filename, ignore_errors=True)
    dbrequests.chapter_progress_reset(db, char_id)


def save_maze(pc, maze, db, tile_sets, animations, audio):
    filename = "./save/%s/dung/%s.pd" % (pc.char_sheet.id, maze.stage_index)
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "wb") as f:
        f.seek(0)

        pickle.dump(maze.chapter, f)
        pickle.dump(maze.stage_index, f)
        # pickle.dump(maze.stage_dict, f)
        pickle.dump(maze.exits_list, f)
        pickle.dump(maze.width, f)
        pickle.dump(maze.height, f)
        pickle.dump(maze.lvl, f)
        pickle.dump(maze.trap_rate, f)
        pickle.dump(maze.lock_rate, f)
        pickle.dump(maze.magic_lock_rate, f)
        pickle.dump(maze.monster_ids, f)
        pickle.dump(maze.monster_type_amount, f)
        pickle.dump(maze.monster_amount_rate, f)
        pickle.dump(maze.tradepost_update, f)
        pickle.dump(maze.array, f)

        for mob in maze.mobs:
            mob.aimed = False
            mob.anim_set = None
            mob.image = None
        for door in maze.doors:
            door.tileset = None
            door.image = None
        for chest in maze.chests:
            chest.tileset = None
            chest.image = None
            if chest.container is None:
                continue
            for itm in chest.container:
                if itm is None:
                    continue
                for key in itm.props.keys():
                    if 'image_' in key or 'sound_' in key:
                        itm.props[key] = None
                if 'treasure_id' in itm.props and itm.props['use_skill'] is not None:
                    for key in itm.props['use_skill'].props.keys():
                        if 'image_' in key or 'sound_' in key:
                            itm.props['use_skill'].props[key] = None
        for trap in maze.traps:
            trap.tileset = None
            trap.images = None
        for stair in maze.exits:
            stair.image = None
            stair.room = None
        for itm in maze.loot:
            if itm is None:
                continue
            for key in itm.props.keys():
                if 'image_' in key or 'sound_' in key:
                    itm.props[key] = None
            if 'treasure_id' in itm.props and itm.props['use_skill'] is not None:
                for key in itm.props['use_skill'].props.keys():
                    if 'image_' in key or 'sound_' in key:
                        itm.props['use_skill'].props[key] = None

        for room in maze.rooms:
            room.adj_rooms = None

        pickle.dump(maze.rooms, f)
        pickle.dump(maze.doors, f)
        pickle.dump(maze.chests, f)
        pickle.dump(maze.mobs, f)
        pickle.dump(maze.traps, f)
        pickle.dump(maze.exits, f)
        pickle.dump(maze.loot, f)
        pickle.dump(maze.anim_timing, f)

        f.truncate()

    restore_maze_media(pc, maze, db.cursor, tile_sets, animations, audio, cooldown_reset=True)


def load_maze(pc, maze, db, tile_sets, animations, audio):
    filename = "./save/%s/dung/%s.pd" % (pc.char_sheet.id, pc.location[1])
    if not os.path.exists(filename):
        return
    with open(filename, "rb") as f:
        maze.chapter = pickle.load(f)
        maze.stage_index = pickle.load(f)
        # maze.stage_dict = pickle.load(f)
        maze.exits_list = pickle.load(f)

        maze.width = pickle.load(f)
        maze.height = pickle.load(f)

        maze.lvl = pickle.load(f)

        maze.trap_rate = pickle.load(f)
        maze.lock_rate = pickle.load(f)
        maze.magic_lock_rate = pickle.load(f)

        maze.monster_ids = pickle.load(f)
        maze.monster_type_amount = pickle.load(f)
        maze.monster_amount_rate = pickle.load(f)
        maze.tradepost_update = pickle.load(f)
        maze.array = pickle.load(f)

        maze.rooms = pickle.load(f)
        maze.doors = pickle.load(f)
        maze.chests = pickle.load(f)
        maze.mobs = pickle.load(f)
        maze.traps = pickle.load(f)
        maze.exits = pickle.load(f)
        maze.loot = pickle.load(f)
        maze.anim_timing = pickle.load(f)

        maze.tile_set = tile_sets.get_maze_tiles(maze.stage_dict['tile_set'])

    restore_maze_media(pc, maze, db.cursor, tile_sets, animations, audio, cooldown_reset=True)


def restore_char_media(pc, db_cursor, tile_sets, audio, cooldown_reset=False):
    equipped = pc.char_sheet.equipped
    for socket in equipped:
        for itm in socket:
            if itm is None:
                continue
            treasure.images_update(db_cursor, itm.props, tile_sets)
            treasure.sounds_update(db_cursor, itm.props, audio)
            if itm.props['use_skill'] is not None:
                if cooldown_reset:
                    itm.props['use_skill'].cooldown_timer = 0
                skill.images_update(db_cursor, itm.props['use_skill'].props, tile_sets)
                skill.sounds_update(db_cursor, itm.props['use_skill'].props, audio)

    inventory = pc.char_sheet.inventory
    for itm in inventory:
        if itm is None:
            continue
        treasure.images_update(db_cursor, itm.props, tile_sets)
        treasure.sounds_update(db_cursor, itm.props, audio)
        if itm.props['use_skill'] is not None:
            if cooldown_reset:
                itm.props['use_skill'].cooldown_timer = 0
            skill.images_update(db_cursor, itm.props['use_skill'].props, tile_sets)
            skill.sounds_update(db_cursor, itm.props['use_skill'].props, audio)

    skills = pc.char_sheet.skills
    for itm in skills:
        if itm is None:
            continue
        skill.images_update(db_cursor, itm.props, tile_sets)
        skill.sounds_update(db_cursor, itm.props, audio)
        if cooldown_reset:
            itm.cooldown_timer = 0

    hotbar = pc.char_sheet.hotbar
    for itm in hotbar:
        if itm is None:
            continue
        if 'treasure_id' in itm.props:
            treasure.images_update(db_cursor, itm.props, tile_sets)
            treasure.sounds_update(db_cursor, itm.props, audio)
            if itm.props['use_skill'] is not None:
                if cooldown_reset:
                    itm.props['use_skill'].cooldown_timer = 0
                skill.images_update(db_cursor, itm.props['use_skill'].props, tile_sets)
                skill.sounds_update(db_cursor, itm.props['use_skill'].props, audio)
        elif 'skill_id' in itm.props:
            skill.images_update(db_cursor, itm.props, tile_sets)
            skill.sounds_update(db_cursor, itm.props, audio)
            if cooldown_reset:
                itm.cooldown_timer = 0


def restore_maze_media(pc, maze, db_cursor, tile_sets, animations, audio, cooldown_reset=False):
    for mob in maze.mobs:
        mob.anim_set = animations.get_animation(mob.stats['animation'])
        mob.animate()
    for door in maze.doors:
        door.tileset = maze.tile_set
        door.image_update()
    for chest in maze.chests:
        chest.tileset = maze.tile_set
        chest.image_update()
        if chest.container is None:
            continue
        for itm in chest.container:
            if itm is None:
                continue
            treasure.images_update(db_cursor, itm.props, tile_sets)
            treasure.sounds_update(db_cursor, itm.props, audio)
            if itm.props['use_skill'] is not None:
                if cooldown_reset:
                    itm.props['use_skill'].cooldown_timer = 0
                skill.images_update(db_cursor, itm.props['use_skill'].props, tile_sets)
                skill.sounds_update(db_cursor, itm.props['use_skill'].props, audio)
    for trap in maze.traps:
        trap.tileset = maze.tile_set
        trap.image_update()
    for stair in maze.exits:
        stair.image = maze.tile_set[stair.tilename]
    for itm in maze.loot:
        if itm is None:
            continue
        treasure.images_update(db_cursor, itm.props, tile_sets)
        treasure.sounds_update(db_cursor, itm.props, audio)
        if itm.props['use_skill'] is not None:
            if cooldown_reset:
                itm.props['use_skill'].cooldown_timer = 0
            skill.images_update(db_cursor, itm.props['use_skill'].props, tile_sets)
            skill.sounds_update(db_cursor, itm.props['use_skill'].props, audio)