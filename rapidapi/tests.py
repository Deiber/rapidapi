import unittest
from pymongo import MongoClient
from app import RapidApi, App
import pandas as pd
import os

class CommonTestCase(unittest.TestCase):
	def setUp(self):
		self.app = App(
			db_path="rapidapi_test.sqlite3",
			file_path="test.json"
		)
		self.data = [
			{"game": "pokemon","level":1,"max_points":200,"player": "me"},
			{"game": "pokemon","level":2,"max_points":100,"player": "you"}
		]
		self.df = self.app.pandas_dataframe(self.data)

class TestRapidApi(CommonTestCase):
	def setUp(self):
		super().setUp()

	def test_df_time_field(self):
		"""checking field 'Time' in the DataFrame"""
		self.assertTrue("Time" in self.df.columns, "Column 'Time' not in dataframe")
		self.assertTrue(len(self.df["player"])==2, f"DataFrame contains {len(self.df['player'])} rows, sould be 2")

	def test_json_file(self):
		"""test exporting data to json file"""
		cols = self.data[0].keys()
		self.app.export_data_to_file(self.df, options={"orient": "records"})
		jdf = pd.read_json(self.app.file_path)
		self.assertTrue(self.df[cols].equals(jdf[cols]), "DataFrames are not equals")

	def test_export_to_sql(self):
		"""test exporting data to sql"""
		self.app.export_to_sql_database(self.df, options=self.app._to_sql_db_options())
		cnn = self.app._sql_engine()
		cr = cnn.cursor()
		recs = cr.execute(f"SELECT * FROM {self.app.table_name};").fetchall()
		self.assertEqual(len(recs), len(self.data), "Length data mismatch")
		self.assertEqual(recs[0][4],self.data[0]["player"])

	def test_export_to_mongo(self):
		ids = self.app.export_to_mongo_db(self.df)
		self.assertFalse(len(self.data) != len(ids),"Incomplete save collection")
		db_name = os.environ["MONGO_DB"]
		collection = self.app.mongo_client[db_name][self.app.table_name]
		x = collection.find_one({"_id":ids[0]})
		self.assertTrue(x)
		self.assertEqual(x["player"], self.data[0]["player"])

if __name__ == "__main__":
	unittest.main()