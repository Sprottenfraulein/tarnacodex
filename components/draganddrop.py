def item_move(win, element, mb_event, m_bttn, in_realm, skillfuncs):
    if m_bttn == 3 and in_realm:
        if element.id < len(element.tags[0]) and element.tags[0][element.id] is not None:
            if 'skill_id' in element.tags[0][element.id].props:
                getattr(skillfuncs, element.tags[0][element.id].props['function_name'])(
                    win.wins_dict, win.resources.fate_rnd, win.pc, element.tags[0][element.id],
                    (element.tags[0], element.id), True)
            elif 'treasure_id' in element.tags[0][element.id].props and element.tags[0][element.id].props[
                'use_skill'] is not None:
                getattr(skillfuncs, element.tags[0][element.id].props['use_skill'].props['function_name'])(
                    win.wins_dict, win.resources.fate_rnd, win.pc, element.tags[0][element.id].props['use_skill'],
                    (element.tags[0], element.id), True)
    elif m_bttn == 1:
        if win.wins_dict['context'] in win.active_wins:
            win.active_wins.remove(win.wins_dict['context'])
        item_info = [element.tags[0], element.id]
        if mb_event == 'down' and win.mouse_pointer.drag_item is None:
            if item_info[0][item_info[1]] is not None:
                win.mouse_pointer.drag_item = item_info
                # exchange between inventory socket and mouse

                item_down = win.mouse_pointer.drag_item[0][win.mouse_pointer.drag_item[1]]
                win.mouse_pointer.image = item_down.props['image_inventory'][0]
                win.pygame_settings.audio.sound('item_drag')
        elif mb_event == 'up' and win.mouse_pointer.drag_item is not None:
            item_dragging = win.mouse_pointer.drag_item[0][win.mouse_pointer.drag_item[1]]
            if win.wins_dict['realm'].maze is not None and win.mouse_pointer.drag_item[0] == win.wins_dict[
                'realm'].maze.loot:
                win.mouse_pointer.catcher[0] = item_dragging
                win.mouse_pointer.drag_item = [win.mouse_pointer.catcher, 0]
                win.wins_dict['realm'].maze.loot.remove(item_dragging)
            if item_info[0][item_info[1]] is None:
                item_info[0][item_info[1]], win.mouse_pointer.drag_item[0][win.mouse_pointer.drag_item[1]] = \
                    win.mouse_pointer.drag_item[0][win.mouse_pointer.drag_item[1]], item_info[0][item_info[1]]
            else:
                item_info[0][item_info[1]], win.mouse_pointer.drag_item[0][win.mouse_pointer.drag_item[1]] = \
                    win.mouse_pointer.drag_item[0][win.mouse_pointer.drag_item[1]], item_info[0][item_info[1]]

            if (
                    item_info[0][item_info[1]].props['item_type'] not in item_info[0].filters['item_types']
                    or (win.mouse_pointer.drag_item[0][win.mouse_pointer.drag_item[1]] is not None
                        and win.mouse_pointer.drag_item[0][win.mouse_pointer.drag_item[1]].props['item_type']
                        not in win.mouse_pointer.drag_item[0].filters['item_types'])
            ):
                item_info[0][item_info[1]], win.mouse_pointer.drag_item[0][win.mouse_pointer.drag_item[1]] = \
                    win.mouse_pointer.drag_item[0][win.mouse_pointer.drag_item[1]], item_info[0][item_info[1]]
                win.wins_dict['dialogue'].dialogue_elements = {
                    'header': 'Attention',
                    'text': "The item won't fit for that socket!",
                    'bttn_cancel': 'OK'
                }
                win.wins_dict['dialogue'].launch(win.pc)
            elif (
                    item_info[0] in win.pc.char_sheet.equipped
                    and item_info[0][item_info[1]].props['usable_%s' % win.pc.char_sheet.type] == 0
                    or (win.mouse_pointer.drag_item[0][win.mouse_pointer.drag_item[1]] is not None
                        and win.mouse_pointer.drag_item[0] in win.pc.char_sheet.equipped
                        and win.mouse_pointer.drag_item[0][win.mouse_pointer.drag_item[1]].props[
                            'usable_%s' % win.pc.char_sheet.type] == 0)
            ):
                item_info[0][item_info[1]], win.mouse_pointer.drag_item[0][win.mouse_pointer.drag_item[1]] = \
                    win.mouse_pointer.drag_item[0][win.mouse_pointer.drag_item[1]], item_info[0][item_info[1]]
                win.wins_dict['dialogue'].dialogue_elements = {
                    'header': 'Attention',
                    'text': "%s can not use this type of item!" % win.pc.char_sheet.name.capitalize(),
                    'bttn_cancel': 'OK'
                }
                win.wins_dict['dialogue'].launch(win.pc)
            elif (
                    item_info[0] in win.pc.char_sheet.equipped
                    and item_info[0][item_info[1]].props['lvl'] > win.pc.char_sheet.level
                    or (win.mouse_pointer.drag_item[0][win.mouse_pointer.drag_item[1]] is not None
                        and win.mouse_pointer.drag_item[0] in win.pc.char_sheet.equipped
                        and win.mouse_pointer.drag_item[0][win.mouse_pointer.drag_item[1]].props[
                            'lvl'] > win.pc.char_sheet.level)
            ):
                item_info[0][item_info[1]], win.mouse_pointer.drag_item[0][win.mouse_pointer.drag_item[1]] = \
                    win.mouse_pointer.drag_item[0][win.mouse_pointer.drag_item[1]], item_info[0][item_info[1]]
                win.wins_dict['dialogue'].dialogue_elements = {
                    'header': 'Attention',
                    'text': "%s is not experienced enough to use this item!" % win.pc.char_sheet.name.capitalize(),
                    'bttn_cancel': 'OK'
                }
                win.wins_dict['dialogue'].launch(win.pc)
            else:
                win.pc.moved_item_cooldown_check(item_info[0][item_info[1]], element)
                win.pygame_settings.audio.sound(item_info[0][item_info[1]].props['sound_pickup'])

            if win.mouse_pointer.catcher[0] is not None:
                win.mouse_pointer.drag_item = [win.mouse_pointer.catcher, 0]
                win.mouse_pointer.image = \
                    win.mouse_pointer.drag_item[0][win.mouse_pointer.drag_item[1]].props['image_inventory'][0]
            else:
                win.mouse_pointer.drag_item = None
                win.mouse_pointer.image = None

            win.pc.char_sheet.itemlists_clean_tail()

            win.pc.char_sheet.calc_stats()
            if in_realm:
                win.wins_dict['realm'].calc_vision_alt()
            win.wins_dict['charstats'].updated = True
        win.render_slots()
