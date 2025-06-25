import sys

def readMem(pathFile):
    with open(pathFile, 'r') as f:
        lenMemory = int(f.readline())
        memoryRepStr = f.readline()
        memory = [int(char) for char in memoryRepStr]

        return lenMemory, memory
    
def findFreeBlocks(memory):
    freeBlocks = []
    i = 0
    while i < len(memory):
        if memory[i] == 0:
            start = i
            while i < len(memory) and memory[i] == 0:
                i+=1
            freeBlocks.append((start, i - start))
        else:
            i+=1

    return freeBlocks

def firstFit(freeBlocks, lenAllocation):
    for start, len in freeBlocks:
        if len >= lenAllocation:
            return start
        
    return None

def bestFit(freeBlocks, lenAllocation):
    best = None
    for start, len in freeBlocks:
        if len >= lenAllocation:
            if best is None or len < best[1]:
                best = (start, len)

    return best[0] if best != None else None

def worstFit(freeBlocks, lenAllocation):
    worst = None
    for start, len in freeBlocks:
        if len >= lenAllocation:
            if worst is None or len > worst[1]:
                worst = (start, len)

    return worst[0] if worst != None else None

def alloc(memory, indexAllocStart, lenAllocation, pid):
    for i in range(indexAllocStart, indexAllocStart + lenAllocation):
        memory[i] = pid

if __name__ == '__main__':
    strategy = sys.argv[1]
    pathFile = sys.argv[2]

    memLength, memory = readMem(pathFile)
    
    while True:
        lenAllocation = int(input('Informe o tamanho da alocação (ou -1 para sair): '))

        if lenAllocation == -1:
            break
        
        freeBlocks = findFreeBlocks(memory)
        
        if not freeBlocks:
            print('Não há mais memória livre para alocação.')
            break

        if strategy == 'first':
            indexAllocStart = firstFit(freeBlocks, lenAllocation)
        elif strategy == 'best':
            indexAllocStart = bestFit(freeBlocks, lenAllocation)
        elif strategy == 'worst':
            indexAllocStart = worstFit(freeBlocks, lenAllocation)

        if indexAllocStart is None:
            print('Não há espaço suficiente para alocação. Tente um tamanho menor.')
        else:
            pid = max(memory) + 1
            alloc(memory, indexAllocStart, lenAllocation, pid)

            print('Estado da memória após alocação:')
            print(memory)
            print('----------------------------------------')

    print('Alocações encerradas.\n')
    print('Estado final da memória:')
    print(memory)