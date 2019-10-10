import pickle
from selenium import webdriver
import time
import requests
import numpy as np
import json
from bs4 import BeautifulSoup
from scipy.io import loadmat, savemat

class course_scraper():

    def __init__(self):

        self.level_dict = {'AllIntAdv': 'https://www.coursera.org/search?query=%22%22&indices%5Bprod_all_products%5D%5BrefinementList%5D%5Blanguage%5D%5B0%5D=English&indices%5Bprod_all_products%5D%5BrefinementList%5D%5BproductDifficultyLevel%5D%5B0%5D=Intermediate&indices%5Bprod_all_products%5D%5BrefinementList%5D%5BproductDifficultyLevel%5D%5B1%5D=Advanced&indices%5Bprod_all_products%5D%5Bpage%5D=1&indices%5Bprod_all_products%5D%5Bconfigure%5D%5BclickAnalytics%5D=true&indices%5Bprod_all_products%5D%5Bconfigure%5D%5BhitsPerPage%5D=10&configure%5BclickAnalytics%5D=true',
                           'AllMixed': 'https://www.coursera.org/search?query=%22%22&indices%5Bprod_all_products%5D%5BrefinementList%5D%5Blanguage%5D%5B0%5D=English&indices%5Bprod_all_products%5D%5BrefinementList%5D%5BproductDifficultyLevel%5D%5B0%5D=Mixed&indices%5Bprod_all_products%5D%5Bpage%5D=1&indices%5Bprod_all_products%5D%5Bconfigure%5D%5BclickAnalytics%5D=true&indices%5Bprod_all_products%5D%5Bconfigure%5D%5BhitsPerPage%5D=10&configure%5BclickAnalytics%5D=true',
                           'AllBeg': 'https://www.coursera.org/search?query=%22%22&indices%5Bprod_all_products%5D%5BrefinementList%5D%5Blanguage%5D%5B0%5D=English&indices%5Bprod_all_products%5D%5BrefinementList%5D%5BproductDifficultyLevel%5D%5B0%5D=Beginner&indices%5Bprod_all_products%5D%5BrefinementList%5D%5BentityTypeDescription%5D%5B0%5D=Courses&indices%5Bprod_all_products%5D%5BrefinementList%5D%5Bskills%5D=&indices%5Bprod_all_products%5D%5Bpage%5D=1&indices%5Bprod_all_products%5D%5Bconfigure%5D%5BclickAnalytics%5D=true&indices%5Bprod_all_products%5D%5Bconfigure%5D%5BhitsPerPage%5D=10&configure%5BclickAnalytics%5D=true'}

        self.level_names = list(self.level_dict.keys())

    def scrape_urls(self):
        """
        A method to scrape Coursera URLs.
        """
        urls_all = []
        driver = webdriver.Chrome("/mnt/c/Users/easso/docs/neurohackademy/insight_examples/chromedriver.exe")
        for level_name in self.level_names:
            print('Scraping', level_name, 'urls')
            url = self.level_dict[level_name]
            driver.get(url)
            while True:
                try:
                    courses = driver.find_elements_by_xpath("//li[@class='ais-InfiniteHits-item']//a")
                    urls_page = [course.get_attribute("href") for course in courses if "/learn/" in course.get_attribute("href")]
                    urls_all.extend(urls_page)
                    button = driver.find_element_by_xpath("//button[@id='pagination_right_arrow_button' and @class='label-text box arrow']")
                    button.click()
                    time.sleep(2)
                except Exception as e:
                    print("Reached end of", level_name, "course list")
                    break

        file = open('../data/edu-cater_urls.pkl', 'wb')
        pickle.dump(urls_all, file)
        file.close()

    def load_urls(self):
        """
        A method to load all URLs after they have been scraped.
        """
        file = open('../data/edu-cater_urls.pkl', 'rb')
        self.urls_all = pickle.load(file)
        file.close()

    def scrape_courses(self):
        """
        A method to scrape course information from each course URL.
        """
        self.load_urls()

        # get course info
        course_info_all = {}

        for i, url in enumerate(self.urls_all):
            print(url)
            r  = requests.get(url)
            data = r.text
            soup = BeautifulSoup(data)

            ### get course info and add to dictionary
            # course title
            title = soup.find(class_="H2_1pmnvep-o_O-weightNormal_s9jwp5-o_O-fontHeadline_1uu0gyz max-text-width-xl m-b-1s").text
            # course description
            description = soup.find_all(class_='AboutCourse')[0].find(class_="content-inner").text
            # syllabus headings
            syllabus_headings_all = soup.find_all(class_='H2_1pmnvep-o_O-weightBold_uvlhiv-o_O-bold_1byw3y2 m-b-2')
            syllabus_headings = ""
            for heading in syllabus_headings_all:
                syllabus_headings += heading.text + " "
            # syllabus descriptions
            try:
                syllabus_descriptions_all = soup.find_all(class_='Syllabus')[0].find_all(class_="content-inner")
                syllabus_descriptions = ""
                for desc in syllabus_descriptions_all:
                    syllabus_descriptions += desc.text + " "
            except:
                syllabus_descriptions = ""
            # number of reviews
            try:
                nreviews = int(soup.find(itemprop="reviewCount").text)
            except:
                nreviews = np.nan
            # level
            try:
                level = soup.find('title', id=re.compile('Level')).text.split()[0]
            except:
                level = "Mixed"
            # hours (course length)
            try:
                hours_tmp = soup.find_all(text=re.compile("Approx. "))[0]
                hours = int(hours_tmp.split('Approx. ')[1].split(' hours')[0])
            except:
                hours = np.nan
            # stars (overall rating)
            try:
                stars = soup.find_all(class_="H4_1k76nzj-o_O-weightBold_uvlhiv-o_O-bold_1byw3y2 m-l-1s m-r-1 m-b-0")
                stars = float(stars[0].text)
            except:
                stars = np.nan
            # enrollment
            enrollment_tmp = soup.find('script', text = re.compile('totalEnrollment')).text
            enrollment = int(enrollment_tmp.split('"totalEnrollmentCount":')[1].split('}')[0])
            # skills you'll gain
            skills = []
            try:
                soup.find_all(class_="Box_120drhm-o_O-displayflex_poyjc-o_O-wrap_rmgg7w")[0].text
                skills_tags = soup.find_all(class_="centerContent_dqfu5r")
                for skill in skills_tags:
                    skills.append(skill.text)
            except:
                pass
            # occupations (Learners taking this course are...)
            occupations_tags = soup.find_all(class_="occupation-name")
            occupations = []
            for occupation in occupations_tags:
                occupations.extend(occupation)
            # reviews
            print("number of reviews:", nreviews)
            reviews = []
            counter = 1
            get_reviews = 0
            if get_reviews==1:
                while True:
                    try:
                        if counter%10==1:
                            print(counter)
                        if counter == 1:
                            r = requests.get(url+'/reviews')
                        else:
                            r = requests.get(url+'/reviews'+'?page='+str(counter))
                        data = r.text
                        soup = BeautifulSoup(data)
                        reviews_all = soup.find_all(class_="reviewText")
                        if len(reviews_all)==0:
                            break
                        else:
                            for review in reviews_all:
                                reviews.append(review.text)
                            counter += 1
                    except:
                        pass

            # add info to dictionary
            course_info  =   {'title': title,
                              'description': description,
                              'syllabus_headings': syllabus_headings,
                              'syllabus_descriptions': syllabus_descriptions,
                              'nreviews': nreviews,
                              'level': level,
                              'hours': hours,
                              'stars': stars,
                              'enrollment': enrollment,
                              'skills': skills,
                              'occupations': occupations,
                              'reviews': reviews}

            # save course_info
            file = '../course_info/course' + str(i) + '.json'
            with open(file, 'w') as fp:
                json.dump(course_info, fp)


    def scrape_course_network(self):
        """
        A method to scrape a list of recommended courses from a single course page.
        """
        self.load_urls()

        # make course network
        course_network = np.zeros((len(self.urls_all), len(self.urls_all)))

        driver = webdriver.Chrome("/mnt/c/Users/easso/docs/neurohackademy/insight_examples/chromedriver.exe")
        for i, url in enumerate(self.urls_all):
            print(url)
            driver.get(url)

            recs_all = []
            recs = driver.find_elements_by_xpath('//div[@class="m-a-1s"]//div//a[@data-click-value]')
            for rec in recs:
                recs_all.append(rec.get_attribute("href"))

            time.sleep(2)

            while True:
                try:
                    button = driver.find_element_by_xpath("//button[@class='Button_1w8tm98-o_O-icon_1rbfoc-o_O-md_1jvotax']")
                except:
                    break
                button.click()
                time.sleep(2)
                recs = driver.find_elements_by_xpath('//div[@class="m-a-1s"]//div//a[@data-click-value]')
                repeats=0
                for rec in recs:
                    if rec.get_attribute("href") in recs_all:
                        repeats += 1
                    else:
                        recs_all.append(rec.get_attribute("href"))
                if repeats == len(recs):
                    break

            recs_all = np.unique(recs_all)
            recs_all_courses = []
            for rec in recs_all:
                if '/learn/' in rec:
                    recs_all_courses.append(rec)

            for rec in recs_all_courses:
                try:
                    ind = scraper.urls_all.index(rec)
                    course_network[i,ind] = 1
                except:
                    pass

            coursenet = course_network[i,:]
            savename = '../course_nets/course' + str(i) + '.mat'
            savemat(savename,{'coursenet': coursenet})
        self.course_network = course_network

def isEnglish(s):
    """
    Return True if all characters in a string are
    characters used in the English language, else False.

    Parameters
    ----------
    s : string

    Output
    ------
    y : bool
    True if all characters are used in the English language
    False otherwise
    """
    try:
        s.encode(encoding='utf-8').decode('ascii')
    except UnicodeDecodeError:
        return False
    else:
        return True

def fix_text(txt):
    """
    Fixes a string to replace non-English characters.

    Parameters
    ----------
    txt : string
    The string of text to be fixed

    Output
    ------
    txt : string
    The fixed string of text
    """
    if not isEnglish(txt):
        for i, s in enumerate(txt):
            if not isEnglish(s):
                if len(txt)>=i+2:
                    if txt[i+1] == 's':
                        txt = txt.replace(s,"'")
                    elif txt[i+1] == ' ' and "'" not in txt:
                        txt = txt.replace(s,'-')
                    else:
                        txt = txt.replace(s,'')
                else:
                    txt = txt.replace(s,'')
    return txt
