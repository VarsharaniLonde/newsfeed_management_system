# The goal is to extract individual news and store these feeds as JSON files by date. The JSON
# file should contain fields such as current_date, story_date, story_time, body, title, source,
# story_id

import newspaper
import datetime
import tldextract
import time
import logging
import concurrent.futures

from .db import get_collection, check_duplicate


def manage_newsfeed(filename):
	links = [line.rstrip('\n') for line in open(filename)]
	with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
		
		futures=[executor.submit(extract_news, link) for link in links]
		# print(futures)
		for future in as_completed(futures):
			print(future.result())
	
        # for future in as_completed(futures):
        #     print(future.result())
  		# r = executor.map(extract_news, links)
  		# print(r.result())
  		# input()

	

def extract_news(link):
	print(link)
	coll = get_collection(collection_name="feeds")
	news = newspaper.build(link)
	source_count = 0
	for category in news.category_urls():	
		cat_paper = newspaper.build(category)	
		for article in cat_paper.articles:
			try:
				feed = newspaper.Article(article.url)
				feed.download()

			except Exception as e:
				print("Timeout occured while downloading  "+article.url+" retrying")
				feed.download()
				time.sleep(2)
				source_count+=1
				continue
				
			parsed_feed, source = parse_data(feed, link)
			feed_json, insert_flag = build_json(parsed_feed, i, source, category)
			if insert_flag == False:
				coll.insert(feed_json)
			source_count+=1
	print(source_count)
	return source_count		

def parse_data(feed, source_link):
	feed.parse()
	feed.nlp()
	feed.text.replace("\n","")	
	temp = tldextract.extract(source_link)
	source = temp.domain
	return feed, source

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


if __name__ == '__main__':
	
	manage_newsfeed("./links.txt")
	