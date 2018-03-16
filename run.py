import os
import glob
import datetime
import re
import pandas as pd


def get_csv_folder():
    csv_folder = "csv"
    if not os.path.exists(csv_folder):
        os.makedirs(csv_folder)
    return csv_folder


def get_csv_mask_in_folder(folder):
    filename_pattern = '_'.join(['REX', '[0-9][0-9][0-9][0-9][0-1][0-9][0-3][0-9]', '[0-9][0-9][0-9][0-9][0-1][0-9][0-3][0-9]',
                                 'NOW', '[0-9][0-9][0-9][0-9][0-1][0-9][0-3][0-9]',
                                 '[1-9],[1-9],[1-9]'])
    return os.path.join(folder, filename_pattern + '.csv')


def get_merged_csv_raw(file_list, **kwargs):
    return pd.concat([pd.read_csv(f, **kwargs) for f in file_list], axis=0, ignore_index=True)  # Merge from Top-Down(axis0) and ignore indexes when merging


def rfm_asc_classification(value, buckets, q_dict):
    """
    :param value: a value to be rendered into RFM score
    :param buckets: quantile definition, a list of unique elements that are in range [0,1] in ascending order
    :param q_dict: quantile calculation by using buckets above, a dictionary of the percentiles by the bucket defined in buckets above
    :return: calculated RFM score, 1 is the worst and len(buckets)+1 is the best
    """
    for key, bucket in enumerate(buckets):
        if value > q_dict[buckets[-1]]:
            # print(value, bucket, q_dict[bucket], len(buckets)+1)
            return len(buckets)+1
        elif value <= q_dict[bucket]:
            # print(value, bucket, q_dict[bucket], key + 1)
            return key + 1


def rfm_analysis():

    # Find out which csv files to be collected, returning a list of file names
    file_list = glob.glob(get_csv_mask_in_folder(get_csv_folder()))
    print('Number of files to be collected : {}\n{}'.format(len(file_list), file_list))

    for f in file_list:
        # Collect information from each file and create Pandas DataFrame
        raw = pd.read_csv(f, index_col=None, low_memory=False) # If file contains no header row, then you should explicitly pass header=None
        print('\nRaw Data Format : {}\n{}'.format(raw.shape, raw.dtypes))

        # Collect the 'NOW' date for RFM analysis from the file name
        file_path, file_extension = os.path.splitext(f)
        filename = file_path.split('\\')[-1]
        filename_item = filename.split('_')  # File Name Split Array
        rfm_now = datetime.datetime.strptime(str(filename_item[-2]), '%Y%m%d')
        highest_score_r, highest_score_f, highest_score_m = map(int,filename_item[-1].split(','))
        print(highest_score_r, highest_score_f, highest_score_m)

        # Keep the columns that are essential to RFM analysis
        raw_header_customer_id, raw_header_customer_date, raw_header_order_id, raw_header_net = 'CustomerNumber', 'Date Created', 'OrderNumber', 'Sale Price Ext'
        raw = raw.loc[:, [raw_header_customer_id, raw_header_customer_date, raw_header_order_id, raw_header_net]]

        # Cleaning and reformatting raw data
        # Series.astype would not convert things that can not be converted to while pandas.to_datetime(Series) can (NaN).
        raw[raw_header_customer_date] = pd.to_datetime(raw[raw_header_customer_date], format='%d/%m/%Y %H:%M:%S %p')  # Convert to datetime value
        raw[raw_header_net] = pd.to_numeric(raw[raw_header_net]).astype('float').fillna(0)  # Convert to numeric value, format to float and fill na with zero
        raw[raw_header_customer_id] = raw[raw_header_customer_id].str.strip()  # Trimming
        raw[raw_header_order_id] = raw[raw_header_order_id].str.strip()  # Trimming
        print('\nNew Data Format : {}\n{}'.format(raw.shape, raw.dtypes))

        # Creating RFM data set
        recency_max = (rfm_now - raw[raw_header_customer_date].min()).days
        rfm = raw.groupby(raw_header_customer_id).agg(
            {
                raw_header_customer_date: lambda x: recency_max - (rfm_now - x.max()).days + 1,
                raw_header_order_id: 'count',
                raw_header_net: 'sum',
            }
        )
        rfm.rename(columns={raw_header_customer_date: 'recency', raw_header_order_id: 'frequency', raw_header_net: 'monetary_value'}, inplace=True)
        print('\nRFM Data Descriptive Statistics :\nAssuming NOW refers to {}\n{}'.format(rfm_now, rfm.describe()))

        rfm['last_trx'] = raw.groupby(raw_header_customer_id)[raw_header_customer_date].max()
        rfm['now'] = pd.to_datetime(rfm_now)
        print('\nRFM Data Format : {}\n{}'.format(rfm.shape, rfm.dtypes))

        # Calculate quantile
        buckets_r = [float((x+1)/highest_score_r) for x in range(highest_score_r-1)]
        buckets_f = [float((x+1)/highest_score_f) for x in range(highest_score_f-1)]
        buckets_m = [float((x+1)/highest_score_m) for x in range(highest_score_m-1)]

        quantiles_r = rfm['recency'].quantile(q=buckets_r).to_dict()
        quantiles_f = rfm['frequency'].quantile(q=buckets_f).to_dict()
        quantiles_m = rfm['monetary_value'].quantile(q=buckets_m).to_dict()
        print('\nquantiles R:\n{}\nquantiles F:\n{}\nquantiles M:\n{}'.format(quantiles_r, quantiles_f, quantiles_m))

        # Apply quantiles to RFM data set
        # rfm['r_score'] = rfm['recency'].apply(rfm_asc_classification, args=())
        rfm['r_score'] = rfm['recency'].apply(rfm_asc_classification, args=(buckets_r, quantiles_r))
        rfm['f_score'] = rfm['frequency'].apply(rfm_asc_classification, args=(buckets_f, quantiles_f))
        rfm['m_score'] = rfm['monetary_value'].apply(rfm_asc_classification, args=(buckets_m, quantiles_m))

        # Save RFM data set
        rfm.to_csv(os.path.join(get_csv_folder(), '_'.join([filename, 'rfmTable']) + '.csv'), encoding='utf-8-sig')

    print('\nDone! Please check results in folder : {}'.format(os.path.join(os.getcwd(), get_csv_folder())))


if __name__ == '__main__':
    rfm_analysis()
