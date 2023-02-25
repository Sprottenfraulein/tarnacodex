# APPLICATION SETTINGS.

# System settings
# Application resolution.
APP_RES = (1600, 900)
# APP_RES = (1680, 1050)
app_scale = 2
# Application caption (visible in window title or OS apps manager)
APP_CAPTION = 'TARNA CODEX'
tag_string = 'TARNA CODEX, pre-alpha build. © Senya Tarna, 2022.'
# Frames per second (changing this affects app's run speed)
FPS = 60

# Game settings
tilesets = (
    ('default', 'res/tilesets/default01.png'),
    ('red_glass', 'res/tilesets/texture01.png'),
    ('black_rock', 'res/tilesets/texture02.png'),
    ('paper', 'res/tilesets/texture03.png'),

    ('dung_bricks', 'res/tilesets/dung_bricks.png'),
    ('dung_cave', 'res/tilesets/dung_cave.png'),
    ('dark_bricks', 'res/tilesets/dark_bricks.png'),

    ('dung_doors', 'res/tilesets/dung_doors.png'),
    ('dung_chests', 'res/tilesets/dung_chests.png'),
    ('dark_edges', 'res/tilesets/darkedges.png'),
    ('interface', 'res/tilesets/interface.png'),
    ('inv_items', 'res/tilesets/inv_items.png'),
    ('floor_items', 'res/tilesets/floor_items.png'),
    ('inv_skills', 'res/tilesets/inv_skills.png'),
    ('de_buffs', 'res/tilesets/de_buffs.png'),

    ('pools', 'res/tilesets/pools.png'),
    ('char_portraits', 'res/tilesets/char_portraits.png'),
    ('char_portraits_archive', 'res/tilesets/char_portraits_archive.png'),
    ('item_effects', 'res/tilesets/item_effects.png'),

    # Character sprites & monsters
    ('anthro_ragdoll', 'res/tilesets/anthro_ragdoll.png'),

    ('anthro_skeleton_red', 'res/tilesets/anthro_skeleton_red.png'),
    ('anthro_skeleton_yellow', 'res/tilesets/anthro_skeleton_yellow.png'),
    ('anthro_zombie', 'res/tilesets/anthro_zombie.png'),
    ('monster_spider_light', 'res/tilesets/monster_spider_light.png'),
    ('monster_spider_pale', 'res/tilesets/monster_spider_pale.png'),
    ('monster_slime_green', 'res/tilesets/monster_slime_green.png'),
    ('monster_gel_yellow', 'res/tilesets/monster_gel_yellow.png'),
    ('anthro_knight_blue', 'res/tilesets/anthro_knight_blue.png'),
    ('anthro_knight_blue_rich', 'res/tilesets/anthro_knight_blue_rich.png'),
    ('monster_mimic_chest', 'res/tilesets/monster_mimic_chest.png'),
    ('giant_spider_light', 'res/tilesets/giant_spider_light.png'),

    ('anthro_champion', 'res/tilesets/anthro_champion.png'),
    ('anthro_kingslayer', 'res/tilesets/anthro_kingslayer.png'),
    ('anthro_cosmologist', 'res/tilesets/anthro_cosmologist.png'),

    ('chapter_thumbs', 'res/tilesets/chapter_thumbs.png')
)

