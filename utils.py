import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

ch.setFormatter(formatter)
logger.addHandler(ch)

def stripDictList(dictList, listOfAllowedFields):
    #logger.debug("inside strip dict")
    tmpList = []
    for listItem in dictList:
        #logger.debug("list item")
        #logger.debug(listItem)
        tmpDict = {key: value for (key, value) in listItem.items() if key in listOfAllowedFields}
        #logger.debug(tmpDict)
        if tmpDict:
            tmpList.append(tmpDict)
    #logger.debug(tmpList)
    return tmpList

def flattenItem(displayitem, key, flattenkey):
    return flattenDict(displayitem[key], flattenkey)

def flattenDict(flattenable, flattenKey):
    flatstring = ''
    
    if type(flattenable) == list:
        for tag in flattenable:
            if flattenKey in tag:
                flatstring = tag[flattenKey]
    elif type(flattenable) == dict:
        if flattenKey in flattenable:
            flatstring = flattenable[flattenKey]
    return flatstring
