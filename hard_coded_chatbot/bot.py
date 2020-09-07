import pandas as pd
import numpy as np
import time
from nltk.corpus import stopwords
import re, string
import nltk
import random

# load the datasets
df=pd.read_csv("chatbot_data_Q&A - basic_python_questions.csv").dropna(axis=0)

# Remove some uncompleted questions
# if a question or answers end with ":" 
questions=[]
for i in df.question:
    if i[-1]==":":
        questions.append(None)
    else:
        questions.append(i)
        
        
# remove some uncompleted answers
answers=[]
for i in df.answer:
    if i[-1]==":":
        answers.append(None)
    else:
        answers.append(i)
        
# rearrange a little bit
df['answer']=answers
df['question']=questions

df=df.dropna(axis=0).copy()


def clean_text(text):
    text = text.lower()
    text = re.sub(r"i'm", "i am", text)
    text = re.sub(r"he's", "he is", text)
    text = re.sub(r"she's", "she is", text)
    text = re.sub(r"that's", "that is", text)
    text = re.sub(r"what's", "what is", text)
    text = re.sub(r"where's", "where is", text)
    text = re.sub(r"how's", "how is", text)
    text = re.sub(r"\'ll", " will", text)
    text = re.sub(r"\'ve", " have", text)
    text = re.sub(r"\'re", " are", text)
    text = re.sub(r"\'d", " would", text)
    text = re.sub(r"n't", " not", text)
    text = re.sub(r"won't", "will not", text)
    text = re.sub(r"can't", "cannot", text)
    text = re.sub(r'[-()\"#/@;:<>{}`+=~|.!?,]\|', "", text)
    text=text.replace("[\'","").replace("\n"," ").replace("']"," ").replace('["',"").replace('"]',"").replace("it\'s","it's ").replace("\', \'","")
    text=text.replace("\',","").replace("it\'s","it is ").replace("it\\\'s","it is").replace(" \\"," ")
    text=text.replace('",'," ").replace("\',","").replace( ":\',","").replace("here\'s","").replace(":","").replace(',"',"")
    text=text.replace("[","").replace("]","").replace("\'s","'s")
    text=re.sub(r"let's", "let us", text)
    text = text.replace("\'s", "")
    return text


#declare answers and questions
questions=df.question
answers=df.answer
# Cleaning the questions
clean_questions = []
for question in questions:
    clean_questions.append(clean_text(question))
# Cleaning the answers
clean_answers = []
for answer in answers:
    clean_answers.append(clean_text(answer))
    
    
# list contains  punctuation
#sw_list = stopwords.words('english')
sw_list = list(string.punctuation)
sw_list += ["''", '""', '...', '``', '’', '“', '’', '”', '‘', '‘',"'", '©',
'said',"'s", "also",'one',"n't",'com', '-', '–','--' ,
'—', '_']
sw_set = set(sw_list)

# tokenization
def process_data(string):
    tokens = nltk.word_tokenize(string) # tokenization
    punctuation_removed = [token.lower() for token in tokens if token.lower() not in sw_set]
    return punctuation_removed

# Stemming
from nltk.stem import PorterStemmer
ps = PorterStemmer()
# create a function stemming() and loop through each word in a review
def stemming(string):
    stemmed_string=[]
    for w in string:
        stemmed_string.append(ps.stem(w))
    return stemmed_string

# import libraries
from nltk.stem.wordnet import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()

# create a function  and loop through each word in  a review
def lemmatization(string):
    lemma_list=[]
    for word in string:
        lemma_word=lemmatizer.lemmatize(word,pos='v') 
        lemma_list.append(lemma_word)
    return lemma_list

# Conbime all functions above and obtian cleaned text data 
def data_preprocessing(text_data):
    #tokenization, stop words removal, punctuation marks removel
    processed_string=list(map(process_data,text_data))
    # stemming
    stemming_string=list(map(stemming,processed_string))
    # lemmatization
    lemma_string=list(map(lemmatization,stemming_string))
    
    return lemma_string


# create a function of NLP for single line
def NLP(text):
    cleaned_question=clean_text(text)
    processed_question=process_data(cleaned_question)
    stemming_question=stemming(processed_question)
    lemma_question=lemmatization(stemming_question)
    return lemma_question


# List of Greeting , goodbye and thank you you are welcome
greeting=['hey', 'hi', 'hello', 'hey man', 'hi how are you', 'how are you','how is it going', 
          'nice to meet you', 'how are you doing', 'what is up', 'what is new', 
          'what is going on', 'how is everything', 'how are things', 'how is life', 
          'how is your day', 'how is your day going', 'good to see you', 'nice to see you']
goodbye=["see you","bye","byebye","goodbye","I will miss you soon"]

thankyou=["thanks","thank you", "thank you very much"]
yourwelcome=["you are welcome ^.^","my pleasure!","I am happy to help you!"]


# using the function above to process the data 
cleaned_questions=data_preprocessing(clean_questions)


   
    # function - chatbot
def chatbot(question):
   
    if  question.strip().lower() in greeting:
        answer=random.choice(greeting).capitalize()
        return  answer
    elif  question.strip().lower() in goodbye:
        answer=random.choice(goodbye)
        return answer    

    elif question.strip().lower() in thankyou:
        answer= random.choice(yourwelcome).capitalize()
        return  answer
    else:
        # NLP
        pro_text= NLP(question)

        # to find which row has intersection with the words from question you asked
        # which means to find the who have common elements between your question and the data
        inter_list=[]
        for i in cleaned_questions:
            if (set(pro_text) & set(i)):
                inter_list.append((list(set(pro_text) & set(i)),cleaned_questions.index(i)))

        # remove stop words  
        new_inter_list=[]
        for i in range(len(inter_list)):
            for j in inter_list[i][0]:
                if j not in stopwords.words('english'):
                    new_inter_list.append(inter_list[i])

        # find the max length of common elements
        lengths=[len(new_inter_list[i][0]) for i in range(len(new_inter_list)) ]
        

        indexes=[]
        if len(lengths)>0:
            max_length=max(lengths)
            # find all the index whose correspondiong question data have the most common elements
            for i in range(len(new_inter_list)):
                if len(new_inter_list[i][0])==max_length:
                    indexes.append(new_inter_list[i][1])
                    # to find ratios that the keys in a sentence
            ratios=[]
            for i in list(set(indexes)):
                ratio=len(pro_text)/len(questions.iloc[i])
                ratios.append((ratio,i))
                
            final_indexes=[]
            if [ratios[i][0] for i in range(len(ratios))]!=[]:
                max_ratios=max([ratios[i][0] for i in range(len(ratios))])

                for i in range(len(ratios)):
                    if ratios[i][0]==max_ratios:
                        final_indexes.append(ratios[i][1])
            else:
                return "Sorry, I don't know. I need to learn more!"




            if len(final_indexes)>0:
                # to randomly find an answer based on the index
                answer_index=random.choice(final_indexes)
                return answers.iloc[answer_index]
 

            else:
               return "Sorry, I don't know. I need to learn more!"  
                    
        else:
            return "Sorry, I don't know. I need to learn more!"
        