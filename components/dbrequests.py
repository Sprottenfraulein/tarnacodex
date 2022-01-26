from components import debuff


def trap_params_get(cursor, table_name, key_level):
    ex_str = "SELECT label, range, attack_type, attack_val_base, attack_val_spread, lvl FROM %s WHERE monster_type='mt_trap' AND lvl<=?" % (table_name,)
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
        de_buff_dict = debuff.DeBuff()
        for i in range(0, len(column_names)):
            de_buff_dict[column_names[i]] = row[i]
        de_buffs_list.append(de_buff_dict)
    return treasure_dict, modifiers_list, de_buffs_list


def treasure_get(cursor, lvl, treasure_group, roll, item_type=None, char_type=None, equipment_type=None):
    ex_str = "SELECT treasure_id FROM treasure WHERE lvl<=? AND treasure_group=? AND roll_chance>=?"
    if item_type is not None:
        itm_str = ','.join(item_type)
        itm_query = ' AND item_type IN (%s)' % itm_str
        ex_str += itm_query
    if char_type is not None:
        char_str = ','.join(char_type)
        char_query = ' AND char_type IN (%s)' % char_str
        ex_str += char_query
    if equipment_type is not None:
        eq_str = ','.join(equipment_type)
        eq_query = ' AND eq_type IN (%s)' % eq_str
        ex_str += eq_query
    cursor.execute(ex_str, (lvl, treasure_group, roll))
    rows = cursor.fetchall()
    treasure_ids = []
    for row in rows:
        treasure_ids.append(row[0])
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
    ex_str = "SELECT * FROM modifiers m JOIN affix_modifier_sets ams ON ams.modifier_id=m.modifier_id WHERE ams.affix_id=?"
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
    ex_str = "SELECT * FROM de_buffs d JOIN affix_de_buff_sets adbs ON adbs.de_buff_id=d.de_buff_id WHERE adbs.affix_id=?"
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
    ex_str = "SELECT treasure_grade, filename FROM sounds s JOIN treasure_sound_sets tss ON tss.sound_id=s.sound_id WHERE tss.treasure_id=? AND tss.treasure_grade=?"
    cursor.execute(ex_str, (treasure_id, grade))
    rows = cursor.fetchall()
    column_names = [column[0] for column in cursor.description]
    sounds_dict = {}
    s_ind = 0
    for row in rows:
        sound_dict = {}
        sound_dict[column_names[1]] = row[1]
        sounds_dict[row[0]] = sound_dict
        s_ind += 1
    return sounds_dict


def get_affixes(cursor, max_level, max_grade, item_types, roll, is_suffix=None):
    ex_str = "SELECT affix_id FROM affixes_loot WHERE affix_level<=? AND item_grade<=? AND roll_chance>=?"
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


def monster_get_by_id(cursor, monster_id):
    ex_str = "SELECT * FROM monsters WHERE monster_id=?"
    cursor.execute(ex_str, (monster_id,))
    rows = cursor.fetchall()
    column_names = [column[0] for column in cursor.description]
    monster_dict = {}
    for i in range(0, len(column_names)):
        monster_dict[column_names[i]] = rows[0][i]
        # item modifiers set query
    ex_str = "SELECT ma.attack_id, label, range, attack_type, attack_val_base, attack_val_spread, monster_type, lvl FROM monster_attack_sets mas JOIN monster_attacks ma ON mas.attack_id=ma.attack_id WHERE mas.monster_id=?"
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
    return monster_dict


def get_monsters(cursor, max_level, max_grade, monster_types, roll):
    ex_str = "SELECT monster_id FROM monsters WHERE lvl<=? AND grade<=? AND roll_chance>=?"
    if monster_types is not None:
        mon_str = ','.join(monster_types)
        mon_query = ' AND monster_type IN (%s)' % mon_str
        ex_str += mon_query
    bindings = [max_level, max_grade, roll]
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
    ex_str = "SELECT skill_grade, filename FROM sounds s JOIN skill_sound_sets sss ON sss.sound_id=s.sound_id WHERE sss.skill_id=? AND sss.skill_grade=?"
    cursor.execute(ex_str, (skill_id, grade))
    rows = cursor.fetchall()
    column_names = [column[0] for column in cursor.description]
    sounds_dict = {}
    s_ind = 0
    for row in rows:
        sound_dict = {}
        sound_dict[column_names[1]] = row[1]
        sounds_dict[row[0]] = sound_dict
        s_ind += 1
    return sounds_dict