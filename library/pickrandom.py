# Takes a list of items and picks one random.
# Every item is an object/probability pair.
# Options are available: pick several items, pick several items removing the picked from the list.
import random
from library import logfun


# Pick items with or without removing the last cell in item list line has to be probability value.
def items_get(items_list, items_number=1, items_pop=False, log=False):
    if items_list is None or items_list == [] or items_number < 1:
        return []

    logfun.put('Roll for item (n=%s, pop=%s)...' % (items_number, items_pop), log)
    logfun.put(items_list, log)

    roll_volume = sum([itm[1] for itm in items_list])

    logfun.put('Roll scale: %s' % roll_volume, log)

    stop_rolls = False
    picked_list = []
    for k in range(0, items_number):
        counter = 1
        roll_rnd = random.randrange(1, roll_volume + 1)

        logfun.put('Roll result: %s' % roll_rnd, log)

        for i in range(0, len(items_list)):
            ceiling = counter + items_list[i][1]
            if counter <= roll_rnd < ceiling:
                picked_item = items_list[i][0]
                picked_list.append(picked_item)

                logfun.put('Roll falls inbetween %s and %s.' % (counter, ceiling), log)
                logfun.put('Picked item:', log)
                logfun.put(picked_item, log)

                if items_pop:
                    del items_list[i]

                    logfun.put('Rolled item removed!', log)

                    if len(items_list) == 0:
                        stop_rolls = True
                        break

                    roll_volume = sum([itm[1] for itm in items_list])

                    logfun.put('New roll scale: %s' % roll_volume, log)
                break
            counter = ceiling
        else:
            picked_item = None

            logfun.put('Result exceeds roll volume. No item picked.', log)

        if stop_rolls:
            break

    logfun.put('\nPicked list:', log)
    logfun.put(picked_list, log)

    return picked_list
