# importing all required packages
# %pip install pandas, requests, bs4, nltk, re
import pandas as pd
import requests
from bs4 import BeautifulSoup
import os
import string
import nltk
nltk.download('punkt')
nltk.download('brown')
nltk.download('stopwords')
from nltk.tokenize import word_tokenize
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
import re

#reading the excel file to a pandas dataframe
df = pd.read_excel('Input.xlsx')

#iterating over the dataframe
for idx, row in df.iterrows():
    url_id = row['URL_ID']
    url = row['URL']
    
    #requesting url data through get
    res = requests.get(url)
    #creating a BeautifulSoup object on the url requested text data
    html = BeautifulSoup(res.text, 'html')
    
    #Capture the title of the url page, which is under the <h1> tag and 'entry-title' class
    #If we are unable to extract the title, we will skip that url
    try:
        title = html.find('h1', class_='entry-title').text
    except:
        continue
    
    #Capture the text content of the url page, which is under the <div> tag and 'td-post-content tagdiv-type' class
    #If we are unable to extract the text, we will skip that url
    try:
        article_text = html.find('div', class_='td-post-content tagdiv-type').text
    except:
        continue
    
    #Creating a new file with the url_id as the title of the file
    with open("./text_file/{}.txt".format(url_id), 'w') as file:
        try:
            file.write("{}\n{}".format(title,article_text))
        except:
            file.write("{}\n{}".format(title,article_text.encode('utf-8'))) #this encoding is in case the text contains characters that require encoding (U+204)
          
#creating a set of stopwords from the nltk stopwords corpus and the files in Stopword diretory
stopwords = set(stopwords.words('english'))
for files in os.listdir('./StopWords'):
    with open(os.path.join('./StopWords',files), 'r', encoding='ISO-8859-1') as file:
        stopwords.update(set(file.read().lower().splitlines()))
stopwords.update(set(string.punctuation)) #We also added the punctuations from string to the stopword set

#tokenizing and cleaning the text data (using the stopwords)
clean_text = []
for files in os.listdir('./text_file'):
    with open(os.path.join('./text_file/', files), 'r') as file:
        text = file.read()
        text = text.replace('\\n', ' ')
        
        words = word_tokenize(text) #nltk word tokenizer is a very efficient and fast tokenizer
        
        use_text = [word for word in words if word.lower() not in stopwords] #the list of words excluding the stopwords
        clean_text.append(use_text)

#Set of positive and negative words
with open('./MasterDictionary/positive-words.txt','r', encoding='ISO-8859-1') as file:
    pos = set(file.read().splitlines())
with open('./MasterDictionary/negative-words.txt','r', encoding='ISO-8859-1') as file:
    neg = set(file.read().splitlines())

#intializing required variables
positive_words = []
negative_words = []
positive_score = []
negative_score = []
polarity_score = []
subjectivity_score = []

#iterate throught the previously made corpus of cleaned words to check if they are positive or negative
for i in range(len(clean_text)):
    positive_words.append([word for word in clean_text[i] if word.lower() in pos])
    negative_words.append([word for word in clean_text[i] if word.lower() in neg])
    positive_score.append(len(positive_words[i]))
    negative_score.append(len(negative_words[i]))
    polarity_score.append((positive_score[i] - negative_score[i]) / (positive_score[i] + negative_score[i] + 0.000001))
    subjectivity_score.append((positive_score[i] + negative_score[i]) / (len(clean_text[i]) + 0.000001))

#function to find the number of complex words, takes a list of words or string as input and returns the count of complex words
def count_complex_words(words):
    complex_words = []
    for word in words:
            vowels = 'aeiou'
            syllable_count = sum(1 for char in word if char in vowels)
            if syllable_count>2:
                complex_words.append(word)
    return len(complex_words)

#function to find the number of syllable in each text, takes a list of words or string as input and returns the count of total syllable
def count_syllable(words):
    syllable_count = 0
    for word in words:
        if word.endswith('es'):
            word = word[:-2]
        elif word.endswith('ed'):
            word = word[:-2]
        vowels = 'aeiou'
        syllable_count_word = sum( 1 for letter in word if letter.lower() in vowels)
        syllable_count += syllable_count_word
    return syllable_count

#function to count the personal pronouns, takes a string or list of words and returns the count of pronouns
def count_pronouns(text):
    pronouns = ["I", "we", "my", "ours", "us", "We", "My", "Ours", "Us"]
    count = 0
    for pronoun in pronouns:
        count += len(re.findall(r"\b" + pronoun + r"\b", text))
    return count

#intializing required variables
avg_sentence_length = []
percentage_of_complex_words  =  []
Fog_Index = []
complex_word_count =  []
syllable_per_word = []
avg_words_per_sentence = []
avg_word_length = []
pronoun_count = []

i=0       #counter for the iterative access to the clean_text list

#iterate through the files
for files in os.listdir('./text_file'):
    with open(os.path.join('./text_file/', files), 'r') as file:
        text = file.read()
        text = text.replace('\\n', ' ')
        
        #the sent_tokenizer splits or creates tokens of the text into proper sentences
        sentences = sent_tokenize(text)
        sent_count = len(sentences)  #count of total senteces in the given text of the file
        word_count = len(clean_text[i])  #count of total words in the text file. We had already cleaned and stored the words in clean_text
        
        char_count = 0       #variable for the total count of character in a text file
        for word in clean_text[i]:
            char_count+= len(word)
        
        complex_word_count.append(count_complex_words(clean_text[i]))
        
        syllable_per_word.append(count_syllable(clean_text[i]))
        
        #adding the values to the list
        avg_sentence_length.append(word_count/sent_count)
        percentage_of_complex_words.append(complex_word_count[i]/word_count)
        Fog_Index.append(0.4*(avg_sentence_length[i]+percentage_of_complex_words[i]))
        avg_words_per_sentence.append(word_count/sent_count)
        avg_word_length.append(char_count/word_count)
        
        pronoun_count.append(count_pronouns(text))
        
        i+=1


# URL 36 and 49 through error status code
# While these URL were uable to provide a parsable title to BeautifulSoup 14,20,29,43,83,84,92,99,100
# Therefore, they must be removed from the output dataframe

#reading the structure of the output file
output_df = pd.read_excel('./Output Data Structure.xlsx')

#droping the above mentioned urls, we minus one(1) from the index as it is 0-based indexing
drop_index = [drop-1 for drop in [14,20,29,36,43,49,83,84,92,99,100]]

output_df.drop(drop_index, inplace=True)

#storing the final output variables
output_variables = [positive_score,
                    negative_score,
                    polarity_score,
                    subjectivity_score,
                    avg_sentence_length,
                    percentage_of_complex_words,
                    Fog_Index,
                    avg_words_per_sentence,
                    complex_word_count,
                    word_count,
                    syllable_per_word,
                    pronoun_count,
                    avg_word_length]

#wrting the final values to the dataframe
for i, var in enumerate(output_variables):
  output_df.iloc[:,i+2] = var

#creating a Output.csv file to save the output in the mentioned structure
output_df.to_csv('Output.csv')