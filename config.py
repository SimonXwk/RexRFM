import os


# Default Configuration (inheriting from object is not necessary in python3)
class BaseConfig(object):
	""" Builtin Value Configurations
	"""
	DEBUG = False
	TESTING = False

	SECRET_KEY = 'you-will-never-guess'
	# MAX_CONTENT_LENGTH = 16 * 1024 * 1024

	""" General Value Configurations
	"""

	# Define the database directory
	DATABASE_URI = 'sqlite://:memory:'

	""" Flask-SQLAlchemy Configurations
	"""
	# TODO(delete this): SQLALCHEMY_TRACK_MODIFICATIONS adds significant overhead and will be disabled by default in the future. Set it to True or False to suppress this warning.
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	SQLALCHEMY_DATABASE_URI = 'mssql+pyodbc://usr:pwd@server/db?driver=SQL+Server'


class CustomConfig(BaseConfig):
	""" Configurations only apply to this application
	"""
	UPLOAD_FOLDER = 'csv'
	ALLOWED_EXTENSIONS = {'csv', 'tsv'}
	RFM_SECTOR_SEP = '_'
	RFM_SCORE_SEP = '-'


# Development Configuration
class DevelopmentConfig(CustomConfig):
	# Statement for enabling the development environment
	DEBUG = True
	TESTING = False


# Production Configuration
class ProductionConfig(CustomConfig):
	# Making sure that development/Testing environment are disabled
	DEBUG = False
	TESTING = False


# Testing Configuration
class TestingConfig(CustomConfig):
	# Statement for enabling the testing environment
	DEBUG = False


app_config_dict = {
	'development': DevelopmentConfig,
	'production': ProductionConfig,
	'testing': TestingConfig
}
