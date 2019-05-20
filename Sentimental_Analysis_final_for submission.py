import sys,csv,tweepy,re
import twitter
from textblob import TextBlob
import matplotlib.pyplot as plt
from nltk.tokenize import word_tokenize
from string import punctuation 
from nltk.corpus import stopwords 
import csv
import time
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from flask import Flask, render_template, url_for, request

#---------------------------------------------------------------------------------------------------------------------------

# intitializing the twitter account for test data set-----------------
# Parijat's account	
twitter_api = twitter.Api(consumer_key='consumer_key,
		consumer_secret='consumer_secret',
		access_token_key='access_token_key',
		access_token_secret='access_token_secret')
#Rohit's account
twitter_api2 = twitter.Api(consumer_key='consumer_key',
		consumer_secret='consumer_secret',
		access_token_key='access_token_key',
		access_token_secret='access_token_secret')

ProcessedPositive = "C:/Users/CampusUser/Desktop/Sentimental_Analysis_ADBMS/TrainDataSet/processedPositive.csv"
ProcessedNegative = "C:/Users/CampusUser/Desktop/Sentimental_Analysis_ADBMS/TrainDataSet/processedNegative.csv"
ProcessedNeutral = "C:/Users/CampusUser/Desktop/Sentimental_Analysis_ADBMS/TrainDataSet/processedNeutral.csv"

app = Flask(__name__)
app.config["DEBUG"] = True
@app.route('/')

def index():
	return render_template('index.html')
	#print(api.VerifyCredentials())
       # input for term to be searched and how many tweets to search

