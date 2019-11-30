import pymongo


def get_db(db_name="news"):	

	client = pymongo.MongoClient()
	db_instance = client[db_name]
	return db_instance


def get_collection(collection_name="feeds"):
	db = get_db()
	collection = db.collection_name
	# db.members.createIndex( { groupNumber: 1, lastname: 1, firstname: 1 }, { unique: true } )
	return collection


def read_collection(collection_name="feeds"):
	db = get_db()
	collection = db.collection_name
	cursor = collection.find({})
	for document in cursor:
		print(document)


def check_duplicate(title, story_date):
	
	"""
	Returns True if a duplicate exists
	"""
	db = get_db()
	l = db.feeds.find({title: title}).count()
	# if story_date is not None:
	# 	l = db.feeds.find({title: title, story_date_time: story_date}).count()
	# else:
	# 	l = db.feeds.find({title: title}).count()

	return l > 0
