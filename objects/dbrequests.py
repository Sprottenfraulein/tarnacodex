def trap_params_get(cursor, table_name, key_level):
    ex_str = "SELECT label, range, dam_typ, dam_val_base, dam_val_spread, lvl FROM %s WHERE mon_type='mt_trap' AND lvl<=?" % (table_name,)
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