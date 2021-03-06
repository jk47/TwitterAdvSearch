#! usr/bin/python3

from bs4 import BeautifulSoup
import time
from csv import DictWriter
import pprint
import datetime
from datetime import date, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

def init_driver():
	driver = webdriver.Firefox()
	driver.wait = WebDriverWait(driver, 5)
	return driver

def scroll(driver, start_date, end_date):
	url = "https://twitter.com/search?l=en&q=feel%20OR%20feels%20OR%20feeling%20OR%20felt%20since%3A{}%20until%3A{}&src=typd".format(start_date, end_date)
	print(url)
	driver.get(url)
	max_time = 180
	start_time = time.time()  # remember when we started
	while (time.time() - start_time) < max_time:
	    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

def scrape_tweets(driver):
	try:
		tweet_divs = driver.page_source
		obj = BeautifulSoup(tweet_divs, "html.parser")
		content = obj.find_all("div", class_="content")
		dates=[]
		names=[]
		tweet_texts=[]
		for i in content:
			date = (i.find_all("span", class_="_timestamp")[0].string).strip()
			try:
				name = (i.find_all("strong", class_="fullname")[0].string).strip()
			except AttributeError:
				name = "Anonymous"
				
			tweets = i.find("p", class_= "tweet-text").strings
			tweet_text = "".join(tweets)
			# hashtags = i.find_all("a", class_="twitter-hashtag")[0].string
			dates.append(date)
			names.append(name)
			tweet_texts.append(tweet_text)

		data = {
			"date": dates,
			"name": names,
			"tweet": tweet_texts, 
		}

		make_csv(data, start_date)

	except Exception:
		print("Whoops! Something went wrong!")
		driver.quit()

def make_csv(data, start_date):

	l = len(data['date'])
	print("count: %d"%l)
	with open("twitterData.csv", "a+") as file:
		fieldnames = ['Date', 'Name', 'Tweets']
		writer = DictWriter(file, fieldnames = fieldnames)
		writer.writeheader()
		for i in range(l):
			writer.writerow({'Date': data['date'][i],
							'Name': data['name'][i],
							'Tweets': data['tweet'][i],
							})
def get_all_dates(start_date, end_date):
	
	dates = []
	start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
	end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")
	step = timedelta(days=1)
	while start_date <= end_date:
		dates.append(str(start_date.date()))
		start_date += step

	return dates

def main():
	wordsToSearch = input("Enter the words: ").split(',')
	wordsToSearch = wordsToSearch.strip()
	start_date = input("Enter the start date in (Y-M-D): ")
	end_date = input("Enter the end date in (Y-M-D): ")
	all_dates = get_all_dates(start_date, end_date)
	print(all_dates)
	for i in range(len(all_dates)-1):
		driver = init_driver()
		scroll(driver, str(all_dates[i]), str(all_dates[i+1]))
		scrape_tweets(driver)
		time.sleep(5)
		print("The tweets for {} are ready!".format(all_dates[i]))
		driver.quit()	

if __name__ == "__main__":

	main()