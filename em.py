#!/bin/python

def expect(e, j, maxE2J):
ßßßß    return enumAlign(e, j, maxE2J)


#
# def enumerateAlignments(e, j, maxE2J):
#     aligns = [[[] for k in range(maxE2J)] for i in range(e)]
#     jpos = 0
#     for i in range(len(e)):
#         for k in range(maxE2J):
#             aligns[i][k].append((e[i], ))


def enumAlign(eng, jap, maxE2J):
    if len(eng) == 0 and len(jap) == 0:
        return []
    elif len(eng) == 0 or len(jap) == 0:
        return None

    aligns = []
    align = [[(eng[0], jap[:i])] for i in range(min(maxE2J, len(jap)))]
    for i in range(min(maxE2J, len(jap))):
        post = enumAlign(eng[1:], jap[i + 1:], maxE2J)
        print post
        if post != None:
            align[i].append(post)

    return align




if __name__ == '__main__':
    print expect(['B', 'OW', 'T'], ['B', 'O', 'T'], 3)