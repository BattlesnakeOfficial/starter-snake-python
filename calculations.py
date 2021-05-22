import collections
from termcolor import colored
def distanceSort(posX,posY,fruitArray):
    print(colored("DISTANCE SORT DEBUG:","cyan"))
    
    distances = []
    for x in fruitArray:
       thing = (abs(posX - x[1]) + abs(posY - x[0]))
       distances.append(thing)
    print(fruitArray)
    print(colored("RAW: Distances","cyan"))
    print(colored(distances,"yellow"))
    output = [fruitArray for _, fruitArray in sorted(zip(distances, fruitArray))]
    print(output)
    return output




