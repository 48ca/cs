def find(n):
    if n==1: return []
    if n==2: return [0,0]
    fs = find(n-1)
    lr = list(range(n-1))
    pfx = [lr, lr[::-1]]
    fsr = [pfx[i%2] + [fs[i] + (i%2)] for i in range(len(fs))]
    return [elem for fsrsub in fsr for elem in fsrsub]
