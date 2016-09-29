#!/usr/bin/env python3
import sys
import cProfile
from random import shuffle
    

def main():
    """
    if(len(sys.argv) < 2):
        print("Enter a queens string")
        return
    """

    USE_ALL_EQUAL_MINS = False
    USING_LATERAL = False

    global swap_num
    swap_num = 0

    # queens = sys.argv[1]
    global n
    n = 8
    # len(queens)

    def printboard(qs,conf):
        out = "   "
        for i in range(n):
            out += str(i) + " "
        out += "\n"
        out += (2*n+4) * "-" + "\n"
        for i in range(n):
            out += str(i) + "| "
            for ind,q in enumerate(qs):
                if ord(q) != i:
                    out+=". "
                else:
                    if((ind,ord(q)) in conf):
                        out += "\x1b[0;31mQ\x1b[0m "
                    else:
                        out += "Q "
            out += "|\n"
        out += (2*n+4) * "-" + "\n  "
        for i in range(n):
            out += str(i) + " "
        print(out)
        return

    cmap = {}
    def conflicts(sqs):
        if sqs not in cmap:
            n = len(sqs)
            qs = [(i,ord(sqs[i])) for i in range(n)]
            cons = 0
            ucons = 0
            fcons = set()
            for c1,r1 in qs:
                for c2,r2 in qs:
                    if c2 == c1 and r2 == r1: continue
                    if (c2-c1)**2 == (r2-r1)**2:
                        cons += 1
                        fcons.add((c2,r2))
            cmap[sqs] = cons,ucons,fcons
        return cmap[sqs]

    """
    def conflicts(sqs):
        n = len(sqs)
        # sqs = list(sqs)
        qs = [(i,ord(sqs[i])) for i in range(n)]
        cons = set()
        nums = {}
        # print(qs)
        for c,r in qs:
            # cons.append(set())
            for i in range(n):
                # cons[c].update({(i,(i-c)+r),(i,r),(i,(c-i)+r)})
                if i == c: continue
                y1 = (i,(i-c)+r)
                y2 = (i,(c-i)+r)
                if y1 not in nums:
                    nums[y1] = 0
                nums[y1] += 1
                cons.add(y1)
                if y2 not in nums:
                    nums[y2] = 0
                nums[y2] += 1
                cons.add(y2)
        fcons = set()
        nconflicts = 0
        nuconflicts = 0
        for c,r in qs:
            # conflictb = False
            # inter = (c,r) & cons
            if (c,r) in cons:
                nuconflicts += 1
                nconflicts += nums[(c,r)]
                # conflictb = True
                fcons.add((c,r))
            # if (c,r) in cons:
            # for key,con in enumerate(cons):
                # if c != key and (c,r) in con:
                # nconflicts += 1
                # fcons.add((c,r))
            # if(conflictb): nuconflicts += 1
        return nconflicts,nuconflicts,fcons
    """

    queens = ''.join([chr(i) for i in range(8)])
    c,unique,carr = conflicts(queens)
    print("Calculated: {}".format(c))
    print("Unique: {}".format(unique))
    printboard(queens,carr)
    print("Finding min")

    def swap(qs,i1,i2):
        qs[i1],qs[i2] = qs[i2],qs[i1]
        return qs
    def allswaps(qs):
        all = []
        for i in range(n-1):
            for j in range(i+1,n):
                global swap_num
                swap_num += 1
                all.append(''.join(swap(qs.copy(),i,j)))
        return all
    global seen
    seen = set()
    solns = set()
    C_NUM = 0 # 1 for dupe deletion, 0 for less pickiness
    def findmin(qs,depth=0,c=n**2):
        # if depth > 10: return qs
        seen.add(qs)
        c = conflicts(qs)[C_NUM]
        # print("Checking... D:{} C:{}".format(depth,c))
        if c == 0:
            # print("SOLUTION!!!")
            return qs
        res = {}
        for qstring in allswaps(list(qs)):
            if qstring in seen: continue
            nc = conflicts(qstring)[C_NUM]
            # seen.add(qstring)
            # if(nc == 0): return qstring
            res[qstring] = nc
            # print(nc)
        if not res: return qs;
        # print(res)
        mr = min(res)
        minc = res[mr]
        # print(list(mr),minc,depth)
        b = c < minc if USING_LATERAL else c <= minc
        if b:
            if depth == 0:
                # print("Already at local min")
                """
                if minc == c:
                    print("Adjacent mins: {}".format(all_min))
                """
            return qs
        minlist = []
        if USE_ALL_EQUAL_MINS:
            all_min = [index for index in res if minc == res[index]]
            all_min = sorted(all_min, key=lambda k:res[k])
            # all_min = all_min[0:5]
            # print(all_min)
            for mins in all_min:
                ms = findmin(mins,depth+1)
                if not ms: continue
                conf = conflicts(ms)[C_NUM]
                if depth == 0:
                    """ print("{} : {}".format(ms,conf)) """
                if(conf == 0):
                    solns.add(ms)
                    return ms
                if conf == 0 and ms not in solns:
                    """ print("{} : {}".format(ms,conf)) """
                    solns.add(ms)
                minlist.append(ms)
        else:
            ms = findmin(mr,depth+1)
            conf = conflicts(ms)[C_NUM]
            if(conf == 0):
                solns.add(ms)
            return ms
        if solns:
            return next(iter(solns)) # First solution
        else:
            return minlist[0] # Random local min

    FIND_MIN = False

    if FIND_MIN:
        m = findmin(queens,0)
        c,unique,carr = conflicts(m)
        print("Conflicts:")
        print("  Calculated: {}".format(c))
        print("  Unique: {}".format(unique))
        print("Board: {}".format(m))
        if(carr): print("Conflicts: {}".format(carr))
        printboard(m,carr)
        print("Total found solutions: {}".format(len(solns)))
    else:
        def shuffleall(queens):
            tot = 0
            lat = 0
            tplat = 0
            max_trials = 10000
            global swap_num
            swap_num = 0
            s = set()
            ns = set()
            # cmap = {} ## Cleared ONLY when n is changed (AND MUST BE CLEARED UNDER SUCH CASE)
            for i in range(max_trials):
                while True:
                    yep = True
                    global seen
                    seen = set()
                    sql = list(queens)
                    shuffle(sql)
                    # print("Shuffling...")
                    sq = ''.join(sql)
                    m = findmin(sq,0)
                    con,t,th = conflicts(m) # Using C_NUM 0
                    if con == 0: break
                    tot += 1
                    """
                    if(con == 0):
                        tot += 1
                        if(sq not in seen):
                            print("Found {}".format(sq))
                            seen.add(sq)
                    """
                    tplat += 1
                    for qstring in allswaps(list(m)):
                        nc = conflicts(qstring)[C_NUM]
                        if(nc <= con):
                            lat += 1
                            yep = False
                            # if m not in s: print(m)
                            s.add(m)
                            break
                    if yep:
                        if m not in ns:
                            # print(th)
                            # printboard(m,th)
                            print(m,con)
                        ns.add(m)
                            # print(m)
                    # minc = res[min(res)]
                # sys.stdout.write("{}%              \r".format(100*(i+1)/max_trials))
                # if(USE_ALL_EQUAL_MINS): print("Found a solution in {} shuffles".format(j))
            print("Average shuffles: {}".format(tot/max_trials))
            print("Average swaps: {}".format(swap_num/max_trials))
            # print("Percent correct: {}%".format(100*tot/trials))
            print("Percent can-move-laterally: {}%".format(100*lat/tplat))
            print(solns)
     
        allq = [''.join( [chr(i) for i in range(n)] ) for n in range(40,41)]
        # allq = ['0123','01234','012345','0123456','01234567','012345678','0123456789']
        # allq = map(list,allq)
        """
        USING_LATERAL = False
        print("Not using lateral")
        for eachq in allq:
            n = len(eachq)
            # for i in range(n):
            #     print(ord(eachq[i]))
            print("\tn="+str(n))
            shuffleall(eachq)
        """
        n = 7
        shuffleall('0123456')
        """
        USING_LATERAL = True
        print("Using lateral")
        for eachq in allq:
            # print(eachq)
            n = len(eachq)
            print("\tn="+str(n))
            shuffleall(eachq)
            cmap = {}
        """
    return

main()
# cProfile.run("main()")
