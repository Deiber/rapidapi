import sqlite3
from requests import request
import os
import json
import pandas as pd
from pandas import DataFrame
import json
import logging
import hashlib as h
import time
from typing import Optional
from pandas._typing import Axes, Dtype
from pymongo import MongoClient

API_KEY = os.environ["API_KEY"]


ENDPOINTS = {
	"all": "https://restcountries-v1.p.rapidapi.com/all",
	"all_countries": "https://restcountries.eu/rest/v2/all"
}

# mongo credentials
MONGO = {
	"db": os.environ["MONGO_DB"],
	"host": os.environ["MONGO_HOST"],
	"port": "27017",
	"username": os.environ["MONGO_USERNAME"],
	"psw": os.environ["MONGO_PSW"]
}

logging.basicConfig(format="%(levelname)s: %(message)s")


def set_time(value, time_start, round_numbers=None):
	"""
	helper function that returns the difference between tow dates and add it 
	to given value 
	"""
	if not round_numbers:
		round_numbers = 10

	return float(
		round(value + (time.time() - time_start), round_numbers)
	)

class RapidApi:
	
	def _get_headers(self, extra_headers={}):
		"""helper method for request headers"""
		default_headers = {
			"x-rapidapi-host": "restcountries-v1.p.rapidapi.com",
			"x-rapidapi-key": API_KEY,
			"Content-Type": "application/json",
		}
		return {**default_headers, **extra_headers}

	def make_request(self, url, method, headers):
		"""Helper method to make the callback"""
		try:
			resp = request(method, url, headers=headers)
			return resp.json()
		except Exception as e:
			raise Exception(e)

class DataFrame(DataFrame):

	def __init__(
		self,
		data=None,
		index: Optional[Axes] = None,
		columns: Optional[Axes] = None,
		dtype: Optional[Dtype] = None,
		copy: bool = False,
		time_column = None
	):
		"""
		extends DataFrame class
		params:
		:params DataFrame class params: https://github.com/pandas-dev/pandas/blob/master/pandas/core/frame.py#L420
		:param time_column: the name of the column where the creation time of 
			each record will store (optional)
		:type time_column: py:class:str 
		"""

		super().__init__(data,index,columns,dtype,copy)
		self._time_column = "time" if not time_column else time_column
		self._set_row_time()

	def _set_row_time(self):
		"""
		method that update the time of specified column that represent the 
		taken time to build every record through lambda function
		if the column not in the DataFrame the column will be added
		"""
		col = self.columns[0]
		if self._time_column in self.columns:
			self[self._time_column] = self[self._time_column].apply(lambda x: set_time(x, time.time()))
		else:
			self[self._time_column] = self[col].apply(lambda x: set_time(0, time.time()))

