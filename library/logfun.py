# Logging module
# Takes message and outputs it to log.

def put(items_list, log=True):
    if log:
        if type(items_list) in (tuple, list):
            for itm in items_list:
                print(itm)
            return len(items_list)
        else:
            print(items_list)
            return 1
    return 0