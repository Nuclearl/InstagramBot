from selenium import webdriver
from time import sleep


class InstaBot:
    def __init__(self, username, password):
        self.driver = webdriver.Chrome()
        self.driver.get("https://www.instagram.com/")
        sleep(1)
        self.driver.find_element_by_xpath("//input[@name=\"username\"]") \
            .send_keys(username)
        self.driver.find_element_by_xpath("//input[@name=\"password\"]") \
            .send_keys(password)
        self.driver.find_element_by_xpath('//button[@type="submit"]') \
            .click()
        sleep(2)
        self.driver.find_element_by_xpath("/html/body/div[1]/section/main/div/div/div/div/button") \
            .click()
        sleep(1)

    def get_likes(self, url):
        self.driver.get(url)
        sleep(1)
        self.driver.find_element_by_xpath("/html/body/div[1]/section/main/div/div[1]/article/div[3]/section[2]/div/div/button").click()
        following = self._get_names()
        print(following)

    def _get_names(self):
        names = []
        sleep(1)
        scroll_box = self.driver.find_element_by_xpath("/html/body/div[4]/div/div/div[2]/div")
        last_ht, ht = 0, 1
        while last_ht != ht:
            last_ht = ht
            sleep(2)
            ht = self.driver.execute_script("""
                   arguments[0].scrollTo(0, arguments[0].scrollHeight); 
                   return arguments[0].scrollHeight;
                   """, scroll_box)
            print(ht)
            sleep(1)
            links = scroll_box.find_elements_by_tag_name('a')
            for name in links:
                if name.text != '':
                    names.append(name.text)
        # close button
        self.driver.find_element_by_xpath("/html/body/div[4]/div/div/div[1]/div/div[2]/button").click()
        return names

