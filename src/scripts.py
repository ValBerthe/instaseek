from os import listdir
from os.path import isfile, join

def countLinesInPath(path,directory):
    count=0
    for line in open(join(directory,path), encoding="utf8"):
        count+=1
    return count

def countLines(paths,directory):
    count=0
    for path in paths:
        count=count+countLinesInPath(path,directory)
    return count

def getPaths(directory):
    return [f for f in listdir(directory) if isfile(join(directory, f))]

def countIn(directory):
    return countLines(getPaths(directory),directory)

if __name__ == '__main__':
    print('Number of lines in src: ' + str(countIn('./')))