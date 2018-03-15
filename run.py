import os
import glob
import re
import pandas as pd


def get_csv_folder():
    csv_folder = "csv"
    if not os.path.exists(csv_folder):
        os.makedirs(csv_folder)
    return csv_folder


def get_csv_mask_in_folder(folder):
    filename_pattern = '_'.join(['RFM', '*'])
    return os.path.join(folder, filename_pattern + '.csv')


def get_merged_csv_df(file_list, **kwargs):
    return pd.concat([pd.read_csv(f, **kwargs) for f in file_list], axis=0, ignore_index=True)  # Merge from Top-Down(axis0) and ignore indexes when merging


def collect_data():

    # Find out which csv files to be collected, returning a list of file names
    file_list = glob.glob(get_csv_mask_in_folder(get_csv_folder()))
    print('Number of files to be collected : {}\n{}'.format(len(file_list), file_list))

    # Collecting information and merge all to one Pandas DataFrame
    df = get_merged_csv_df(file_list, index_col=None, low_memory=False)  # If file contains no header row, then you should explicitly pass header=None

    df = df[['CustomerNumber', 'Date Created', 'OrderNumber', 'Sale Price Ext']]
    df.columns = ['CustomerID', 'Date', 'OrderID', 'Net']
    print('\nRaw Data Format : {}\n{}'.format(df.shape, df.dtypes))

    # Cleaning Raw Data
    # Series.astype would not convert things that can not be converted to while pandas.to_datetime(Series) can (NaN).
    df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y %H:%M:%S %p')  # Convert to datetime value
    df['Net'] = pd.to_numeric(df['Net']).astype('float')  # Convert to numeric value
    df['CustomerID'] = df['CustomerID'].str.strip()  # Trimming
    df['OrderID'] = df['OrderID'].str.strip()  # Trimming
    print('\nNew Data Format : {}\n{}'.format(df.shape, df.dtypes))

    # Fill Na for net value
    argg = []
    argg.append(df.groupby(['CustomerID'])['Net'].sum())
    argg.append(df.groupby(['CustomerID'])['OrderID'].count())
    argg.append(df.groupby(['CustomerID'])['Date'].max())

    result = pd.concat(argg, axis=1, ignore_index=False)

    result.to_csv(os.path.join(get_csv_folder(), 'out.csv'), encoding='utf-8-sig')


if __name__ == '__main__':

    collect_data()

