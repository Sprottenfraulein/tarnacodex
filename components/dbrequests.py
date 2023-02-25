from components import debuff, initmod
import random


def trap_params_get(cursor, table_name, key_level):
    ex_str = "SELECT label, range, attack_type, attack_val_base, attack_val_spread, lvl, sound_attack FROM %s WHERE monster_type='mt_trap' AND lvl<=?" % (table_name,)
    cursor.execute(ex_str, (key_level,))
    rows = cursor.fetchall()

    return rows


def tile_ind_get(cursor, table_name, key_set):
    ex_str = """SELECT * FROM %s WHERE point=?""" % (table_name,)
    cursor.execute(ex_str, (key_set,))
    rows = cursor.fetchall()

    return rows[0]


def char_params_get(cursor, table_name, key_chartype):
    ex_str = "SELECT * FROM %s WHERE char_type=?" % (table_name,)
    cursor.execute(ex_str, (key_chartype,))
    rows = cursor.fetchall()
    column_names = [column[0] for column in cursor.description]
    param_dict = {}
    for i in range(0, len(column_names)):
        param_dict[column_names[i]] = rows[0][i]
    return param_dict


def chars_get_all(cursor):
    ex_str = "SELECT * FROM characters"
    cursor.execute(ex_str)
    rows = cursor.fetchall()
    column_names = [column[0] for column in cursor.description]
    chars_list = []
    for row in rows:
        char_dict = {}
        for i in range(0, len(column_names)):
            char_dict[column_names[i]] = row[i]
        chars_list.append(char_dict)
    return chars_list


def chapters_get_all(cursor):
    ex_str = "SELECT * FROM chapters"
    cursor.execute(ex_str)
    rows = cursor.fetchall()
    column_names = [column[0] for column in cursor.description]
    chapters_list = []
    for row in rows:
        chapter_dict = {}
        for i in range(0, len(column_names)):
            chapter_dict[column_names[i]] = row[i]
        chapters_list.append(chapter_dict)
    return chapters_list


def savegames_get_all(cursor):
    ex_str = "SELECT * FROM savegames"
    cursor.execute(ex_str)
    rows = cursor.fetchall()
    column_names = [column[0] for column in cursor.description]
    savegame_list = []
    for row in rows:
        savegame_dict = {}
        for i in range(0, len(column_names)):
            savegame_dict[column_names[i]] = row[i]
        savegame_list.append(savegame_dict)
    return savegame_list


def char_save(db, char_id, hardcore_char, stage_index, stage_label, chapter_label, char_level, char_name, char_type, char_image_index, char_title=None):
    ex_str = "INSERT OR REPLACE INTO savegames (savegame_id, char_image_index, char_type, char_name, char_level, chapter_label, stage_index, char_title, char_id, stage_label, hardcore_char) VALUES ((SELECT savegame_id FROM savegames WHERE char_id=?), ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
    db.cursor.execute(ex_str, (char_id, char_image_index, char_type, char_name, char_level, chapter_label, stage_index, char_title, char_id, stage_label, hardcore_char))
    db.conn.commit()


def char_delete(db, char_id):
    ex_str = "DELETE FROM savegames WHERE char_id=?"
    db.cursor.execute(ex_str, (char_id,))
    db.conn.commit()


def char_name_get_random(cursor):
    ex_str = "SELECT * FROM names"
    cursor.execute(ex_str)
    rows = cursor.fetchall()
    rnd_index = random.randrange(0, len(rows))
    return rows[rnd_index][1]


