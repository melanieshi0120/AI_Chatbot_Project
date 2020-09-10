# Scrape imports
import requests
import praw
from bs4 import BeautifulSoup as bs

# Trying not to be trottled imports
import time

# Writing files imports
import pandas as pd

class QAScraper:
    def __init__(self):
        self.reddit = None
        self.questions = []
        self.answers = []
        
    def set_reddit(self, config):
        '''
        Method to use reddit to get questions and answers for topics
        
        Parameters
        ----------
        config: Dictionary of containing client_id, client_secret, username, password, and user_agent
        '''
        self.reddit = praw.Reddit(
            client_id = config['client_id'],
            client_secret = config['client_secret'],
            username = config['username'],
            password = config['password'],
            user_agent = config['user_agent'],
        )
    
    # Helper function to extract posts in a single subreddit
    def _extract_reddit(self, sub):
        subreddit = self.reddit.subreddit(sub)
        hot = subreddit.hot(limit=100)
        
        title_reply = []
        for submission in hot:
            if not submission.stickied:
                comments = submission.comments
                for comment in comments:
                    try:
                        title_reply.append({
                            'body': comment.body,
                            'reply': [ reply.body for reply in comment.replies ],
                        })                 
                    except:
                        pass

        questions = []
        answers = []
        for i in range(len(title_reply)):
            questions.append(list(title_reply)[i]['body'])
            answers.append(list(title_reply)[i]['reply']) 

        return questions, answers
    
    def get_reddit(self, subs):
        '''
        Method to add questions and answers from list of subreddits
        
        Parameters
        ----------
        subs: List of subreddits (strings) for getting posts
        '''
        assert type(subs) == list, 'Subreddits must be list of strings'
        
        success = []
        failure = []
        for sub in subs:
            try:
                q, a = self._extract_reddit(sub)
                success.append(f'{sub}')
                self.questions.append(q)
                self.answers.append(a)
            except:
                failure.append(f'{sub}')
                
        print('Subreddits searched:', ', '.join(success))
        print('Subreddits not searched:', ', '.join(failure))
        return
    
    # Helper function to get all hrefs on a page
    def _href(self, soup):
        hrefs = []
        for i in soup.find_all('a', class_='question-hyperlink', href=True):
            hrefs.append(i['href'])
            
        return hrefs
    
    # Helper function to collect all valid hrefs
    def _clean_empty_hrefs(self, hrefs):
        # Remove all empty lists
        list_hrefs = []
        for i in hrefs:
            if i != []:
                list_hrefs.append(i)
                
        # Merge all elements in one list
        hrefs_list = []
        for i in list_hrefs:
            for j in i:
                hrefs_list.append(j)
                
        return hrefs_list
    
    # Helper function to correct addresses
    def _add_prefix(self, hrefs_list):
        # Arrange links that do not have 'https://stackoverflow.com' prefix
        new_href = []
        prefix = 'https://stackoverflow.com'
        for h in hrefs_list:
            if 'https' not in h:
                m = prefix + h + 'answertab=votes#tab-top'
                new_href.append(m)
            else:
                new_href.append(h + 'answertab=votes#tab-top')
            
        return new_href
    
    # Helper function to obtain one soup of one question 
    def _single_page_scraper(self, url):
        r = requests.get(url=url)
        soup = bs(r.text, 'html.parser')
        
        return soup
    
    # Helper function to obtain the questions and answers of a url
    def _single_page_question_answer(self, url):
        page = self._single_page_scraper(url).find_all('div', class_='post-layout')
        questions = [ i.find('p').get_text() for i in page ][0]
        answers = [ i.find('p').get_text() for i in page ][1]

        return questions, answers
    
    def get_stack_overflow(self, maximum_pages, topics):
        '''
        Parameters
        ----------
        maximum_pages: Number (int) of pages to scrape
        topics: List of topics (strings) to query
        '''
        assert type(topics) == list, 'Topics must be list of strings'
        for topic in topics:
            soups = []
            for page in range(1, maximum_pages + 1):
                url = f'https://stackoverflow.com/questions/tagged/{topic}?tab=votes&page={page}&pagesize=15'
                r = requests.get(url=url)
                soup = bs(r.text, 'html.parser')
                soups.append(soup)
                time.sleep(0.2)
                
            print(f'{topic.capitalize()} soups are ready!')
                  
            # Obtain and process all hrefs
            hrefs = [ self._href(soup) for soup in soups ]
            hrefs_list = self._clean_empty_hrefs(hrefs)
            new_hrefs_list = self._add_prefix(hrefs_list)
            print(f'All {topic.capitalize()} hrefs are ready!')
            
            # Retrieve and append questions and answers from each page
            for url in new_hrefs_list:
                time.sleep(0.2)
                try:
                    q, a = self._single_page_question_answer(url)
                    self.questions.append(q)
                    self.answers.append(a)
                except:
                    pass

            print(f'{topic.capitalize()} finished!')
        
        assert len(self.questions) == len(self.answers)
        print('All topics finished!')
        return
    
    def write_csv(self, name):
        '''
        Method to write csv file of questions and answers
        
        Parameters
        ----------
        name: Name of file (string)
        '''
        df = pd.DataFrame([self.questions, self.answers], index=['questions', 'answers']).T
        df.to_csv(f'{name}')

        print(f'{name} made!')
        return