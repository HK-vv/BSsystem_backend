def calc_rating_result(rank, blst):
    tot = len(rank)
    r = {}
    for p, ra in blst.items():
        diff = 0
        rk = rank[p]
        if rk <= tot * 5 // 75:
            diff = 5
        elif rk <= tot * 15 // 75:
            diff = 4
        elif rk <= tot * 30 // 75:
            diff = 3
        elif rk <= tot * 50 // 75:
            diff = 2
        elif rk <= tot * 75 // 75:
            diff = 1
        r[p] = ra + diff
    return r