def treasure_get_by_id(cursor, key_id):
    # base item properties query
    ex_str = "SELECT * FROM treasure WHERE treasure_id=?"
    cursor.execute(ex_str, (key_id,))
    rows = cursor.fetchall()
    column_names = [column[0] for column in cursor.description]
    treasure_dict = {}
    for i in range(0, len(column_names)):
        treasure_dict[column_names[i]] = rows[0][i]
    # item modifiers set query
    ex_str = "SELECT * FROM modifiers m JOIN treasure_modifiers_sets tms ON tms.modifier_id=m.modifier_id WHERE tms.treasure_id=?"
    cursor.execute(ex_str, (key_id,))
    rows = cursor.fetchall()
    column_names = [column[0] for column in cursor.description]
    modifiers_list = []
    for row in rows:
        mods_dict = {}
        for i in range(0, len(column_names)):
            mods_dict[column_names[i]] = row[i]
        modifiers_list.append(mods_dict)
    # item de_buff effects set query
    ex_str = "SELECT * FROM de_buffs d JOIN treasure_de_buff_sets tdbs ON tdbs.de_buff_id=d.de_buff_id WHERE tdbs.treasure_id=?"
    cursor.execute(ex_str, (key_id,))
    rows = cursor.fetchall()
    column_names = [column[0] for column in cursor.description]
    de_buffs_list = []
    for row in rows:
        de_buff_dict = {}
        for i in range(0, len(column_names)):
            de_buff_dict[column_names[i]] = row[i]
        de_buffs_list.append(de_buff_dict)
    return treasure_dict, modifiers_list, de_buffs_list


def treasure_get(cursor, lvl, roll, treasure_group=None, item_type=None, item_class=None, char_type=None, equipment_type=None, shop=None):
    ex_str = "SELECT treasure_id, roll_chance FROM treasure WHERE (lvl is Null OR lvl<=?) AND roll_chance>=?"
    if treasure_group is not None:
        itm_query = ' AND treasure_group IN (0, %s)' % treasure_group
        ex_str += itm_query
    if item_type is not None:
        itm_str = "'%s'" % "','".join(item_type)
        itm_query = ' AND item_type IN (%s)' % itm_str
        ex_str += itm_query
    if item_class is not None:
        itm_str = "'%s'" % "','".join(item_class)
        itm_query = ' AND class IN (%s)' % itm_str
        ex_str += itm_query
    if char_type is not None:
        for cht in char_type:
            try:
                char_query = ' AND %s=1' % {
                    'champion': 'usable_champion','kingslayer': 'usable_kingslayer','cosmologist': 'usable_cosmologist'
                }[cht]
                ex_str += char_query
            except KeyError:
                continue

    if equipment_type is not None:
        eq_str = "'%s'" % "','".join(equipment_type)
        eq_query = ' AND eq_type IN (%s)' % eq_str
        ex_str += eq_query
    if shop is not None:
        eq_query = ' AND shop=%s' % shop
        ex_str += eq_query
    cursor.execute(ex_str, (lvl, roll))
    rows = cursor.fetchall()
    column_names = [column[0] for column in cursor.description]
    treasure_ids = []
    for row in rows:
        tr_dict = {}
        for i in range(0, len(column_names)):
            tr_dict[column_names[i]] = row[i]
        treasure_ids.append(tr_dict)
    return treasure_ids


def de_buff_get_mods(cursor, de_buff_id):
    # de_buff modifiers query
    ex_str = "SELECT * FROM modifiers m JOIN de_buff_modifier_sets dbms ON dbms.modifier_id=m.modifier_id WHERE dbms.de_buff_id=?"
    cursor.execute(ex_str, (de_buff_id,))
    rows = cursor.fetchall()
    column_names = [column[0] for column in cursor.description]
    modifiers_list = []
    for row in rows:
        mods_dict = {}
        for i in range(0, len(column_names)):
            mods_dict[column_names[i]] = row[i]
        modifiers_list.append(mods_dict)
    return modifiers_list


def de_buff_get_by_id(cursor, de_buff_id):
    # de_buff modifiers query
    ex_str = "SELECT * FROM de_buffs WHERE de_buff_id=?"
    cursor.execute(ex_str, (de_buff_id,))
    rows = cursor.fetchall()
    column_names = [column[0] for column in cursor.description]
    de_buff_list = []
    for row in rows:
        de_buff_dict = {}
        for i in range(0, len(column_names)):
            de_buff_dict[column_names[i]] = row[i]
        de_buff_list.append(de_buff_dict)
    return de_buff_list


