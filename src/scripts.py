"""
Copyright © 2018 Valentin Berthelot.

This file is part of Instaseek.

Instaseek is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Instaseek is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Instaseek. If not, see <https://www.gnu.org/licenses/>.
"""

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