from components import dbrequests


def create(de_buffs, win, xy, icon_size, num_per_row):
    de_buff_list = []
    x, y = xy
    icon_w, icon_h = icon_size
    db_image_ids = [d['image_id'] for d in de_buffs]
    for i in range(0, len(de_buffs)):
        de_buff = de_buffs[i]
        db_x = x + icon_w * (i % num_per_row)
        db_y = y + icon_h * (i // num_per_row)
        db_image_list = dbrequests.images_get_by_id(win.db.cursor, (db_image_ids[i],))[0]
        db_image = win.tilesets.get_image(db_image_list['tileset'],
                                          (db_image_list['width'], db_image_list['height']),
                                          (db_image_list['index'],))[0]
        db_panel = win.win_ui.panel_add(i, (db_x, db_y), icon_size,
                                           images=(db_image,), page=None, img_stretch=True,
                                           tags=(de_buff, 'de_buff'), win=win)
        de_buff_list.append(db_panel)
    return de_buff_list
