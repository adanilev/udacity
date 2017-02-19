import string

lowercase = list(string.ascii_lowercase)
uppercase = list(string.ascii_uppercase)
increment = 13

def convert(text, direction):
    """Converts the text to ROT13 if direction > 1, converts from ROT13 back to
    english if direction < 0
    TODO: make this a class so we don't need to construct the lists every
    call
    TODO: is there a better way to do this with tuples and/or comprehensions?
    """

    #add lowercase letters to dict so we can look them up
    dictLower = {}
    i = 0
    for letter in lowercase:
        dictLower[letter] = i
        i += 1

    #now the uppercase
    dictUpper = {}
    i = 0
    for letter in uppercase:
        dictUpper[letter] = i
        i += 1

    #now add all the letters to a list so we can access by index
    listLower = []
    for letter in lowercase:
        listLower.append(letter)

    #again, do the uppercase
    listUpper = []
    for letter in uppercase:
        listUpper.append(letter)

    #finally, let's convert the user's input
    #TODO: deal with wrapping around the list, reversing to convert back, uppercase
    result = ''
    for letter in text:
        if letter.islower():
            result += listLower[getNewIndex(dictLower[letter], len(listLower), direction)]
        elif letter.isupper():
            result += listUpper[getNewIndex(dictUpper[letter], len(listUpper), direction)]
        else:
            result += letter

    return result

def getNewIndex(currindex, listlen, direction):
    if direction > 0:
        if currindex + increment >= listlen:
            return increment - (listlen - currindex)
        else:
            return currindex + increment
    else:
        #DON'T NEED TO THINK ABOUT DIRECTION!!! DOH!!
        if currindex - direction < 0:
            return listlen - (increment - currindex)
        else:
            return currindex - increment
