import os
import glob
import datetime
import pandas as pd
from flask import current_app

from app.rfm_segment import rfm_segment_2 as rfm_segment


def get_csv_folder():
	# csv_folder = "csv"
	csv_folder = current_app.config['UPLOAD_FOLDER']
	if not os.path.exists(csv_folder):
		os.makedirs(csv_folder)
	return csv_folder


def get_csv_mask_in_folder(folder):
	"""
	:param folder: folder full path where the csv files will be matched by file name mask
	:return: String(mask) the describes what the file name looks like
	"""
	sep1 = current_app.config['RFM_SECTOR_SEP']
	sep2 = current_app.config['RFM_SCORE_SEP']

	# Mask structure: (REX)_(system report start date)_(system report end date)_(NOW)_now date you defined_(R highest score),(F highest score),(M highest score).csv
	# Date format in file name : '%Y%m%d'
	filename_pattern = sep1.join(['REX', '[0-9][0-9][0-9][0-9][0-1][0-9][0-3][0-9]', '[0-9][0-9][0-9][0-9][0-1][0-9][0-3][0-9]',
	                              'NOW', '[0-9][0-9][0-9][0-9][0-1][0-9][0-3][0-9]', '[1-9]'+sep2+'[1-9]'+sep2+'[1-9]'
	                              ])
	return os.path.join(folder, filename_pattern + '.csv')


def get_merged_csv_raw(file_list, **kwargs):
	return pd.concat([pd.read_csv(f, **kwargs) for f in file_list], axis=0, ignore_index=True)  # Merge from Top-Down(axis0) and ignore indexes when merging


def rfm_calculate_score(value, buckets, q_dict, sort_type='asc'):
	"""
	:param value: a value to be rendered into RFM score
	:param buckets: quantile definition, a list of unique elements that are in range [0,1] in ascending order
	:param q_dict: quantile calculation by using buckets above, a dictionary of keys of the percentages  in buckets above and values of calculated values percentiles
	:param sort_type:
	:return: calculated RFM score, 1 is the worst and len(buckets)+1 is the best (ASC), 1 is the best and len(buckets)+1 is worst (DESC)
	"""
	if str(sort_type).upper() == 'ASC':
		for key, bucket in enumerate(buckets):
			if value > q_dict[buckets[-1]]:
				return len(buckets) + 1  # Bigger than the highest percentile : highest score
			elif value <= q_dict[bucket]:
				return key + 1  # Checking from lowest to highest, give score on the first match
	elif str(sort_type).upper() == 'DESC':
		for key, bucket in enumerate(reversed(buckets)):
			if value < q_dict[buckets[-1]]:
				return len(buckets) + 1  # Smaller than the highest percentile : highest score
			elif value >= q_dict[bucket]:
				return key + 1  # Checking from highest to lowest, give score on the first match


def file_all_files():
	return glob.glob(get_csv_mask_in_folder(get_csv_folder()))


