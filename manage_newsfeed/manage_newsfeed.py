import newspaper
import datetime
import tldextract
import time

from .db import get_collection, check_duplicate


def manage_newsfeed(filename):
	links = [line.rstrip('\n') for line in open(filename)]
	for link in links:		
		extract_news(link)		

def extract_news(link):
	coll = get_collection(collection_name="feeds")
	source_dict = {}
	news = newspaper.build(link)
	i = 1
	for category in news.category_urls():
		
		cat_paper = newspaper.build(category)	
		for article in cat_paper.articles:
			try:
				print(article.url)
				feed = newspaper.Article(article.url)
				feed.download()

			except Exception as e:
				print("Timeout occured while downloading  "+article.url+" retrying")
				feed.download()
				time.sleep(2)
				i+=1
				continue
				
			parsed_feed, source, category = parse_data(feed, link)
			feed_json, insert_flag = build_json(parsed_feed, i, source, category)
			if insert_flag == False:
				coll.insert(feed_json)
			i+=1		

def parse_data(feed, source_link):
	feed.parse()
	feed.nlp()
	feed.text.replace("\n","")	
	temp = tldextract.extract(source_link)
	source = temp.domain
	category = temp.subdomain
	print(source, category)
	return feed, source, category

def build_json(feed, i, source, category):

	feed_json = {
	"story_id" : i,
	"current_date_time": datetime.datetime.now(),
	"authors": feed.authors,
	"story_date_time": feed.publish_date,
	"title": feed.title,
	"body": feed.text,
	"source": source,
	"category" : category,
	"video_link": feed.movies,
	"summary": feed.summary,
	"topics": feed.keywords,
	}
	insert_flag = check_duplicate(feed.title, feed.publish_date)	
	return feed_json, insert_flag		



   
# The goal is to extract individual news and store these feeds as JSON files by date. The JSON
# file should contain fields such as current_date, story_date, story_time, body, title, source,
# story_id




if __name__ == '__main__':
	manage_newsfeed("./links.txt")