sounds = (
    ('button_click_push', 'res/sounds/click_02.wav'),
    ('button_click_release', 'res/sounds/click_04.wav'),
    ('switch_click_push', 'res/sounds/click_01.wav'),
    ('switch_click_release', 'res/sounds/click_03.wav'),
    ('input_key_press', 'res/sounds/singlesharptick01.wav'),
    ('input_enter', 'res/sounds/singlelowtick01.wav'),

    ('news_bell', 'res/sounds/bell_01.wav'),
    ('trader_cart', 'res/sounds/cart_01.wav'),
    ('paper_show', 'res/sounds/paper_03.wav'),
    ('paper_hide', 'res/sounds/paper_02.wav'),
    ('realmtext_noise', 'res/sounds/stone_01.wav'),
    ('important_jingle', 'res/sounds/owl_01.wav'),
    ('thunder_blast', 'res/sounds/thunder_02.wav'),
    ('thunder_rolling', 'res/sounds/thunder_01.wav'),
    ('level_up', 'res/sounds/fanfare_01.wav'),
    ('task_complete', 'res/sounds/fanfare_02.wav'),

    ('pc_step_01', 'res/sounds/step_01.wav'),
    ('pc_step_02', 'res/sounds/step_02.wav'),
    ('pc_step_03', 'res/sounds/step_03.wav'),
    ('pc_step_04', 'res/sounds/step_04.wav'),
    ('pc_step_05', 'res/sounds/step_05.wav'),
    ('pc_step_06', 'res/sounds/step_06.wav'),
    ('pc_step_07', 'res/sounds/step_07.wav'),

    ('coins_pickup', 'res/sounds/coins_01.wav'),
    ('coins_drop', 'res/sounds/coins_02.wav'),
    ('coins_trade', 'res/sounds/coins_03.wav'),
    ('prec_metal_ding', 'res/sounds/ding_01.wav'),
    ('prec_metal_muted', 'res/sounds/ding_02.wav'),
    ('item_drop_muted', 'res/sounds/drop_01.wav'),
    ('item_drag', 'res/sounds/rustle_02.wav'),
    ('item_move', 'res/sounds/wet_03.wav'),
    ('item_throw', 'res/sounds/air_01.wav'),
    ('tools_quiet', 'res/sounds/rustle_01.wav'),
    ('bag_drop', 'res/sounds/bag_01.wav'),
    ('cheese_eat', 'res/sounds/eat_02.wav'),
    ('fruit_eat', 'res/sounds/eat_01.wav'),
    ('fruit_pickup', 'res/sounds/wet_02.wav'),
    ('potion_pickup', 'res/sounds/bottle_02.wav'),
    ('potion_drop', 'res/sounds/bottle_01.wav'),
    ('potion_drink', 'res/sounds/drink_01.wav'),
    ('tools_drop', 'res/sounds/clank_02.wav'),
    ('tools_pickup', 'res/sounds/clank_02.wav'),
    ('lockpick_drop', 'res/sounds/clank_04.wav'),
    ('lockpick_pickup', 'res/sounds/clank_03.wav'),
    ('lock_operate', 'res/sounds/lock_01.wav'),
    ('lock_jam', 'res/sounds/snap_01.wav'),
    ('mech_hard', 'res/sounds/rustle_03.wav'),
    ('trap_operate', 'res/sounds/spring_01.wav'),
    ('wooden_door_open', 'res/sounds/door_02.wav'),
    ('wooden_door_shut', 'res/sounds/door_01.wav'),
    ('metal_door_open', 'res/sounds/grate_01.wav'),
    ('metal_door_shut', 'res/sounds/grate_02.wav'),
    ('chest_open', 'res/sounds/chest_01.wav'),
    ('chest_shut', 'res/sounds/chest_02.wav'),
    ('metal_pickup', 'res/sounds/metal_pickup_01.wav'),
    ('wood_pickup', 'res/sounds/wood_pickup_01.wav'),
    ('metal_drop', 'res/sounds/metal_drop_01.wav'),
    ('wood_drop', 'res/sounds/wood_drop_01.wav'),
    ('wooden_shield', 'res/sounds/wood_hit_01.wav'),
    ('chainmail_pickup', 'res/sounds/chains_02.wav'),
    ('chainmail_drop', 'res/sounds/chains_01.wav'),
    ('cloth_pickup', 'res/sounds/cloth_02.wav'),
    ('cloth_drop', 'res/sounds/cloth_01.wav'),
    ('hitech_helm', 'res/sounds/helm_01.wav'),
    ('plate_pickup', 'res/sounds/plate_02.wav'),
    ('plate_drop', 'res/sounds/plate_01.wav'),
    ('fire_pickup', 'res/sounds/torch_01.wav'),
    ('gas_inflation', 'res/sounds/torch_02.wav'),
    ('fire_putout', 'res/sounds/torch_03.wav'),
    ('sand_drop', 'res/sounds/sandy_01.wav'),
    ('sand_pickup', 'res/sounds/sandy_02.wav'),
    ('dig', 'res/sounds/dig_01.wav'),
    ('bones_drop', 'res/sounds/bones_01.wav'),
    ('bones_pickup', 'res/sounds/bones_02.wav'),

    ('melee_swipe', 'res/sounds/swipe_01.wav'),
    ('hit_slice', 'res/sounds/slice_01.wav'),
    ('hit_chop', 'res/sounds/chop_01.wav'),
    ('hit_blunt', 'res/sounds/hit_physical_01.wav'),
    ('hit_physical', 'res/sounds/hit_physical_02.wav'),
    ('hit_lightning', 'res/sounds/lightning_01.wav'),
    ('bow_shot', 'res/sounds/shot_01.wav'),
    ('pc_hit', 'res/sounds/hit_physical_02.wav'),
    ('hit_blast', 'res/sounds/blast_01.wav'),
    ('hit_ring', 'res/sounds/crit_damage_01.wav'),
    ('range_squirt', 'res/sounds/squirt_01.wav'),

    ('death_champion', 'res/sounds/moan_03.wav'),
    ('death_kingslayer', 'res/sounds/moan_01.wav'),
    ('death_cosmologist', 'res/sounds/moan_02.wav'),

    ('claws_tear', 'res/sounds/tear_01.wav'),
    ('undead_amb', 'res/sounds/bones_03.wav'),
    ('undead_aggro', 'res/sounds/snarl_03.wav'),
    ('undead_defeat', 'res/sounds/snarl_02.wav'),
    ('goo_amb', 'res/sounds/goo_03.wav'),
    ('goo_aggro', 'res/sounds/goo_02.wav'),
    ('goo_defeat', 'res/sounds/goo_01.wav'),
    ('insect_amb', 'res/sounds/chitin_03.wav'),
    ('insect_aggro', 'res/sounds/chitin_01.wav'),
    ('insect_defeat', 'res/sounds/chitin_02.wav'),
    ('knight_amb', 'res/sounds/clank_05.wav'),
    ('knight_aggro', 'res/sounds/human_01.wav'),
    ('knight_defeat', 'res/sounds/moan_04.wav'),

    ('laugh_chamber', 'res/sounds/laugh_01.wav'),

    ('cast_dispel', 'res/sounds/magic_ringing_02.wav'),
    ('cast_magical_arrow', 'res/sounds/magic_ringing_01.wav')
)

music = (

)