def rfm_analysis(file_name=None):
	if file_name:
		file_list = [os.path.join(get_csv_folder(), file_name)]
		print('Analysing File {}'.format(file_name))
	else:
		# Find out which csv files to be collected, returning a list of file names
		file_list = file_all_files()
		print('Number of files to be collected : {}\n{}'.format(len(file_list), file_list))

	sep1 = current_app.config['RFM_SECTOR_SEP']
	sep2 = current_app.config['RFM_SCORE_SEP']
	data = {}

	for fid, f in enumerate(file_list):
		# Collect the 'NOW' date for RFM analysis from the file name
		file_path, file_extension = os.path.splitext(f)
		filename = file_path.split('\\')[-1]  # Get rid of containing folders

		# Interpreting the special file naming structure
		filename_item = filename.split(sep1)  # File Name Split Array
		rfm_now = datetime.datetime.strptime(str(filename_item[-2]), '%Y%m%d')  # Second last part of file name is Now date
		highest_score_r, highest_score_f, highest_score_m = map(int, filename_item[-1].split(sep2))  # Second last part of file name is RFM highest scores separated by ,

		# Keep the columns that are essential to RFM analysis
		raw_header_customer_id, raw_header_customer_date, raw_header_order_id, raw_header_net = \
			'CustomerNumber', 'Date Created', 'OrderNumber', 'Sale Price Ext'
		basic_header = [raw_header_customer_id, raw_header_customer_date, raw_header_order_id, raw_header_net]
		addition_header = ['Product Type', 'Description']

		# Collect information from each file and create Pandas DataFrame
		# If file contains no header row, then you should explicitly pass header=None
		raw = pd.read_csv(f, index_col=None, low_memory=False, usecols=basic_header + addition_header)

		# We want only the coffee buyers
		# raw['Coffee'] = raw['Description Type'] = 'Food & Beverages' and raw['Description Type'].str.contain('Food & Beverages', flags=re.IGNORECASE, regex=True)
		# print(raw)

		raw = raw.loc[:, basic_header]
		# print('\nRaw Data Format : {}\n{}'.format(raw.shape, raw.dtypes))

		# Cleaning and reformatting raw data
		# Series.astype would not convert things that can not be converted to while pandas.to_datetime(Series) can (NaN).
		raw[raw.select_dtypes(['object']).columns] = raw.select_dtypes(['object']).apply(lambda x: x.str.strip())  # Trimming String columns
		raw[raw_header_customer_date] = pd.to_datetime(raw[raw_header_customer_date], dayfirst=True)  # Convert to datetime value
		raw[raw_header_net] = pd.to_numeric(raw[raw_header_net]).astype('float').fillna(0)  # Convert to numeric value, format to float and fill na with zero
		# print('\nNew Data Format : {}\n{}'.format(raw.shape, raw.dtypes))

		# Creating RFM data set
		recency_max = (rfm_now - raw[raw_header_customer_date].min()).days  # <class 'datetime.datetime'> - <class 'pandas._libs.tslib.Timestamp'> gives <class 'pandas._libs.tslib.Timedelta'>
		rfm = raw.groupby(raw_header_customer_id).agg(
			{
				raw_header_customer_date: lambda x: recency_max - (rfm_now - x.max()).days + 1,
				raw_header_order_id: 'nunique',
				raw_header_net: 'sum',
			}
		)
		rfm.rename(columns={raw_header_customer_date: 'recency', raw_header_order_id: 'frequency', raw_header_net: 'monetary_value'}, inplace=True)
		# print('\nRFM Data Descriptive Statistics :\nAssuming NOW refers to {}\n{}'.format(rfm_now, rfm.describe()))
		# rfm = rfm.loc[rfm['frequency'] < 120, :]

		rfm['last_trx'] = raw.groupby(raw_header_customer_id)[raw_header_customer_date].max()
		rfm['now'] = pd.to_datetime(rfm_now)
		# print('\nRFM Data Format : {}\n{}'.format(rfm.shape, rfm.dtypes))

		# Calculate quantile
		buckets_r = [float(x / highest_score_r) for x in range(1, highest_score_r)]
		buckets_f = [float(x / highest_score_f) for x in range(1, highest_score_f)]
		buckets_m = [float(x / highest_score_m) for x in range(1, highest_score_m)]

		quantiles_r = rfm['recency'].quantile(q=buckets_r).to_dict()
		quantiles_f = rfm['frequency'].quantile(q=buckets_f).to_dict()
		quantiles_m = rfm['monetary_value'].quantile(q=buckets_m).to_dict()
		print('\nquantiles R:\n{}\nquantiles F:\n{}\nquantiles M:\n{}'.format(quantiles_r, quantiles_f, quantiles_m))

		# Apply quantiles to RFM data set
		rfm['r_score'] = rfm['recency'].apply(rfm_calculate_score, args=(buckets_r, quantiles_r, 'asc'))
		rfm['f_score'] = rfm['frequency'].apply(rfm_calculate_score, args=(buckets_f, quantiles_f, 'asc'))
		rfm['m_score'] = rfm['monetary_value'].apply(rfm_calculate_score, args=(buckets_m, quantiles_m, 'asc'))

		# Calculate Segments
		# segment = seg.rfm_segment_1
		# rfm['Segment'] = rfm.loc[:, ['r_score', 'f_score', 'm_score']].apply(segment, axis=1)

		rfm['Segment'] = rfm.loc[:, ['recency', 'frequency', 'monetary_value']].apply(lambda x: rfm_segment(x), axis=1)
		# rfm['Segment'] = rfm.loc[:, ['r_score', 'f_score', 'm_score']].apply(lambda x: rfm_segment(x), axis=1)

		# Save RFM data set
		# rfm.to_csv(os.path.join(get_csv_folder(), '_'.join([filename, 'rfmTable']) + '.csv'), encoding='utf-8-sig')
		# print(rfm['Segment'])
		data[str(fid)] = rfm['Segment']


	print('\nRFM calculation finished, check results in folder : {}'.format(os.path.join(os.getcwd(), get_csv_folder())))
	return data
