
def attack_default(pc, skill_props, just_values=False):
    att_val_min, att_val_max = pc.char_sheet.attacks['att_base']
    att_mods = pc.char_sheet.calc_attack_mod('att_physical')
    att_val_min += (att_val_min * att_mods // 100)  # att_mods comprehended as procents
    att_val_max += (att_val_min * att_mods // 100)  # att_mods comprehended as procents
    if just_values:
        return att_val_min, att_val_max
