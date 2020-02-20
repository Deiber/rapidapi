# rapidapi

Simple python app that query regions, countries and their first language from [REST-COUNTRY-ENDPOINT], hashing it
using tools such as [Pandas] and [MongoDB]

For more details you can check out the [CHANAGELOG](https://github.com/Deiber/rapidapi/blob/master/CHANGELOG.md)

## Installation

 1. Clone the repository via `https` open a command line terminal and type:

 	```
 	git clone https://github.com/Deiber/rapidapi.git
 	```

 2. Install [docker] and [docker-compose] libraries

 3. Go to root project path `cd <path-to-your-root-folder>` 

 4. Create the local image for the project

 	```
 	docker build -t rapidapi .
 	```

 	**Note:** if you want to change the image's name, you have to also modify the 
 	file `docker-compose.yml`, by default, the image's name is `rapidapi`

 5. Run your container and up your app service

	```
	docker-compose up rapidapi
	```

 6. Run tests typing the command `docker-compose run tests`


# Debug your code

  If you want to bebug your code, you can use break points throug [wdb],
  this will start a session debug for your break point that will available
  on your browser in your [local host](http://localhost:1984/)

  **Example**
  
  ```
  import wdb; wdb.set_trace()
  print("Hello World!")
  ```

### Useful links:

 - [MongoDB] - Mongodb
 - [Pandas] - Pandas
 - [Py-Mongo] - Py-Mongo
 - [REST-COUNTRY-ENDPOINT] - Rest Countries
 
 [MongoDB]: <https://www.mongodb.com/>
 [Pandas]: <https://pandas.pydata.org/docs/>
 [Py-Mongo]: <https://pymongo.readthedocs.io/en/stable/>
 [REST-COUNTRY-ENDPOINT]: <https://restcountries.eu/rest/v2/all>
 [Docker]: <https://docs.docker.com/>
 [Docker-Compose]: <https://docs.docker.com/compose/install/>
 [Python-OAuth2-Mongo]: <https://python-oauth2.readthedocs.io/en/latest/_modules/oauth2/store/mongodb.html>
 [wdb]: <https://hub.docker.com/r/kozea/wdb>