class App:
	"""
	class that allows to customize the application workflow
	"""
	def __init__(
		self,
		db_path=None,
		table_name=None,
		if_exists=None,
		file_path=None,
		sha=None
	):
		"""
		params:
		:param db_path: the path or host to sqlite db
		:type db: py:class:str
		:param table_name: the table's name where the data will store
		:type table_name: py:class:str
		:param if_exists: related to param 'if_exists' of pandas function 
		 	`pandas.Datadrame().to_sql` possible options 
		 	`['fail','replace','append']`
		:type if_exists: py:class:str
		:param file_path: the path of the json file where the data will exported
		:type file_path: py:class:str
		:param sha: hash that will be used to encrypt the language
		:type sha: py:class: str or _hashlib.HASH
		"""
		self.db_path = db_path if db_path else "rapidapi.sqlite3"
		self.table_name = table_name if table_name else "rapidapi"
		self.if_exists = if_exists if if_exists else "replace"
		self.file_path = file_path if file_path else "data.json"
		self.sha = sha if sha else "sha1"
		self.mongo_client = MongoClient(
			host=f"{MONGO['host']}:{MONGO['port']}",
			username=MONGO["username"],
			password=MONGO["psw"],
		)

	def _file_formats(self):
		return ['json']
	
	def _to_sql_db_options(self):
		return {
			"name": self.table_name,
			"con": self._sql_engine(),
			"if_exists": self.if_exists
		}
	
	def _sql_engine(self):
		return sqlite3.connect(self.db_path)

	def export_data_to_file(self, df, options={}, file_format=None):
		"""
		weak method that emulates a dispatcher to handle the DataFrame file 
		exporter
		params:
		:param df: pandas dataframe
		:type df: py:class: pandas.DataFrame
		:param options: options to pass to pandas handler function
		:type options: py:class:dict
		:param file_format: the target file format
		:type file_format: py:class:str
		"""

		logging.warning(f"Exporting data to file path: {self.file_path}")
		if not file_format:
			file_format = "json"

		if file_format not in self._file_formats():
			raise Exception(f"File format {file_format} no supported")

		handler = getattr(df,f"to_{file_format}")
		try:
			handler(self.file_path, **options)
			logging.warning("Done...")
		except Exception as e:
			raise Exception(e)

	def pandas_dataframe(self, data, options={}):
		"""
		method that create a dataframe with given data
		params:
		:param data: the data to insert into pandas dataframe
		:type data: supported pandas data type (ndarray,iterable,dict or DataFrame)
		https://pandas.pydata.org/docs/reference/frame.html
		"""
		return DataFrame(data=data, **options)

	def export_to_sql_database(self, df, options={}):
		"""
		method that handle the DataFrame data to sql engine
		params:
		:param df: pandas dataframe
		:type df: py:class: pandas.DataFrame
		:param options: options to pass to pandas handler function
		:type options: py:class:dict
		https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.to_sql.html
		"""
		logging.warning("Saving data into sqlite3 dabatase...")
		if not options:
			raise Exception("No options were provided")

		df.to_sql(**options)
		logging.warning("Done...")

	def export_to_mongo_db(self, df):
		"""
		method that save DataFrame data into mongo db
		:param df: pandas dataframe
		:type df: py:class: pandas.DataFrame
		"""
		logging.warning("Saving data into mongo db ")
		db = self.mongo_client[MONGO["db"]]
		collection = db[self.table_name]
		collection.delete_many({})
		data = json.loads(df.to_json(orient="records"))
		ids = collection.insert_many(data).inserted_ids
		logging.warning("Done...")
		logging.warning(f"Saved {collection.count_documents({})} documents in mongo...") 
		return ids

	def run(self):
		"""
		method that runs the app and handle its flow
		"""
		logging.warning("...Welcome...")
		rapid = RapidApi()
		logging.warning("Making request")
		resp = rapid.make_request(
			ENDPOINTS["all_countries"], "get", rapid._get_headers()
		)

		logging.warning("Done...")
		logging.warning("Creating DataFrame...")

		df = self.pandas_dataframe(
			resp, options={"columns": ["name", "region", "languages"]}
		)

		logging.warning("Fetching language...")

		# hashing languages
		df['language'] = df['languages'].apply(
			lambda x: h.new(self.sha, x[0]['name'].encode("utf-8")).hexdigest()
		)
		# removing unnecessary data
		del df['languages']

		logging.warning(f"Total time: {df[df._time_column].sum()}")
		logging.warning(f"Minimun time: {df[df._time_column].min()}")
		logging.warning(f"Maximum time: {df[df._time_column].max()}")
		logging.warning(f"Average time: {df[df._time_column].mean()}")

		# exporting data to file
		self.export_data_to_file(
			df, options={"orient": "records"}, file_format="json"
		)
		# saving data into sql db
		self.export_to_sql_database(df, options=self._to_sql_db_options())

		# exporting data to mongodb
		self.export_to_mongo_db(df)

		logging.warning("Finished app execution...!")


if __name__ == "__main__":
	app = App()
	app.run()
