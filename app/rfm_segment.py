class Segment1:
    segments = ('Champions', 'Loyal Customers', 'Potential Loyalist',
                'Recent Customers', 'Promising', 'Customers Needing Attention',
                'About To Sleep', 'At Risk', 'Can’t Lose Them', 'Hibernating', 'Lost'
                'Undefined')

    @classmethod
    def calc(cls, row):
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


class Segment2:
    segments = ('Rising Customer', 'Rising Customer', 'Stars', 'Active', 'Sleeping', 'Falling', 'Alert', 'Undefined')

    @classmethod
    def calc(cls, row_raw):
        """
        Calculate RFM Segment by given R, F and M score stored in the exact sequence in row (List/Tuple/Pandas.core.series)
        :param row_raw: the List/Tuple/Pandas.core.series contains R, F and M raw value in the exact order(R,F,M) / [R,F,M] / {index=[R,F,M], values}
        :return: Segment Name
        """
        r, f, m = row_raw[0], row_raw[1], row_raw[2]
        if 0 <= r <= 53:
            if f == 1:
                return 'New Customers'
            elif 2 <= f <= 3:
                return 'Rising Customer'
            elif f >= 4:
                return 'Stars'
            else:
                return 'Undefined'
        elif 54 <= r <= 107:
            if f == 1:
                return 'New Customers'
            elif f >= 2:
                return 'Active'
            else:
                return 'Undefined'
        elif 108 <= r <= 216:
            if 1 <= f <= 2:
                return 'Sleeping'
            elif f >= 3:
                return 'Falling'
            else:
                return 'Undefined'
        elif r >= 217:
            if 1 <= f <= 2:
                return 'Sleeping'
            elif f >= 3:
                return 'Alert'
            else:
                return 'Undefined'
        else:
            return 'Undefined'