def de_buff_get_by_id_with_mods(cursor, de_buff_id, fate_rnd):
    deb = de_buff_get_by_id(cursor, de_buff_id)[0]
    mods = de_buff_get_mods(cursor, de_buff_id)
    deb['mods'] = {}
    for mod in mods:
        initmod.init_modifier(deb, mod, fate_rnd)
    return deb


def affix_loot_get_by_id(cursor, key_id):
    # base item properties query
    ex_str = "SELECT * FROM affixes_loot WHERE affix_id=?"
    cursor.execute(ex_str, (key_id,))
    rows = cursor.fetchall()
    column_names = [column[0] for column in cursor.description]
    affix_dict = {}
    for i in range(0, len(column_names)):
        affix_dict[column_names[i]] = rows[0][i]
    # item modifiers set query
    ex_str = "SELECT * FROM modifiers m JOIN affix_modifier_sets_loot ams ON ams.modifier_id=m.modifier_id WHERE ams.affix_id=?"
    cursor.execute(ex_str, (key_id,))
    rows = cursor.fetchall()
    column_names = [column[0] for column in cursor.description]
    modifiers_list = []
    for row in rows:
        mods_dict = {}
        for i in range(0, len(column_names)):
            mods_dict[column_names[i]] = row[i]
        modifiers_list.append(mods_dict)
    # item de_buff effects set query
    ex_str = "SELECT * FROM de_buffs d JOIN affix_de_buff_sets_loot adbs ON adbs.de_buff_id=d.de_buff_id WHERE adbs.affix_id=?"
    cursor.execute(ex_str, (key_id,))
    rows = cursor.fetchall()
    column_names = [column[0] for column in cursor.description]
    de_buffs_list = []
    for row in rows:
        de_buff_dict = debuff.DeBuff()
        for i in range(0, len(column_names)):
            de_buff_dict[column_names[i]] = row[i]
        de_buffs_list.append(de_buff_dict)
    return affix_dict, modifiers_list, de_buffs_list


def affix_mob_get_by_id(cursor, key_id):
    # base item properties query
    ex_str = "SELECT * FROM affixes_mon WHERE affix_id=?"
    cursor.execute(ex_str, (key_id,))
    rows = cursor.fetchall()
    column_names = [column[0] for column in cursor.description]
    affix_dict = {}
    for i in range(0, len(column_names)):
        affix_dict[column_names[i]] = rows[0][i]
    # item modifiers set query
    ex_str = "SELECT * FROM modifiers m JOIN affix_modifier_sets_mob ams ON ams.modifier_id=m.modifier_id WHERE ams.affix_id=?"
    cursor.execute(ex_str, (key_id,))
    rows = cursor.fetchall()
    column_names = [column[0] for column in cursor.description]
    modifiers_list = []
    for row in rows:
        mods_dict = {}
        for i in range(0, len(column_names)):
            mods_dict[column_names[i]] = row[i]
        modifiers_list.append(mods_dict)
    # item de_buff effects set query
    ex_str = "SELECT * FROM de_buffs d JOIN affix_de_buff_sets_mob adbs ON adbs.de_buff_id=d.de_buff_id WHERE adbs.affix_id=?"
    cursor.execute(ex_str, (key_id,))
    rows = cursor.fetchall()
    column_names = [column[0] for column in cursor.description]
    de_buffs_list = []
    for row in rows:
        de_buff_dict = {}
        for i in range(0, len(column_names)):
            de_buff_dict[column_names[i]] = row[i]
        de_buffs_list.append(de_buff_dict)
    return affix_dict, modifiers_list, de_buffs_list


def treasure_defaults_get(cursor, character_id):
    ex_str = "SELECT t.treasure_id FROM treasure t JOIN character_treasure_sets cts ON cts.treasure_id=t.treasure_id WHERE cts.character_id=?"
    cursor.execute(ex_str, (character_id,))
    rows = cursor.fetchall()
    treasure_list = []
    for row in rows:
        treasure_list.append(row[0])
    return treasure_list


