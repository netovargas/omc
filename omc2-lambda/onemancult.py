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

import config
import json
import sys
import time
from os import name, system, path

import boto3
import requests

reload(sys)
sys.setdefaultencoding('utf-8')

def clear():
    # for windows
    if name == 'nt':
        _ = system('cls')
    # for mac and linux(here, os.name is 'posix')
    else:
        _ = system('clear')

def main():
	prompt = """Select the mode you want to run by entering the number
	associated with each option below.
	1 - Update Airtable from Mercury API
	2 - Regenerate JSON file from Airtable
	3 - Submit JSON file to One Man Cult website (AWS)
	4 - *Update Airtable, generate JSON file and submit
		to AWS (full workflow)*
	5 - Submit email to Mailchimp subscribers
	p - Print options again
	q - Quit"""
	print (prompt)

	response = -1
	while (response != 'q'):
		response = raw_input("Option: ")
		
		if (response == '1'):
			# Update the Airtable base with the article information by
			# running all articles that are missing data through the
			# Mercury API.
			airtableupdate()
			print ('\n\n' + prompt)
		elif (response == '2'):
			# Generates a JSON file with the article data from Airtable
			# and saves it to the same directory as this file. Does not
			# submit the file to the S3 bucket.
			airtableJsonOutput()
			print ('\n\n' + prompt)
		elif (response == '3'):
			# Note: This option assumes the filename is articledata.json
			# and is in the directory of this file.
			#
			# This will submit the file that is in this directory to the
			# S3 bucket.
			filename = 'articledata.json'
			uploadToS3(filename)
			print ('\n\n' + prompt)
		elif (response == '4'):
			# This option will update the Airtable base using Mercury,
			# generate a JSON file from it and then submit that file to
			# the S3 AWS bucket. This option is the same as the original
			# script.
			airtableupdate()
			filename = airtableJsonOutput()
			uploadToS3(filename)
			print ('\n\n' + prompt)
		elif (response == '5'):
			print ("This option has not been implemented yet. You can choose another one.")
		elif (response == 'q'):
			exit()
		elif (response == 'p'):
			print (prompt)
		else:
			print ("Invalid response. Please enter another option from the ones above.")

def main2():
	airtableupdate()
	filename = airtableJsonOutput()
	uploadToS3(filename)

def uploadToS3(filename):
	print ("\nCreating connection to AWS S3 (www.onemancult.co).")
	filename_path = path.dirname(path.realpath(__file__)) + '/' + filename
	s3 = boto3.client('s3',
         aws_access_key_id = config.aws_access_key_id,
         aws_secret_access_key = config.aws_secret_access_key)

	bucketname = 'www.onemancult.co'

	s3.upload_file(filename_path, bucketname, filename)
	print ("JSON file uploaded to S3 bucket.")
    	
def airtableupdate():
	# Set up Airtable headers, API call URL and paramters
	headers = {
		'Authorization': config.airtable_api_key
	}
	recordCount = 60
	baseApiUrl = "https://api.airtable.com/v0/appleEv8lPCl3jhFw/articles"
	parameter = "?filterByFormula=Posted%3D0&maxRecords=" + str(recordCount) + "&sort%5B0%5D%5Bfield%5D=Created+Time&sort%5B0%5D%5Bdirection%5D=desc"

	# Make API get request to get URLs of entries not posted
	print ("Fetching URLs of unposted links.")
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
	print ("Updating Airtable with link information.")
	for indexNum in range (0, dictLength, 1):
		recordUrl = rjson['records'][indexNum]['fields']['Url']
		type = rjson['records'][indexNum]['fields']['Type']
		# Pass URL to Mercury API to get link information
		fieldDict = mercurycall(recordUrl)
		# Set up API PUT request to update table
		posted = 0
		if ('Title' in fieldDict.keys()):
			# Only mark links as posted if we were able to get a
			# title.			
			posted = 1
		else:
			fieldDict['Title'] = "Error - Needs manual edit."
		fieldDict.update(
		{
			"Url": rjson['records'][indexNum]['fields']['Url'],
			"Posted": posted,
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
		print (" URL: " + str(fieldDict['Url'])[0:49] + "... - " + fieldDict['Type'])
		print (" Title: " + fieldDict['Title'])
		print (" Reading Time: " + str(fieldDict['Reading Time']))
		print (" Excerpt: " + str(fieldDict['Excerpt'])[0:64] + "...")
		print ("")
		time.sleep(.25)

def airtableJsonOutput():
	# Create and open json file and write header
	filename = path.dirname(path.realpath(__file__)) + '/articledata.json'
	jsonFile = open(filename, 'wb')
	print ("Updating JSON file from Airtable.")

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
	parameter = "?fields%5B%5D=Url&fields%5B%5D=Title&fields%5B%5D=Reading+Time&fields%5B%5D=Created+Time&fields%5B%5D=Type&fields%5B%5D=Excerpt&filterByFormula=Posted+%3D+1&maxRecords=60&sort%5B0%5D%5Bfield%5D=Created+Time&sort%5B0%5D%5Bdirection%5D=desc"

	# Make request
	print ("Requesting most recent data from Airtable.")
	r = requests.get(baseApiUrl + parameter, headers=headers)
	rjson = r.json()
	dictLength = len(rjson['records'])
	outputDict = {}

	# Iterate through response and save each line to JSON
	for indexNum in range (0, dictLength, 1):
		print (str(indexNum+1) + "..."),
		title = rjson['records'][indexNum]['fields']['Title']
		url = rjson['records'][indexNum]['fields']['Url']
		readTime = rjson['records'][indexNum]['fields']['Reading Time']
		type = rjson['records'][indexNum]['fields']['Type']
		createdTime = rjson['records'][indexNum]['fields']['Created Time']
		excerpt = rjson['records'][indexNum]['fields']['Excerpt']
		outputDict.update({
			indexNum: {
				"title": title,
				"url": url,
				"readTime": readTime,
				"type": type,
				"createdTime": createdTime,
				"excerpt": excerpt
			}
			})

	#print json.dump(outputDict,jsonFile)
	json.dump(outputDict, jsonFile)
	#jsonFile.write(json.dump(outputDict, jsonFile))
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
