from __future__ import print_function
from collections import defaultdict

'''
Expectation
compute forward and backward probabilities
then return fractional counts of each alignment

wordPairs:  (string, string) of English, Japanese
prior:      dict mapping e->j->p where p is current prob. est.
maxE2J:     maximum k in k-to-1 mapping
'''
def Expectation(wordPairs, prior, maxE2J):
    fracCount = defaultdict(lambda : defaultdict(float))
    for eword, jword in wordPairs:
        e, j = eword.split(), jword.split()
        # compute forward and backward prob for each word
        alpha = Forward(e, j, prior, maxE2J)
        beta = Backward(e, j, prior, maxE2J)
        # sum the fractional counts
        c = FindFracCounts(e, j, alpha, beta, prior, maxE2J)
        for ep, js_co in c.items():
            for js, co in js_co.items():
                fracCount[ep][js] += co

    return fracCount



def Maximization(wordPairs, counts, prior, maxE2J):
    # recompute probabilities based on new "data"
    for eword, jword in wordPairs:
        eword, jword = eword.split(), jword.split()
        for ephon in eword:
            for j in range(len(jword)):
                for k in range(1, min(len(jword) - j, maxE2J) + 1):
                    js = tuple(jword[j : j + k])
                    # prob = ??



'''
forward
eprons:     list of English sounds
jprons:     list of Japanese sounds
prior:      dict mapping e->j->p where p is current prob. est.
maxE2J:     maximum k in k-to-1 mapping
'''
def Forward(eprons, jprons, prior, maxE2J):
    # alpha: prob. of getting to this state by some path from start
    numJ, numE = len(jprons), len(eprons)
    alpha = [[0. for i in range(numJ + 1)] for j in range(numE + 1)]
    alpha[0][0] = 1.
    # find alpha for each alignment
    for i in range(numE):
        for j in range(numJ):
            for k in range(1, min(numJ - j, maxE2J) + 1):
                ep, js = eprons[i], tuple(jprons[j : j + k])
                alpha[i + 1][j + k] += alpha[i][j] * prior[ep][js]

    return [row[1 :] for row in alpha[1 :]]



'''
backward
eprons:     list of English sounds
jprons:     list of Japanese sounds
prior:      dict mapping e->j->p where p is current prob. est.
maxE2J:     maximum k in k-to-1 mapping
'''
def Backward(eprons, jprons, prior, maxE2J):
    # beta: prob. of getting to final state from this state
    numJ, numE = len(jprons), len(eprons)
    beta = [[0. for i in range(numJ + 1)] for j in range(numE + 1)]
    beta[numE][numJ] = 1.
    for i in range(numE - 1, -1, -1):
        for j in range(numJ - 1, -1, -1):
            for k in range(min(j, maxE2J) + 1):
                ep, js = eprons[i], tuple(jprons[j - k : j + 1])
                beta[i][j - k] += beta[i + 1][j + 1] * prior[ep][js]

    return [row[: numJ] for row in beta[: numE]]



'''
backward
eprons:     list of English sounds
jprons:     list of Japanese sounds
alpha:      array of forward probabilities by [epron][jpron]
beta:       array of backward probabilities
prior:      dict mapping e->j->p where p is current prob. est.
maxE2J:     maximum k in k-to-1 mapping
'''
def FindFracCounts(eprons, jprons, alpha, beta, prior, maxE2J):
    numJ, numE = len(jprons), len(eprons)
    counts = defaultdict(lambda : defaultdict(float))

    # sum probabilities for each alignment
    for i in range(numE):
        for j in range(numJ):
            for k in range(1, min(numJ - j, maxE2J) +1):
                ep, js = eprons[i], tuple(jprons[j: j + k])
                # count for align is forward * backward * prior probability
                c = alpha[i][j + k - 1] * beta[i][j + k - 1] * prior[ep][js]
                counts[ep][js] += c
    # normalize
    for e, d in counts.items():
        for j in d.keys():
            counts[e][j] /= beta[0][0]

    return counts



'''
ReadEpronJpron
get word pairs from file
'''
def ReadEpronJpron(filename):
    wordPairs = []
    with open(filename) as fp:
        for i, line in enumerate(fp.readlines()):
            if i % 3 == 0:
                eword = line.strip('\n')
            elif i % 3 == 1:
                jword = line.strip('\n')
                wordPairs.append((eword, jword))

    return wordPairs



'''
EnumAligns
enumerate all possible alignments
ephon:  list of English phonemes
jphon:  list of Japanese phonemes
'''
def EnumAligns(ephon, jphon, pre = []):
    aligns = []
    ep = ephon[0]
    for i in range(1, min(3, len(jphon)) + 1):
        js = tuple(jphon[: i])
        if len(ephon) == 1 and len(jphon) - i == 0:
            aligns.append(pre + [(ep, js)])
        elif len(ephon) == 1 or len(jphon) - i == 0:
            continue
        else:
            s = [(ep, js)]
            post = EnumAligns(ephon[1 :], jphon[i :], s)
            for p in post:
                aligns.append(pre + p)

    return aligns



def InitProb(pairs):
    counts = defaultdict(lambda: defaultdict(int))
    for ew, jw in pairs:
        ew, jw = ew.split(), jw.split()
        aligns = EnumAligns(ew, jw, [])
        for alt in aligns:
            for (ep, js) in alt:
                counts[ep][js] += 1

    # initialize probabilities from "observed" counts
    probs = defaultdict(lambda : defaultdict(float))
    for ep, js_co in counts.items():
        n = sum(js_co.values())
        for js, co in js_co.items():
            probs[ep][js] = float(co) / n

    return probs



'''
InitProb
initialize probabilities of possible alignments
'''
def BadInitProb(pairs):
    counts = defaultdict(lambda : defaultdict(int))
    # count every possible alignment
    for ew, jw in pairs:
        jw = jw.split()
        for i, ep in enumerate(ew.split()):
            for j in range(len(jw)):
                # match to 1, 2 or 3 Japanese sounds
                for k in range(min(3, len(jw) - j) + 1):
                    js = jw[j : j + k]
                    if len(js) != 0:
                        js = tuple(js)
                        counts[ep][js] += 1

    # initialize probabilities from "observed" counts
    probs = defaultdict(lambda : defaultdict(float))
    for ep, js_co in counts.items():
        n = sum(js_co.values())
        for js, co in js_co.items():
            probs[ep][js] = float(co) / n

    return probs



if __name__ == '__main__':
    fname = 'data/epron-jpron.data'
    pairs = ReadEpronJpron(fname)
    probs = InitProb(pairs)
    counts = Expectation(pairs, probs, 3)

    # (e, j) = pairs[0]
    # e, j = e.split(), j.split()
    # aligns = EnumAligns(e, j, [])
    # for a in aligns:
    #     print('{}'.format(a))

    #we need to do the maximization step, but for now I'll print the fractional counts
    for e, jp in counts.items():
        print('\n*** {} ***'.format(e))
        for j, p in jp.items():
            print('\t\t{} : {}'.format(j, p))