def treasure_images_get(cursor, treasure_id, grade):
    ex_str = "SELECT treasure_grade, image_type, tileset, width, height, `index` FROM images i JOIN treasure_image_sets tis ON tis.image_id=i.image_id WHERE tis.treasure_id=? AND tis.treasure_grade=?"
    cursor.execute(ex_str, (treasure_id, grade))
    rows = cursor.fetchall()
    column_names = [column[0] for column in cursor.description]
    images_dict = {}
    for row in rows:
        image_dict = {}
        for i in range(2, len(column_names)):
            image_dict[column_names[i]] = row[i]
        images_dict[row[1]] = image_dict
    return images_dict


def treasure_sounds_get(cursor, treasure_id, grade):
    ex_str = "SELECT sound_type, sound_name FROM sounds s JOIN treasure_sound_sets tss ON tss.sound_id=s.sound_id WHERE tss.treasure_id=? AND (tss.treasure_grade is Null OR tss.treasure_grade=?)"
    cursor.execute(ex_str, (treasure_id, grade))
    rows = cursor.fetchall()
    sounds_dict = {}
    for row in rows:
        sounds_dict[row[0]] = row[1]
    return sounds_dict


def get_affixes_loot(cursor, max_level, max_grade, item_types, roll, is_suffix=None):
    ex_str = "SELECT affix_id FROM affixes_loot WHERE lvl<=? AND item_grade<=? AND roll_chance>=?"
    for t in item_types:
        ex_str += ' AND %s=1' % t
    bindings = [max_level, max_grade, roll]
    if is_suffix is not None:
        ex_str += ' AND suffix=?'
        bindings.append(is_suffix)
    cursor.execute(ex_str, bindings)
    rows = cursor.fetchall()
    affix_ids = []
    for row in rows:
        affix_ids.append(row[0])
    return affix_ids


def get_affixes_mob(cursor, max_level, max_grade, mob_type, roll, is_suffix=None):
    ex_str = ("SELECT affix_id FROM affixes_mon WHERE lvl<=? AND monster_grade<=? "
              "AND roll_chance>=? AND (monster_type is Null OR monster_type=?)")
    bindings = [max_level, max_grade, roll, mob_type]
    if is_suffix is not None:
        ex_str += ' AND suffix=?'
        bindings.append(is_suffix)
    cursor.execute(ex_str, bindings)
    rows = cursor.fetchall()
    affix_ids = []
    for row in rows:
        affix_ids.append(row[0])
    return affix_ids


def monster_get_by_id(cursor, monster_id):
    ex_str = "SELECT * FROM monsters WHERE monster_id=?"
    cursor.execute(ex_str, (monster_id,))
    rows = cursor.fetchall()
    column_names = [column[0] for column in cursor.description]
    monster_dict = {}
    for i in range(0, len(column_names)):
        monster_dict[column_names[i]] = rows[0][i]
    ex_str = "SELECT sound_type, sound_name FROM sounds s JOIN monster_sound_sets mss ON mss.sound_id=s.sound_id WHERE mss.monster_id=?"
    cursor.execute(ex_str, (monster_id, ))
    rows = cursor.fetchall()
    for row in rows:
        monster_dict[row[0]] = row[1]
    # Monster attacks query
    ex_str = "SELECT ma.attack_id, label, range, attack_type, attack_val_base, attack_val_spread, monster_type, lvl, time, chance, sound_attack, blast_radius, sound_blast, projectile_speed, projectile_collision_limit FROM monster_attack_sets mas JOIN monster_attacks ma ON mas.attack_id=ma.attack_id WHERE mas.monster_id=?"
    cursor.execute(ex_str, (monster_id,))
    rows = cursor.fetchall()
    column_names = [column[0] for column in cursor.description]
    ranged_attacks_list = []
    melee_attacks_list = []
    for row in rows:
        attack_dict = {}
        for i in range(0, len(column_names)):
            attack_dict[column_names[i]] = row[i]
        if attack_dict['range'] > 0:
            ranged_attacks_list.append(attack_dict)
        else:
            melee_attacks_list.append(attack_dict)
    monster_dict['attacks_ranged'] = ranged_attacks_list
    monster_dict['attacks_melee'] = melee_attacks_list
    for at in (monster_dict['attacks_melee'], monster_dict['attacks_ranged']):
        for att in at:
            # monster de_buff effects set query
            ex_str = "SELECT * FROM de_buffs d JOIN monster_debuff_sets mdbs ON mdbs.de_buff_id=d.de_buff_id WHERE mdbs.attack_id=?"
            cursor.execute(ex_str, (att['attack_id'],))
            rows = cursor.fetchall()
            column_names = [column[0] for column in cursor.description]
            de_buffs_list = []
            for row in rows:
                de_buff_dict = debuff.DeBuff()
                for i in range(0, len(column_names)):
                    de_buff_dict[column_names[i]] = row[i]
                de_buffs_list.append(de_buff_dict)
            att['de_buffs'] = de_buffs_list
    return monster_dict


