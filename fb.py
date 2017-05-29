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
InitProb
initialize probabilities of possible alignments as uniform distribution
'''
def InitProb(pairs):
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
    fc = Expectation(pairs, probs, 3)

    print fc