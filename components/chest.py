from components import lootgen, dbrequests, treasure, textinserts
from library import particle, pickrandom
import random


class Chest:
    def __init__(self, x_sq, y_sq, alignment, room, tileset, off_x=0, off_y=0, lvl=None, items_number=0, gp_number=0,
                 treasure_group=None, item_type=None, char_type=None, container=None, disappear=False):
        self.x_sq = x_sq
        self.y_sq = y_sq
        self.off_x = off_x
        self.off_y = off_y
        self.alignment = alignment
        self.room = room
        self.tileset = tileset
        self.lock = None
        self.trap = None
        self.closed = True
        self.image = None
        self.image_update()

        self.lvl = lvl
        self.items_number = items_number
        self.gp_number = gp_number
        self.treasure_group = treasure_group
        self.item_type = item_type
        self.char_type = char_type

        self.container = container
        self.disappear = disappear

    def image_update(self):
        if self.alignment:
            align = 'ver'
            """self.off_x = 0
            self.off_y = 0"""
        else:
            align = 'hor'
            """self.off_x = 0
            self.off_y = 0"""
        if self.lock is not None:
            if self.lock.magical:
                pos = 'mlock'
            else:
                pos = 'lock'
        elif self.closed:
            pos = 'shut'
        else:
            pos = 'open'
        image_name = 'chest_%s_%s' % (align, pos)
        self.image = self.tileset[image_name]

    def use(self, wins_dict, active_wins, pc):
        if not self.closed:
            self.closed = True
            self.image_update()
            wins_dict['realm'].sound_inrealm('chest_shut', self.x_sq, self.y_sq)
            return True
        elif self.trap is not None and self.trap.mode == 1:
            if self.trap.visible == 1:
                wins_dict['dialogue'].dialogue_elements = {
                    'header': 'Trap caution',
                    'text': "You are going to trigger the trap! $n Continue?",
                    'bttn_cancel': 'NO',
                    'bttn_ok': 'YES'
                }
                wins_dict['dialogue'].delayed_action['bttn_ok'] = (self.trap, 'trigger', (wins_dict, pc))
                wins_dict['dialogue'].launch(pc)
            elif not self.trap.detect(wins_dict, pc) and self.trap.mode == 1:
                self.trap.trigger(wins_dict, pc)
            return True
        elif self.lock is None:
            self.closed = False
            self.container_unpack(wins_dict, active_wins, pc)
            self.image_update()
            wins_dict['realm'].sound_inrealm('chest_open', self.x_sq, self.y_sq)
            return True
        elif self.lock.unlock(wins_dict, pc):
            self.lock = None
            self.image_update()
            return True
        return False

    def container_unpack(self, wins_dict, active_wins, pc):
        realm = wins_dict['realm']
        if self.gp_number > 0:
            if self.container is None:
                self.container = []
            goods_level_cap = self.lvl or pc.char_sheet.level
            for i in range(0, self.gp_number):
                new_gold = treasure.Treasure(6, goods_level_cap, realm.db.cursor, realm.tilesets, realm.resources,
                                             realm.pygame_settings.audio, realm.resources.fate_rnd)
                amount = new_gold.props['amount']
                new_gold.props['amount'] = round(amount * (treasure.SCALE_RATE_GOLD * (goods_level_cap * (goods_level_cap + 1) / 2)))
                if new_gold.props['amount'] >= 10000:
                    new_gold.props['grade'] = {'grade_level': 3}
                elif new_gold.props['amount'] >= 1000:
                    new_gold.props['grade'] = {'grade_level': 2}
                elif new_gold.props['amount'] >= 100:
                    new_gold.props['grade'] = {'grade_level': 1}
                else:
                    new_gold.props['grade'] = {'grade_level': 0}
                treasure.images_update(realm.db.cursor, new_gold.props, realm.tilesets)
                treasure.sounds_update(realm.db.cursor, new_gold.props)
                self.container.append(new_gold)
            self.gp_number = 0
        if self.items_number > 0:
            if self.container is None:
                self.container = []
            goods_level_cap = self.lvl or pc.char_sheet.level
            rnd_roll = random.randrange(1, 10001)
            tr_ids_list = [(tr['treasure_id'], tr['roll_chance']) for tr in
                           dbrequests.treasure_get(realm.db.cursor, goods_level_cap,
                           self.treasure_group, rnd_roll, item_type=self.item_type,
                           char_type=self.char_type)]
            good_ids = pickrandom.items_get(tr_ids_list, self.items_number, items_pop=True)
            for rnd_id in good_ids:
                new_tr = treasure.Treasure(rnd_id, goods_level_cap, realm.db.cursor, realm.tilesets,
                                                        realm.resources, realm.pygame_settings.audio,
                                                        realm.resources.fate_rnd,
                                                        findmagic=pc.char_sheet.profs['prof_findmagic'])
                self.container.append(new_tr)
                # SPECIAL MANUSCRIPT STATEMENT
                if new_tr.props['item_type'] == 'misc_man':  # Manuscript item treasure_id
                    rnd_roll = random.randrange(1, 10001)
                    mans_list = [
                        (mn, mn['roll_chance'])
                        for mn in
                        dbrequests.manuscript_get(realm.db.cursor, (new_tr.props['class'],), new_tr.props['lvl'],
                                                  rnd_roll)
                    ]
                    if len(mans_list) == 0:
                        del self.container[-1]
                    else:
                        new_tr.props['desc'] = textinserts.insert(realm, pc,
                                                                  pickrandom.items_get(mans_list, 1)[0]['desc'])
            self.items_number = 0
        if self.container is not None and len(self.container) > 0:
            lootgen.drop_loot(self.x_sq, self.y_sq, realm, self.container)
            self.container.clear()
        if self.disappear:
            realm.maze.chests.remove(self)
            realm.maze.flag_array[self.y_sq][self.x_sq].obj = None
            realm.maze.flag_array[self.y_sq][self.x_sq].mov = True
            realm.particle_list.append(particle.Particle(
                (self.x_sq, self.y_sq), (self.off_x, self.off_y),
                realm.animations.get_animation('effect_dust_cloud')['default'], 16
            ))