def affixed_attack_get(cursor, affix_id):
    ex_str = "SELECT ma.attack_id, label, range, attack_type, attack_val_base, attack_val_spread, monster_type, lvl, time, chance, sound_attack, blast_radius, sound_blast, projectile_speed, projectile_collision_limit FROM affixed_attack_sets aas JOIN monster_attacks ma ON aas.attack_id=ma.attack_id WHERE aas.affix_id=?"
    cursor.execute(ex_str, (affix_id,))
    rows = cursor.fetchall()
    column_names = [column[0] for column in cursor.description]
    ranged_attacks_list = []
    melee_attacks_list = []
    for row in rows:
        attack_dict = {}
        for i in range(0, len(column_names)):
            attack_dict[column_names[i]] = row[i]
        if attack_dict['range'] > 0:
            ranged_attacks_list.append(attack_dict)
        else:
            melee_attacks_list.append(attack_dict)
    for at in (ranged_attacks_list, melee_attacks_list):
        for att in at:
            # monster de_buff effects set query
            ex_str = "SELECT * FROM de_buffs d JOIN monster_debuff_sets mdbs ON mdbs.de_buff_id=d.de_buff_id WHERE mdbs.attack_id=?"
            cursor.execute(ex_str, (att['attack_id'],))
            rows = cursor.fetchall()
            column_names = [column[0] for column in cursor.description]
            de_buffs_list = []
            for row in rows:
                de_buff_dict = {}
                for i in range(0, len(column_names)):
                    de_buff_dict[column_names[i]] = row[i]
                de_buffs_list.append(de_buff_dict)
            att['de_buffs'] = de_buffs_list
    return melee_attacks_list, ranged_attacks_list


def get_monsters(cursor, max_level, max_grade, monster_types, roll):
    ex_str = "SELECT monster_id FROM monsters WHERE lvl<=? AND roll_chance>=?"
    if monster_types is not None:
        mon_str = ','.join(monster_types)
        mon_query = ' AND monster_type IN (%s)' % mon_str
        ex_str += mon_query
    bindings = [max_level, roll]
    cursor.execute(ex_str, bindings)
    rows = cursor.fetchall()
    monster_ids = []
    for row in rows:
        monster_ids.append(row[0])
    return monster_ids


def skill_get_by_id(cursor, skill_id):
    ex_str = "SELECT * FROM skills WHERE skill_id=?"
    cursor.execute(ex_str, (skill_id,))
    rows = cursor.fetchall()
    column_names = [column[0] for column in cursor.description]
    skill_dict = {}
    for i in range(0, len(column_names)):
        skill_dict[column_names[i]] = rows[0][i]
    return skill_dict


