from math import sqrt


class RatingSystem:
    """
    Attributes of this class is not stable, do not use them.
    """
    participants = []
    rank = {}
    ratings = {}
    d = {}
    stimulation = 0

    def __init__(self, ranks: dict, before_ratings: dict, stimulation: int = None):
        ordered = sorted(ranks.items(), key=lambda it: it[1])
        self.participants = []
        for x in ordered:
            self.participants.append(x[0])
        self.rank = ranks.copy()
        self.ratings = before_ratings.copy()
        self.participants.append(-1)
        self.rank[-1] = max(ranks.values()) + 1
        self.ratings[-1] = stimulation if stimulation is not None else 0
        self.__rearrange_ranks()

    def get_new_ratings(self):
        self.__calc_diff()
        r = {}
        for i in self.participants:
            r[i] = self.ratings[i] + self.d[i]
        r.pop(-1)
        rem = self.d[-1]
        return r, rem

    def __calc_diff(self):
        orded_by_rating = sorted(self.ratings.items(), key=lambda it: it[1], reverse=True)
        n = len(self.participants)

        for i in range(len(orded_by_rating)):
            orded_by_rating[i] = orded_by_rating[i][0]
        for i in self.participants:
            sd = self.__calc_seed(i)
            rk = self.rank[i]
            m = round(sqrt(sd * rk))
            R = self.ratings[orded_by_rating[m - 1]]
            act = sd - rk
            self.d[i] = (R - self.ratings[i]) // 2 + int(act * 10)

        # Total sum should not be more than zero.
        sum = 0
        for i in self.participants:
            sum += self.d[i]
        inc = -sum // n
        for i in self.participants:
            self.d[i] += inc

        # Sum of top-4*sqrt should be adjusted to zero.
        sum = 0
        zero_sum_count = min(int(4 * round(sqrt(n))), n)
        for i in range(0, zero_sum_count):
            sum += self.d[orded_by_rating[i]]
        inc = min(max(-sum // zero_sum_count, -10), 0)
        for i in self.participants:
            self.d[i] += inc

    def __calc_P(self, x, y):
        return 1 / (1 + 10 ** ((self.ratings[y] - self.ratings[x]) / 400))

    def __calc_seed(self, pid):
        sd = 1
        for i in self.participants:
            if i != pid:
                sd += self.__calc_P(i, pid)
        return sd

    def __rearrange_ranks(self):
        new_rk = {}
        successive_ordered_rank = sorted(self.rank.items(), key=lambda x: x[1])
        p = 1
        for k, v in successive_ordered_rank:
            new_rk[k] = p
            p += 1
        self.rank = new_rk


if __name__ == '__main__':
    rlst = {}
    blst = {}
    for i in range(1, 11):
        rlst[i] = i
        blst[i] = 0
    while True:
        input("press enter")
        print("contest result:")
        print('rlst:', rlst)
        print('blst:', blst)

        print("after contest ratings")
        rs = RatingSystem(ranks=rlst, before_ratings=blst, stimulation=5000)
        nlst = rs.get_new_ratings()
        delta = {}
        for i in blst.keys():
            delta[i] = nlst[i] - blst[i]
        print('new ratings:', nlst)
        print('delta:', delta)
        blst = nlst
