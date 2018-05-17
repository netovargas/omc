## STRUCTURE
#
#	Connect to airtable and request last 60 things
#	Loop through and call mercury api
#   parameter = url from airtable
#   gather: title, lead image, excerpt, word count, reading time
#   save into dict with all info
# 
#  Take dict and put it back into airtable
#  Take dict and save it as text file into Amazon S3
#
#  Amazon S3 file is just a container for reading the static
#  text file with all the info.

import requests
import time
import json
import config
import boto3

def main():
	airtableupdate()
	filename = airtableJsonOutput()
	uploadToS3(filename)

def uploadToS3(filename):
	s3 = boto3.client('s3',
         aws_access_key_id = config.aws_access_key_id,
         aws_secret_access_key = config.aws_secret_access_key)

	bucketname = 'onemancult.co'

	s3.upload_file(filename, bucketname, filename)
    	

def airtableupdate():
	# Set up Airtable headers, API call URL and paramters
	headers = {
		'Authorization': config.airtable_api_key
	}
	recordCount = 60
	baseApiUrl = "https://api.airtable.com/v0/appleEv8lPCl3jhFw/articles"
	parameter = "?filterByFormula=Posted%3D0&maxRecords=" + str(recordCount) + "&sort%5B0%5D%5Bfield%5D=Created+Time&sort%5B0%5D%5Bdirection%5D=desc"

	# Make API get request to get URLs of entries not posted
	r = requests.get(baseApiUrl + parameter, headers=headers)
	rjson = r.json()

	# Set up PUT request headers and auxiliary variables
	recordUrl = ""
	fieldDict = {}
	headers = {
		'Authorization': config.airtable_api_key,
		'Content-Type': 'application/json'
	}

	# Iterate through URLs from GET request
	dictLength = len(rjson['records'])
	for indexNum in range (0, dictLength, 1):
		recordUrl = rjson['records'][indexNum]['fields']['Url']
		type = rjson['records'][indexNum]['fields']['Type']
		# Pass URL to Mercury API to get link information
		fieldDict = mercurycall(recordUrl)
		# Set up API PUT request to update table
		fieldDict.update(
		{
			"Url": rjson['records'][indexNum]['fields']['Url'],
			"Posted": 1,
			"Type": type
		})
		payload = {
		"fields": fieldDict
		}
		parameter = "/" + rjson['records'][indexNum]['id']
		# Make request
		r = requests.put(
			baseApiUrl + parameter,
			headers=headers,
			data=json.dumps(payload)
			)
		# Print response in case something went wrong
		#print r
		# API has limit of 5 calls per second, wait so it doesn't
		# time out.
		time.sleep(.25)

def airtableJsonOutput():
	# Create and open csv file and write header
	filename = 'articledata.json'
	jsonFile = open(filename, "wb")

	# Set up Airtable headers and API call URL
	headers = {
		'Authorization': config.airtable_api_key
	}

	# Set up API call to retrieve complete records.
	baseApiUrl = "https://api.airtable.com/v0/appleEv8lPCl3jhFw/tblFbKbLEGWoqe3R3"
	#Parameters
	#Fields: Url, Title, Reading Time, Created Time, Type
	#Formula Filter: Posted = 1
	#Max Records = 60
	#Sort = By Created Time, descending
	# URL Encoder - https://codepen.io/airtable/full/rLKkYB?baseId=appleEv8lPCl3jhFw&tableId=tblFbKbLEGWoqe3R3
	parameter = "?fields%5B%5D=Url&fields%5B%5D=Title&fields%5B%5D=Reading+Time&fields%5B%5D=Created+Time&fields%5B%5D=Type&filterByFormula=Posted+%3D+1&maxRecords=60&sort%5B0%5D%5Bfield%5D=Created+Time&sort%5B0%5D%5Bdirection%5D=desc"

	# Make request
	r = requests.get(baseApiUrl + parameter, headers=headers)
	rjson = r.json()
	dictLength = len(rjson['records'])
	outputDict = {}

	# Iterate through response and save each line to JSON
	for indexNum in range (0, dictLength, 1):
		#fieldCount = len(rjson['records'][indexNum]['fields'])
		title = rjson['records'][indexNum]['fields']['Title']
		url = rjson['records'][indexNum]['fields']['Url']
		readTime = rjson['records'][indexNum]['fields']['Reading Time']
		type = rjson['records'][indexNum]['fields']['Type']
		createdTime = rjson['records'][indexNum]['fields']['Created Time']
		outputDict.update({
			indexNum: {
				"title": title,
				"url": url,
				"readTime": readTime,
				"type": type,
				"createdTime": createdTime
			}
			})

	print json.dump(outputDict,jsonFile)
	#jsonFile.write()
	jsonFile.close()

	return filename

def mercurycall(airtableUrl):
	headers = {
	'x-api-key': config.mercury_api_key
	}

	baseApiUrl = "https://mercury.postlight.com/parser?url="
	parameter = airtableUrl

	r = requests.get(baseApiUrl + parameter, headers=headers)

	rjson = r.json()

	wordcount = rjson.get('word_count', -1)
	if wordcount < 200:
		wordcount = -1
		readtime = -1
	else:
		readtime = wordcount/200

	fieldDict = {
		"Title": rjson.get('title', 'error'),
		"Lead Image": rjson.get('lead_image_url', 'error'),
		"Excerpt": rjson.get('excerpt', 'error'),
		"Word Count": wordcount,
		"Reading Time": readtime,
	}

	return fieldDict

if __name__ == "__main__":
	main()