def skill_defaults_get(cursor, character_id):
    ex_str = "SELECT s.skill_id FROM skills s JOIN character_skill_sets css ON css.skill_id=s.skill_id WHERE css.character_id=?"
    cursor.execute(ex_str, (character_id,))
    rows = cursor.fetchall()
    skill_list = []
    for row in rows:
        skill_list.append(row[0])
    return skill_list


def skill_images_get(cursor, skill_id, grade):
    ex_str = "SELECT skill_grade, image_type, tileset, width, height, `index` FROM images i JOIN skill_image_sets sis ON sis.image_id=i.image_id WHERE sis.skill_id=? AND sis.skill_grade=?"
    cursor.execute(ex_str, (skill_id, grade))
    rows = cursor.fetchall()
    column_names = [column[0] for column in cursor.description]
    images_dict = {}
    for row in rows:
        image_dict = {}
        for i in range(2, len(column_names)):
            image_dict[column_names[i]] = row[i]
        images_dict[row[1]] = image_dict
    return images_dict


def skill_sounds_get(cursor, skill_id, grade):
    ex_str = "SELECT sound_type, sound_name FROM sounds s JOIN skill_sound_sets sss ON sss.sound_id=s.sound_id WHERE sss.skill_id=? AND sss.skill_grade=?"
    cursor.execute(ex_str, (skill_id, grade))
    rows = cursor.fetchall()
    sounds_dict = {}
    for row in rows:
        sounds_dict[row[0]] = row[1]
    return sounds_dict


def grade_set_get(cursor, set_id, lvl):
    ex_str = "SELECT * FROM grade_sets gs JOIN grades g ON gs.grade_id=g.grade_id WHERE set_id=? AND lvl<=?"
    cursor.execute(ex_str, (set_id, lvl))
    rows = cursor.fetchall()
    column_names = [column[0] for column in cursor.description]
    grades_list = []
    for row in rows:
        grade_dict = {}
        for i in range(0, len(column_names)):
            grade_dict[column_names[i]] = row[i]
        grades_list.append(grade_dict)
    return grades_list


def grade_get_by_id(cursor, grade_id):
    ex_str = "SELECT * FROM grades WHERE grade_id=?"
    cursor.execute(ex_str, (grade_id,))
    rows = cursor.fetchall()
    column_names = [column[0] for column in cursor.description]
    grade_dict = {}
    for i in range(0, len(column_names)):
        grade_dict[column_names[i]] = rows[0][i]
    return grade_dict


def chapter_get_by_id(cursor, chapter_id):
    ex_str = "SELECT * FROM chapters c WHERE chapter_id=?"
    cursor.execute(ex_str, (chapter_id,))
    rows = cursor.fetchall()
    column_names = [column[0] for column in cursor.description]
    chapter_dict = {}
    for i in range(0, len(column_names)):
        chapter_dict[column_names[i]] = rows[0][i]
    return chapter_dict


def stage_get(cursor, chapter_id, stage_index, roll):
    ex_str = "SELECT * FROM stages s JOIN chapter_stage_sets css ON css.stage_id=s.stage_id WHERE css.chapter_id=? AND css.stage_index=? AND css.roll_chance>=?"
    cursor.execute(ex_str, (chapter_id, stage_index, roll))
    rows = cursor.fetchall()
    column_names = [column[0] for column in cursor.description]
    stages_list = []
    for row in rows:
        stage_dict = {}
        for i in range(0, len(column_names)):
            stage_dict[column_names[i]] = row[i]
        stages_list.append(stage_dict)
    for stage in stages_list:
        ex_str = "SELECT m.monster_id, sms.roll_chance FROM monsters m JOIN stage_monster_sets sms ON sms.monster_id=m.monster_id WHERE sms.stage_id=?"
        cursor.execute(ex_str, (stage['stage_id'],))
        rows = cursor.fetchall()
        monster_list = []
        for row in rows:
            monster_list.append((row[0], row[1]))
        stage['monsters'] = monster_list
    return stages_list


