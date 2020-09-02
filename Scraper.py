from threading import Thread
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
import time
from webdriver_manager.chrome import ChromeDriverManager

from utils import Profile, ScrapingException, is_url_valid, HumanCheckException, wait_for_loading, wait_for_scrolling, \
    Job, AuthenticationException, Location, Company, ScrapingResult


class Scraper(Thread):

    def __init__(self, linkedin_username, linkedin_password, profiles_urls, headless=False):

        Thread.__init__(self)

        # Creation of a new instance of Chrome
        options = webdriver.ChromeOptions()
        options.add_argument('--no-sandbox')
        if headless:
            options.add_argument('--headless')

        self.browser = webdriver.Chrome(executable_path=ChromeDriverManager().install(), options=options)

        self.profiles_urls = profiles_urls

        self.results = []

        self.linkedin_username = linkedin_username
        self.linkedin_password = linkedin_password

    def run(self):

        # Login in LinkedIn
        self.browser.get('https://www.linkedin.com/uas/login')

        username_input = self.browser.find_element_by_id('username')
        username_input.send_keys(self.linkedin_username)

        password_input = self.browser.find_element_by_id('password')
        password_input.send_keys(self.linkedin_password)
        password_input.submit()

        if not self.browser.current_url == "https://www.linkedin.com/feed/":
            print(self.browser.current_url)
            time.sleep(40)
            raise AuthenticationException()

        for linkedin_url in self.profiles_urls:

            self.results.append(
                ScrapingResult(
                    linkedin_url,
                    self.scrape_profile(linkedin_url)
                )
            )

        # Closing the Chrome instance
        self.browser.quit()

    def scrape_profile(self, linkedin_url, waiting_time=10):

        try:
            profile = self.__scrape_profile(linkedin_url)

        except HumanCheckException:
            print("Please solve the captcha.")
            print("Another try will be performed within 10 seconds...")
            time.sleep(waiting_time)

            profile = self.scrape_profile(linkedin_url, int(waiting_time*1.5))

        except ScrapingException:
            profile = None

        return profile

    def __scrape_profile(self, profile_linkedin_url):

        if not is_url_valid(profile_linkedin_url):
            raise ScrapingException

        self.browser.get(profile_linkedin_url)

        # Check correct loading of profile and eventual Human Check
        if not str(self.browser.current_url).strip() == profile_linkedin_url.strip():
            if self.browser.current_url == 'https://www.linkedin.com/in/unavailable/':
                raise ScrapingException
            else:
                raise HumanCheckException

        self.load_full_page()

        # SCRAPING

        profile_name = self.scrape_profile_name()

        profile_title=self.scrape_title()

        profile_image= self.scrape_image()

        email = self.scrape_email()

        about_profile=self.scrape_about_profile()

        education_profile=self.scrape_education()

        edu1=self.scrape_edu1()
        edu2=self.scrape_edu2()
        edu3=self.scrape_edu3()


        profile_recommendations=self.scrape_recommendations()

        skills = self.scrape_skills()        

        jobs = self.scrape_jobs()  # keep as last scraping

        
        return Profile(
            name=profile_name,
            title=profile_title,
            image=profile_image,
            email=email,
            about=about_profile,
            education=education_profile,
            edu1=edu1,
            edu2=edu2,
            edu3=edu3,
            recommendations= profile_recommendations,
            skills=skills,            
            jobs=jobs
           )

    def scrape_profile_name(self):
        return self.browser.execute_script(
            "return document.getElementsByClassName('pv-top-card--list')[0].children[0].innerText")

    def scrape_recommendations(self):
    	try:
    		return self.browser.execute_script("return document.getElementsByClassName('pv-recommendation-entity')[0].innerText")
    	except:
    		return ''
    def scrape_title(self):
    	try:
    		return self.browser.execute_script("return document.getElementsByClassName('mt1 t-18 t-black t-normal break-words')[0].innerText")
    	except:
    	 return ''	

    def scrape_about_profile(self):
        try:
            self.browser.execute_script(
                "document.getElementsByClassName('lt-line-clamp__more')[0].click()")
            #show more button clicks 
        except WebDriverException:
            pass

        wait_for_loading()

        try:
            return self.browser.execute_script(
                " return document.getElementsByClassName('pv-about__summary-text')[0].innerText;")
        except WebDriverException:
            return ''


    def scrape_education(self):
        try:
    	    return self.browser.execute_script(
    			"return document.getElementById('education-section').innerText;")
        except:
            return ''

    def scrape_edu1(self):
        try:
            try: 
                Institute= self.browser.execute_script("return document.getElementById('education-section').getElementsByTagName('li')[0].getElementsByClassName('pv-entity__school-name')[0].innerText;")
            except:
                Institute=''
            try:
                Degree_Type= self.browser.execute_script("return document.getElementById('education-section').getElementsByTagName('li')[0].getElementsByClassName('pv-entity__comma-item')[0].innerText;")
            except:
                Degree_Type=''
            try:
                Deg_title=self.browser.execute_script("return document.getElementById('education-section').getElementsByTagName('li')[0].getElementsByClassName('pv-entity__comma-item')[1].innerText;")
            except:
                Deg_title=''
            try:
                Year=self.browser.execute_script("return document.getElementById('education-section').getElementsByTagName('li')[0].getElementsByClassName('pv-entity__dates')[0].innerText")
            except:
                Year=''
            edu=Institute+ " @ "+Degree_Type+ " @ "+ Deg_title+ " @ "+Year
            return edu
        except:
         return ''

    def scrape_edu2(self):
        try:
            try: 
                Institute= self.browser.execute_script("return document.getElementById('education-section').getElementsByTagName('li')[1].getElementsByClassName('pv-entity__school-name')[0].innerText;")
            except:
                Institute=''
            try:
                Degree_Type= self.browser.execute_script("return document.getElementById('education-section').getElementsByTagName('li')[1].getElementsByClassName('pv-entity__comma-item')[0].innerText;")
            except:
                Degree_Type=''
            try:
                Deg_title=self.browser.execute_script("return document.getElementById('education-section').getElementsByTagName('li')[1].getElementsByClassName('pv-entity__comma-item')[1].innerText;")
            except:
                Deg_title=''
            try:
                Year=self.browser.execute_script("return document.getElementById('education-section').getElementsByTagName('li')[1].getElementsByClassName('pv-entity__dates')[0].innerText")
            except:
                Year=''
            edu=Institute+ " @ "+Degree_Type+ " @ "+ Deg_title+ " @ "+Year
            return edu
        except:
         return ''
    def scrape_edu3(self):
        try:
            try: 
                Institute= self.browser.execute_script("return document.getElementById('education-section').getElementsByTagName('li')[2].getElementsByClassName('pv-entity__school-name')[0].innerText;")
            except:
                Institute=''
            try:
                Degree_Type= self.browser.execute_script("return document.getElementById('education-section').getElementsByTagName('li')[2].getElementsByClassName('pv-entity__comma-item')[0].innerText;")
            except:
                Degree_Type=''
            try:
                Deg_title=self.browser.execute_script("return document.getElementById('education-section').getElementsByTagName('li')[2].getElementsByClassName('pv-entity__comma-item')[1].innerText;")
            except:
                Deg_title=''
            try:
                Year=self.browser.execute_script("return document.getElementById('education-section').getElementsByTagName('li')[2].getElementsByClassName('pv-entity__dates')[0].innerText")
            except:
                Year=''
            edu=Institute+ " @ "+Degree_Type+ " @ "+ Deg_title+ " @ "+Year
            return edu
        except:
         return ''
    def scrape_image(self):
    	return self.browser.execute_script(
    		" return document.getElementsByClassName('EntityPhoto-circle-9')[0].src")
    	

    def scrape_email(self):
        # > click on 'Contact info' link on the page
        self.browser.execute_script(
            """(function(){
                  try{
                    for(i in document.getElementsByTagName('a'))
                         {let el = document.getElementsByTagName('a')[i];
                          if(el.innerHTML.includes('Contact info')){el.click();}}}
                          catch(e){}})()""")
        wait_for_loading()

        # > gets email from the 'Contact info' popup
        try:
            email = self.browser.execute_script(
                """return (function(){
                                try{
                                 for (i in document.getElementsByClassName('pv-contact-info__contact-type')){ 
                                   let el = document.getElementsByClassName('pv-contact-info__contact-type')[i];
                                   if(el.className.includes( 'ci-email')){
                                    return el.children[2].children[0].innerText; } }}
                                     catch(e){return '';}})()"""
                                                 )
        except WebDriverException:
            email = ''

        try:
            self.browser.execute_script("document.getElementsByClassName('artdeco-modal__dismiss')[0].click()")
        except WebDriverException:
            pass

        return email



    def scrape_jobs(self):

        try:
            jobs = self.browser.execute_script(
                """return (
                function(){ 
                 var jobs = []; 
                 var els = document.getElementById('experience-section').getElementsByTagName('ul')[0].getElementsByTagName('li');
                 for (var i=0;i<els.length; i++){
                    if(els[i].className!='pv-entity__position-group-role-item-fading-timeline'){   
                    if(els[i].getElementsByClassName('pv-entity__position-group-role-item-fading-timeline').length>0){ 
                     } 
                    else { 
                        try {position = els[i].getElementsByClassName('pv-entity__summary-info')[0].getElementsByTagName('h3')[0].innerText;} 
                        catch(err) { position = ''; } 
                        try { company_name = els[i].getElementsByClassName('pv-entity__summary-info')[0].getElementsByClassName('pv-entity__secondary-title')[0].innerText;}
                        catch (err) { company_name = ''; }
                        try{date_ranges = els[i].getElementsByClassName('pv-entity__summary-info')[0].getElementsByClassName('pv-entity__date-range')[0].getElementsByTagName('span')[1].innerText;}
                        catch (err) {date_ranges = ''; }
                        try {exp=els[i].getElementsByClassName('pv-entity__summary-info')[0].getElementsByTagName('h4')[1].getElementsByTagName('span')[1].innerText;}
                        catch(err) {exp='';}        
                        try{job_location = els[i].getElementsByClassName('pv-entity__summary-info')[0].getElementsByClassName('pv-entity__location')[0].getElementsByTagName('span')[1].innerText;}
                        catch (err) {job_location = ''; }
                        try{company_url =els[i].getElementsByTagName('a')[0].href;} 
                        catch (err) {company_url = ''; }
                        jobs.push([position, company_name, company_url, date_ranges, exp, job_location]);}}}
                        return jobs; })();""")
        except WebDriverException:
            jobs = []

        parsed_jobs = []

        for job in jobs:
         try:
            company_industry, company_employees = self.scrape_company_details(job[2])

            parsed_jobs.append(
                Job(
                    position=job[0],
                    company=Company(
                        name=job[1],
                        industry=company_industry,
                        employees=company_employees,
                    ),
                    location=Location(job[5]),
                    exp=job[4],
                    date_range=job[3]
                )
            )
         except:
         	pass
        return parsed_jobs

    def scrape_company_details(self, company_url):

        self.browser.get(company_url)

        try:
            company_employees = self.browser.execute_script(
                "return document.querySelector('a[data-control-name" +
                '="topcard_see_all_employees"' +
                "]').innerText.split(' employees')[0].split(' ').lastObject;"
            )
        except WebDriverException:
            company_employees = ''

        try:
            company_industry = self.browser.execute_script(
                "return document.getElementsByClassName('org-top-card-summary-info-list__info-item')[0].innerText")
        except WebDriverException:
            company_industry = ''

        return company_industry, company_employees

    def scrape_skills(self):
        try:
            self.browser.execute_script(
                "document.getElementsByClassName('pv-skills-section__additional-skills')[0].click()")
        except WebDriverException:
            return []

        wait_for_loading()

        try:
            return self.browser.execute_script(
                """return (
                function(){
                 els = document.getElementsByClassName('pv-skill-category-entity');
                 results = [];
                 for (var i=0; i < els.length; i++){
                 results.push(els[i].getElementsByClassName('pv-skill-category-entity__name-text')[0].innerText);}
                 return results;})()""")
        except WebDriverException:
            return []


    def load_full_page(self):
        window_height = self.browser.execute_script("return window.innerHeight")
        scrolls = 1
        while scrolls * window_height < self.browser.execute_script("return document.body.offsetHeight"):
            self.browser.execute_script('window.scrollTo(0, ' + str(window_height * scrolls) + ');')
            wait_for_scrolling()
            scrolls += 1

        for i in range(self.browser.execute_script(
                "return document.getElementsByClassName('pv-profile-section__see-more-inline').length")):
            try:
                self.browser.execute_script(
                    "document.getElementsByClassName('pv-profile-section__see-more-inline')[" + str(
                        i) + "].click()")
            except WebDriverException:
                pass

            wait_for_loading()
