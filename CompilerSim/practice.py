import argparse
import pefile
import os
from hashlib import sha256
import string
import csv


def createParser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--path', help='Path to .exe file', type=str, required=True)

    return parser


def getFeatures(path):
    imports = []
    sections = []
    strings = []

    # Opening file
    try:
        file = pefile.PE(path)
    except pefile.PEFormatError:
        return None, None, None, None

    # Collecting imports
    try:
        for item in file.DIRECTORY_ENTRY_IMPORT:
            for imp in item.imports:
                if imp.name != None:
                    imports.append(imp.name.decode('utf-8'))
    except AttributeError:
        pass

    # Collecting strings
    try:
        for str in file.StringFileInfo:
            if str.name != None:
                strings.append(str.name.decode('utf-8'))
    except AttributeError:
        pass

    # Collecting sections
    try:
        for sec in file.sections:
            if sec.Name != None:
                secName = sec.Name.decode('utf-8')
                secName = ''.join([x for x in secName if x in string.printable])
                sections.append(secName)
    except AttributeError:
        pass
    except UnicodeDecodeError:
        pass
    file.close()

    # Calculating sha256
    with open(path, "rb") as f:
        bytes = f.read()
        readable_hash = sha256(bytes).hexdigest()

    return imports, sections, strings, readable_hash


def saveFeatures(filename, imports, sections, strings, readable_hash):
    currentDir = filename
    fullDir = 'new_dataset/' + currentDir
    os.makedirs(fullDir, exist_ok=True)

    # Saving imported functions
    f = open(fullDir + '/imports.txt', 'w')
    for i in imports:
        f.write(i + '\n')
    f.close()

    # Saving sections
    f = open(fullDir + '/sections.txt', 'w')
    for i in sections:
        f.write(i + '\n')
    f.close()

    # Saving strings
    f = open(fullDir + '/strings.txt', 'w')
    for i in strings:
        f.write(i + '\n')
    f.close()

    # Saving sha256
    f = open(fullDir + '/sha256.txt', 'w')
    f.write(readable_hash)
    f.close()


def compareFeatures(filename, imports, sections, strings, sha256):
    sharedImports = []
    sharedSections = []
    sharedStrings = []
    sharedTotal = []

    standartPrograms = []
    featuresArrays = [imports, sections, strings]
    featuresFiles = ['imports.txt', 'sections.txt']

    # Getting standart programs names
    for file in os.listdir('dataset/'):
        standartPrograms.append(file)

    for i in standartPrograms:
        sharedImports.append(0)
        sharedSections.append(0)
        sharedStrings.append(0)

    # Counting shared features
    for idp, program in enumerate(standartPrograms):
        for idf, file in enumerate(featuresFiles):
            f = open('dataset/' + program + '/' + file)
            for line in f:
                line = line.strip()
                for ln in featuresArrays[idf]:
                    if line == ln:
                        if idf == 0:
                            sharedImports[idp] += 1
                        if idf == 1:
                            sharedSections[idp] += 1
                        if idf == 2:
                            sharedStrings[idp] += 1
        sharedTotal.append(sharedImports[idp] + sharedSections[idp])

    # Counting features in compared files
    featuresSize = len(imports) + len(sections) + len(strings)
    standartFeaturesSize = 0
    for file in featuresFiles:
        standartFeaturesSize += sum(
            1 for line in open('dataset/' + standartPrograms[sharedTotal.index(max(sharedTotal))] + '/' + file))


    #For getting debug information need to read [IMAGE_DEBUG_DIRECTORY]
    print(pefile.DebugData)
    print('The most similar standart .exe or .dll for ' + filename + ' is ' + standartPrograms[
        sharedTotal.index(max(sharedTotal))])

    with open('out', 'a', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=';')
        writer.writerow([sha256, standartPrograms[sharedTotal.index(max(sharedTotal))],
                         str(max(sharedTotal) / max(featuresSize, standartFeaturesSize))])


def main():
    parser = createParser()
    namespace = parser.parse_args()

    filesList = []

    if namespace.path.lower().endswith('.exe'):
        filename = os.path.basename(namespace.path)
        imports, sections, strings, sha256 = getFeatures(namespace.path)
        if sha256 != None:
            saveFeatures(filename, imports, sections, strings, sha256)
            compareFeatures(filename, imports, sections, strings, sha256)
    else:
        for file in os.listdir(namespace.path):
            if file.lower().endswith('.exe'):
                filesList.append(os.path.join(namespace.path, file))

        for filepaths in filesList:
            filename = os.path.basename(filepaths)
            imports, sections, strings, sha256 = getFeatures(filepaths)
            if sha256 != None:
                saveFeatures(filename, imports, sections, strings, sha256)
                compareFeatures(filename, imports, sections, strings, sha256)


if __name__ == '__main__':
    main()