def chapter_progress_get(cursor, char_id, stage_index=None):
    ex_str = "SELECT * FROM character_chapter_progress ccp WHERE ccp.char_id=?"
    bindings = [char_id]
    if stage_index is not None:
        ex_str += " AND stage_index=?"
        bindings.append(stage_index)
    cursor.execute(ex_str, bindings)
    rows = cursor.fetchall()
    column_names = [column[0] for column in cursor.description]
    progress_list = []
    for row in rows:
        stage_progress_dict = {}
        for i in range(0, len(column_names)):
            stage_progress_dict[column_names[i]] = row[i]
        progress_list.append(stage_progress_dict)
    return progress_list


def chapter_progress_set(db, char_id, stage_index, maze, mobs, obj, doors, traps, exits):
    ex_str = "INSERT OR REPLACE INTO character_chapter_progress (progress_id, char_id, stage_index, maze_rolled, monsters_rolled, objects_rolled, doors_rolled, traps_rolled, exits_rolled) VALUES ((SELECT progress_id FROM character_chapter_progress WHERE char_id=? AND stage_index=?), ?, ?, ?, ?, ?, ?, ?, ?)"
    db.cursor.execute(ex_str, (char_id, stage_index, char_id, stage_index, maze, mobs, obj, doors, traps, exits))
    db.conn.commit()


def chapter_progress_reset(db, char_id, stage_index=None):
    ex_str = "DELETE FROM character_chapter_progress WHERE char_id=?"
    bindings = [char_id]
    if stage_index is not None:
        ex_str += " AND stage_index=?"
        bindings.append(stage_index)
    db.cursor.execute(ex_str, bindings)
    db.conn.commit()


def chapter_demo_get(cursor, chapter_id, demo_tag):
    # Demo get query
    ex_str = "SELECT * FROM demo_text WHERE chapter_id=? AND demo_tag=?"
    cursor.execute(ex_str, (chapter_id, demo_tag))
    rows = cursor.fetchall()
    column_names = [column[0] for column in cursor.description]
    demo_text_list = []
    for row in rows:
        text_dict = {}
        for i in range(0, len(column_names)):
            text_dict[column_names[i]] = row[i]
        demo_text_list.append(text_dict)
    ex_str = "SELECT * FROM demo_images WHERE chapter_id=? AND demo_tag=?"
    cursor.execute(ex_str, (chapter_id, demo_tag))
    rows = cursor.fetchall()
    column_names = [column[0] for column in cursor.description]
    demo_image_list = []
    for row in rows:
        image_dict = {}
        for i in range(0, len(column_names)):
            image_dict[column_names[i]] = row[i]
        demo_image_list.append(image_dict)
    # Retrieving images by ids
    for img in demo_image_list:
        ex_str = "SELECT * FROM images WHERE image_id=?"
        cursor.execute(ex_str, (img['image_id'],))
        rows = cursor.fetchall()
        column_names = [column[0] for column in cursor.description]
        image_dict = {}
        for i in range(0, len(column_names)):
            image_dict[column_names[i]] = rows[0][i]
        img['image'] = image_dict
        del img['image_id']
    return demo_text_list, demo_image_list


def images_get_by_id(cursor, image_ids):
    insertion = ','.join([str(i) for i in image_ids if isinstance(i, int)])
    ex_str = "SELECT * FROM images WHERE image_id in (%s)" % insertion
    cursor.execute(ex_str)
    rows = cursor.fetchall()
    column_names = [column[0] for column in cursor.description]
    image_list = []
    for row in rows:
        image_dict = {}
        for i in range(0, len(column_names)):
            image_dict[column_names[i]] = row[i]
        image_list.append(image_dict)
    return image_list


def manuscript_get(cursor, tag_list, level, rnd_roll):
    insertion = ','.join(['"%s"' % i for i in tag_list if i.isalpha()])
    ex_str = "SELECT * FROM manuscripts WHERE lvl<=? AND roll_chance>=? AND tag in (%s)" % insertion
    cursor.execute(ex_str, (level, rnd_roll))
    rows = cursor.fetchall()
    column_names = [column[0] for column in cursor.description]
    man_list = []
    for row in rows:
        man_dict = {}
        for i in range(0, len(column_names)):
            man_dict[column_names[i]] = row[i]
        man_list.append(man_dict)
    return man_list


