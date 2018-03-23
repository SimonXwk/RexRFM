class RFMScores:
    def __init__(self, rfm_row):
        # Calculate RFM Segment by given R, F and M score stored in the exact sequence in row (List/Tuple/Pandas.core.series)
        self.r = rfm_row[0]
        self.f = rfm_row[1]
        self.m = rfm_row[2]

    def segment1(self):
        if 4 <= self.r <= 5 and 4 <= ((self.f + self.m) / 2) <= 5:
            return 'Champions'
        elif 2 <= self.r <= 5 and 3 <= ((self.f + self.m) / 2) <= 5:
            return 'Loyal Customers'
        elif 3 <= self.r <= 5 and 1 <= ((self.f + self.m) / 2) <= 5:
            return 'Potential Loyalist'
        elif 4 <= self.r <= 5 and 0 <= ((self.f + self.m) / 2) <= 1:
            return 'Recent Customers'
        elif 3 <= self.r <= 4 and 0 <= ((self.f + self.m) / 2) <= 1:
            return 'Promising'
        elif 2 <= self.r <= 3 and 2 <= ((self.f + self.m) / 2) <= 3:
            return 'Customers Needing Attention'
        elif 2 <= self.r <= 3 and 0 <= ((self.f + self.m) / 2) <= 2:
            return 'About To Sleep'
        elif 0 <= self.r <= 2 and 2 <= ((self.f + self.m) / 2) <= 5:
            return 'At Risk'
        elif 0 <= self.r <= 1 and 4 <= ((self.f + self.m) / 2) <= 5:
            return 'Can’t Lose Them'
        elif 1 <= self.r <= 2 and 1 <= ((self.f + self.m) / 2) <= 2:
            return 'Hibernating'
        elif 0 <= self.r <= 2 and 0 <= ((self.f + self.m) / 2) <= 2:
            return 'Lost'


def rfm_segment_1(row):
    """
    Calculate RFM Segment by given R, F and M score stored in the exact sequence in row (List/Tuple/Pandas.core.series)
    :param row: the List/Tuple/Pandas.core.series contains R, F and M score in the exact order(R,F,M) / [R,F,M] / {index=[R,F,M], values}
    :return: Segment Name
    """
    r, f, m = row[0], row[1], row[2]
    fm = (f + m)/2
    if 4 <= r <= 5 and 4 <= fm <= 5:
        return 'Champions'
    elif 2 <= r <= 5 and 3 <= fm <= 5:
        return 'Loyal Customers'
    elif 3 <= r <= 5 and 1 <= fm <= 5:
        return 'Potential Loyalist'
    elif 4 <= r <= 5 and 0 <= fm <= 1:
        return 'Recent Customers'
    elif 3 <= r <= 4 and 0 <= fm <= 1:
        return 'Promising'
    elif 2 <= r <= 3 and 2 <= fm <= 3:
        return 'Customers Needing Attention'
    elif 2 <= r <= 3 and 0 <= fm <= 2:
        return 'About To Sleep'
    elif 0 <= r <= 2 and 2 <= fm <= 5:
        return 'At Risk'
    elif 0 <= r <= 1 and 4 <= fm <= 5:
        return 'Can’t Lose Them'
    elif 1 <= r <= 2 and 1 <= fm <= 2:
        return 'Hibernating'
    elif 0 <= r <= 2 and 0 <= fm <= 2:
        return 'Lost'