@app.route('/SentimentAnalysis', methods=['POST'])
def Sentimental():

	#searchTerm = input("Enter Keyword/Tag to search about: ")
	searchTerm = request.form['choosetopic']
	#searchTerm = input("Enter Keyword/Tag to search about: ")
	
	#----------------------------------------------------------------------------------------------------------
	def percentage(part, whole):
		temp = 100 * float(part) / float(whole)
		return format(temp, '.2f')
	
	
	def buildTestSet(searchTerm):
		try:
			tweets_fetched = twitter_api.GetSearch(searchTerm, count = 200)
			return[{"text":status.text, "id":status.id, "label":None} for status in tweets_fetched]
		except:
			print("Unfortunately, something went wrong..")
			return None
	#--------------------------------------------------------------------------------------
	
	#Preprocessing test data and training data----------------------------------------
	testDataSet = buildTestSet(searchTerm)
	#print(testDataSet)
	countTest = 0
	# now we write them to the empty CSV file
	with open('testDataFile.csv','w', newline='') as csvfile:
		linewriter = csv.writer(csvfile,delimiter=',',quotechar="\"")
		for tweet in testDataSet:
			try:
				countTest = countTest+1
				linewriter.writerow([tweet["id"], tweet["text"]])
			except Exception as e:
				print(e)
	
	#print(countTest)
	data = []
	data_label=[]
	trainingDataSet = []
	countTrain = 0
	with open(ProcessedPositive,'r') as csvfile:
	
		lineReader = csv.reader(csvfile,delimiter=',')
		for row in lineReader:
			trainingDataSet.append({"text":row[0], "label":"positive"})
			data.append(row[0])
			data_label.append('positive')
			countTrain = countTrain + 1
	
	with open(ProcessedNegative,'r') as csvfile:
		lineReader = csv.reader(csvfile,delimiter=',')
		for row in lineReader:
			trainingDataSet.append({"text":row[0], "label":"negative"})
			data.append(row[0])
			data_label.append('negative')
			countTrain = countTrain + 1
	
	with open(ProcessedNeutral,'r') as csvfile:
		lineReader = csv.reader(csvfile,delimiter=',')
		for row in lineReader:
			trainingDataSet.append({"text":row[0], "label":"neutral"})
			data.append(row[0])
			data_label.append('neutral')		
			countTrain = countTrain + 1
	
	#print (countTrain)
	
	
	
	#---------------------------------------------------------------------------------
	
	def plotPieChart(positive,negative,neutral, searchTerm, noOfSearchTerms):
		labels = ['Positive [' + str(positive) + '%]','Neutral [' + str(neutral) + '%]','Negative [' + str(negative) + '%]']
		sizes = [positive, neutral, negative]
		colors = ['green','blue', 'red']
		patches, texts = plt.pie(sizes, colors=colors, startangle=90)
		plt.legend(patches, labels, loc="best")
		plt.title('How people are reacting on ' + searchTerm + ' by analyzing ' + str(noOfSearchTerms) + ' Tweets.')
		plt.axis('equal')
		plt.tight_layout()
		plt.show()
	
	
	# --------------------------------------------------------------------------------
	# NAIVE BAYES
	#---------------------------------------------------------------------------------			
	
	class PreProcessTweets:
		def __init__(self):
			self._stopwords = set(stopwords.words('english') + list(punctuation) + ['AT_USER','URL'])
	        
		def processTweets(self, list_of_tweets):
			processedTweets=[]
			for tweet in list_of_tweets:
				processedTweets.append((self._processTweet(tweet["text"]),tweet["label"]))
			return processedTweets
	    
		def _processTweet(self, tweet):
			tweet = tweet.lower() # convert text to lower-case
			tweet = re.sub('((www\.[^\s]+)|(https?://[^\s]+))', 'URL', tweet) # remove URLs
			tweet = re.sub('@[^\s]+', 'AT_USER', tweet) # remove usernames
			tweet = re.sub(r'#([^\s]+)', r'\1', tweet) # remove the # in #hashtag
			tweet = word_tokenize(tweet) # remove repeated characters (helloooooooo into hello)
			return [word for word in tweet if word not in self._stopwords]
	
	
	tweetProcessor = PreProcessTweets()
	preprocessedTrainingSet = tweetProcessor.processTweets(trainingDataSet)
	preprocessedTestSet = tweetProcessor.processTweets(testDataSet)
	#print(preprocessedTestSet[0:5])
	#print(preprocessedTrainingSet[0:20])
	
	
	import nltk 
	
	def buildVocabulary(preprocessedTrainingData):
		all_words = []
		
		for (words, sentiment) in preprocessedTrainingData:
		    all_words.extend(words)
		
		wordlist = nltk.FreqDist(all_words)
		word_features = wordlist.keys()
		
		return word_features
	
	# ------------------------------------------------------------------------
	
	def extract_features(tweet):
		tweet_words=set(tweet)
		features={}
		for word in word_features:
			features['contains(%s)' % word]=(word in tweet_words)
		return features 
	
	# ------------------------------------------------------------------------
	
	# Now we can extract the features and train the classifier 
	word_features = buildVocabulary(preprocessedTrainingSet)
	#print(word_features)
	trainingFeatures=nltk.classify.apply_features(extract_features,preprocessedTrainingSet)
	#print(trainingFeatures)
	
	# ------------------------------------------------------------------------
	
	NBayesClassifier=nltk.NaiveBayesClassifier.train(trainingFeatures)
	#print(NBayesClassifier)
	
	# ------------------------------------------------------------------------
	
	NBResultLabels = [NBayesClassifier.classify(extract_features(tweet[0])) for tweet in preprocessedTestSet]
	
	# ------------------------------------------------------------------------
	
	# get the majority vote
	#if NBResultLabels.count('positive') > NBResultLabels.count('negative'):
	positiveNB = 100*NBResultLabels.count('positive')/len(NBResultLabels)
	negativeNB = 100*NBResultLabels.count('negative')/len(NBResultLabels)
	neutralNB = 100*NBResultLabels.count('neutral')/len(NBResultLabels)
	
	
	#---------------------------------------------------------------------------
	#SVM
	#-----------------------------------------------------------------------------
	
	
	#---------------------------------------------------------------------------------
	Test= "C:/Users/CampusUser/Desktop/Sentimental_Analysis_ADBMS/testDataFile.csv"
	testDataSet = []
	def buildTestSet():
		try:
			with open(Test,'r') as csvfile:
	
				lineReader = csv.reader(csvfile,delimiter=',',quotechar="\"")
				for row in lineReader:
					testDataSet.append(row[1])
			
		except:
			print("Unfortunately, something went wrong..")
			
	
	buildTestSet()
	
	vectorizer = CountVectorizer(
		analyzer = 'word',
		lowercase = False,
		)
		
	features = vectorizer.fit_transform(
		data
		)
	features_nd = features.toarray()
	
	
	X_train= features_nd
	y_train= data_label
	features_test = vectorizer.transform(
		testDataSet
		)
	features_tst= features_test.toarray()
	X_test = features_tst
	#print(X_test)
	log_model = LogisticRegression()
	log_model = log_model.fit(X=X_train, y=y_train)
	y_pred = log_model.predict(X_test)
	#print(y_pred)
	#print(y_pred[53])
	#print(accuracy_score(y_test, y_pred))
	count = 0
	countpos = 0
	countneu = 0
	countneg = 0
	countn = 0
	limit=y_pred.size
	for count in range(limit):
		
		#print(y_pred[count])
		if y_pred[count] == "positive":
			countpos = countpos + 1
		if y_pred[count] == "negative":
			countneg = countneg + 1
		if y_pred[count] == "neutral":
			countneu = countneu + 1			
		count = count + 1
		
	#print(count)	
	#print(countpos)	
	#print(countneg)	
	perpos = percentage(countpos, count)
	perneg = percentage(countneg, count)
	#countneu = count-(countpos+countneg)
	perneu = percentage(countneu, count)	
	#-------------------------------------------------------------------------
	
	#-----------------------------------------------------------------------------
	#NLP
	#-----------------------------------------------------------------------------
	
	NoOfTerms = 200
	def cleanTweet(tweet):
		# Remove Links, Special Characters etc from tweet
		return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t]) | (\w +:\ / \ / \S +)", " ", tweet).split())
	
	# function to calculate percentage
	
	
	tweets = []
	tweetText = []
	consumerKey = '7kAc3CIJs8kl8lo6GqmFGPRsr'
	consumerSecret = 'FTiQ9uDvP9qSSC2MtWRnEgBrvNFu7bQbbvFVT3tPQuqupi3Vtu'
	accessToken = '1077619320161656832-dDiWhk8200dfxbfv2I86dXDi9DPQt2'
	accessTokenSecret = 'Jlpr1hmCFggiWinScS8ONF5BeCqjczXyGXYwjyBNfi3QN'
	auth = tweepy.OAuthHandler(consumerKey, consumerSecret)
	auth.set_access_token(accessToken, accessTokenSecret)
	api = tweepy.API(auth)
	# searching for tweets
	tweets = tweepy.Cursor(api.search, q=searchTerm, lang = "en").items(200)
	# creating some variables to store info
	polarity = 0
	positive = 0
	wpositive = 0
	spositive = 0
	negative = 0
	wnegative = 0
	snegative = 0
	neutral = 0
	
	
	   # iterating through tweets fetched
	for tweet in tweets:
	       #Append to temp so that we can store in csv later. I use encode UTF-8
		tweetText.append(cleanTweet(tweet.text).encode('utf-8'))
		#print (tweet.text)    #print tweet's text
		analysis = TextBlob(tweet.text)
	       # print(analysis.sentiment)  # print tweet's polarity
		polarity += analysis.sentiment.polarity  # adding up polarities to find the average later
		
		if (analysis.sentiment.polarity == 0):  # adding reaction of how people are reacting to find average later
			neutral += 1
		elif (analysis.sentiment.polarity > 0 and analysis.sentiment.polarity <= 1):
			positive += 1
		elif (analysis.sentiment.polarity > -1 and analysis.sentiment.polarity < 0):
			negative += 1
		  
	
	# finding average of how people are reacting
	positiveNLP = percentage(positive, NoOfTerms)
	negativeNLP = percentage(negative, NoOfTerms)
	neutralNLP = percentage(neutral, NoOfTerms)
	# finding average reaction
	polarity = polarity / NoOfTerms
	
	#--------------------------------------------------------------------------------------------
	#Printing
	#--------------------------------------------------------------------------------------------
	
	# printing out data
	print("How people are reacting on " + searchTerm + " by analyzing " + str(NoOfTerms) + " tweets.")
	print()
	print("General Report: ")
	
	if (polarity == 0):
	    print("Neutral")
	elif (polarity > 0 and polarity <= 1):
	    print("Positive")
	elif (polarity > -1 and polarity < 0):
	    print("Negative")
		
	searchTerm1 = searchTerm + " (in NLP)"
	
	plotPieChart(positiveNLP, negativeNLP, neutralNLP, searchTerm1, NoOfTerms)
	
	searchTerm1 = searchTerm + " (in NaiveBayes)"
	plotPieChart(positiveNB, negativeNB, neutralNB, searchTerm1, NoOfTerms)
	
	searchTerm1 = searchTerm + " (in SVM)"		
	plotPieChart(perpos, perneg, perneu, searchTerm1, NoOfTerms)
	
	print()
	print("Detailed Report: As per NLP")
	print(str(positiveNLP) + "% people thought it was positive")
	print(str(negativeNLP) + "% people thought it was negative")
	print(str(neutralNLP) + "% people thought it was neutral")
	print()
	print("Detailed Report: As per NaiveBayes")
	print("Positive Sentiment Percentage = " + str(positiveNB) + "%")
	print("Negative Sentiment Percentage = " + str(negativeNB) + "%")
	print("Neutral Sentiment Percentage = " + str(neutralNB) + "%")
	print()
	print("Detailed Report: As per SVM")
	print("Positive Sentiment Percentage = " + str(perpos) + "%")
	print("Negative Sentiment Percentage = " + str(perneg) + "%")
	print("Neutral Sentiment Percentage = " + str(perneu) + "%")
	
	return render_template("pass.html", positiveNLP=positiveNLP, negativeNLP=negativeNLP, neutralNLP=neutralNLP, positiveNB=positiveNB, negativeNB=negativeNB, neutralNB=neutralNB, perpos=perpos, perneg=perneg, perneu=perneu)
		
		
app.run(host="127.0.0.1", port="5000", debug=True)
	