def manuscript_get_by_id(cursor, man_id):
    ex_str = "SELECT * FROM manuscripts WHERE manuscript_id=?"
    cursor.execute(ex_str, (man_id,))
    rows = cursor.fetchall()
    column_names = [column[0] for column in cursor.description]
    man_dict = {}
    for i in range(0, len(column_names)):
        man_dict[column_names[i]] = rows[0][i]
    return man_dict


def mission_get(cursor, level, chapter_id, stage_index, char_type, mission_id=None):
    if mission_id is not None:
        ex_str = "SELECT * FROM missions WHERE mission_id=?"
        cursor.execute(ex_str, (mission_id,))
    else:
        ex_str = "SELECT * FROM missions WHERE lvl<=? AND chapter_id in (?, 0) AND %s=1 AND stage_index<=?" % (char_type,)
        cursor.execute(ex_str, (level, chapter_id, stage_index))
    rows = cursor.fetchall()
    column_names = [column[0] for column in cursor.description]
    mission_list = []
    for row in rows:
        mission_dict = {}
        for i in range(0, len(column_names)):
            mission_dict[column_names[i]] = row[i]

        ex_str = "SELECT treasure_id, amount FROM mission_task_sets WHERE mission_id=?"
        cursor.execute(ex_str, (mission_dict['mission_id'],))
        tr_rows = cursor.fetchall()
        mission_dict['tasks'] = tuple([tr for tr in tr_rows])

        ex_str = "SELECT mission_req_id FROM mission_req_sets WHERE mission_id=?"
        cursor.execute(ex_str, (mission_dict['mission_id'],))
        tr_rows = cursor.fetchall()
        mission_dict['reqs'] = tuple([tr[0] for tr in tr_rows])

        ex_str = "SELECT treasure_id, amount FROM mission_reward_sets WHERE mission_id=?"
        cursor.execute(ex_str, (mission_dict['mission_id'],))
        tr_rows = cursor.fetchall()
        mission_dict['non_rnd_reward'] = tuple([tr for tr in tr_rows])

        mission_list.append(mission_dict)
    return mission_list


def mission_tasks_get(cursor, treasure_ids):
    ex_str = (
        "SELECT t.treasure_id, t.label, tileset, width, height, `index` FROM images i JOIN treasure_image_sets tis "
        "ON tis.image_id=i.image_id JOIN treasure t ON tis.treasure_id=t.treasure_id "
        "WHERE tis.treasure_id IN (%s) AND tis.image_type=0 AND tis.treasure_grade=0" % ','.join([str(tr_id) for tr_id in treasure_ids])
    )
    cursor.execute(ex_str)
    rows = cursor.fetchall()
    column_names = [column[0] for column in cursor.description]
    task_list = []
    for row in rows:
        task_dict = {}
        for i in range(0, len(column_names)):
            task_dict[column_names[i]] = row[i]
        task_list.append(task_dict)
    return task_list


def get_recipe_ingredients(cursor, recipe_id):
    ex_str = "SELECT * FROM crafting_ingredient_sets WHERE recipe_treasure_id=?"
    cursor.execute(ex_str, (recipe_id,))
    rows = cursor.fetchall()
    column_names = [column[0] for column in cursor.description]
    ingredient_list = []
    for row in rows:
        ingredient_dict = {}
        for i in range(0, len(column_names)):
            ingredient_dict[column_names[i]] = row[i]
        ingredient_list.append(ingredient_dict)
    return ingredient_list


def get_recipe_result(cursor, recipe_id):
    ex_str = "SELECT result_treasure_id FROM crafting_result_sets WHERE recipe_treasure_id=?"
    cursor.execute(ex_str, (recipe_id,))
    rows = cursor.fetchall()
    result_list = []
    for row in rows:
        result_list.append(row[0])
    return result_list
