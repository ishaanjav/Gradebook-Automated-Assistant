import time
import selenium
from time import sleep
from selenium import webdriver
import sys, os
import requests
from datetime import datetime
from datetime import date
import os.path, operator
from contextlib import contextmanager
from webdriver_manager.chrome import ChromeDriverManager
import setup

gradebook_link = "https://gradebook.pisd.edu/Pinnacle/Gradebook/InternetViewer/GradeReport.aspx"

@contextmanager
def suppress_stdout():
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stderr
        sys.stderr = devnull
        try:  
            yield
        finally:
            sys.stderr = old_stdout

browser = None
with suppress_stdout():
	browser = webdriver.Chrome(ChromeDriverManager().install()) # Will install latest version or used cached version if already present.
	print ("\033[A                             \033[A")

browser.get(gradebook_link)

login = browser.find_element_by_xpath('''//*[@id="ContentPlaceHolder_Username"]''')
passw = browser.find_element_by_xpath('''//*[@id="ContentPlaceHolder_Password"]''')
login.send_keys(setup.username)
passw.send_keys(setup.password)
btn = browser.find_element_by_xpath('''//*[@id="ContentPlaceHolder_LogonButton"]''')
btn.click()

at = True
classes = setup.class_commands
class_grades = [("/html/body/form/section/div[2]/div/div[2]/div/div/div["+str(i)+"]/div[3]/div/a[2]/div[1]/div/div") for i in range(2, 9)]

def prGreen(skk): print("\033[92m {}\033[00m" .format(skk)) 
def prYellow(skk): print("\033[1;33m{}\033[00m" .format(skk)) 

def grades():
	prGreen("- - - - - - -")
	for idx, i in enumerate(classes):
		if "here" in i: 
			continue
		prYellow("  " + browser.find_element_by_xpath(class_grades[idx]).text.partition('\n')[0][:-1] + " % " + (i if len(setup.class_names) <= idx else setup.class_names[idx]))
	prGreen("- - - - - - -")

def ordered():
	global at
	if not at:
		browser.get(gradebook_link)
		at = True
	g = {}
	for idx, i in enumerate(classes):
		if "here" in i: 
			continue
		grade = int(browser.find_element_by_xpath(class_grades[idx]).text.partition('\n')[0][:-1])
		key = i if len(setup.class_names) <= idx else setup.class_names[idx]
		g[key] = grade

	sorted_g = sorted(g.items(), key = operator.itemgetter(1))
	prGreen("- - - - - - -")
	for i, j in sorted_g:
		prYellow("  {} % {}".format(j, i))
	prGreen("- - - - - - -")

grades()
at = True

while True:
	s = input("Enter a command: ")
	if s == "close":
		browser.close()
		break
	if s == "grades":
		if not at:
			browser.get(gradebook_link)
			at = True
		grades()
	elif s =="sort":
		ordered()
		at = True
	elif s == "home":
		if not at:
			browser.get(gradebook_link)
			at = True
	else:
		found = False
		if not at:
			browser.get(gradebook_link)
		at = False
		for idx, period in enumerate(classes):
			if period == s:
				found = True
				item = browser.find_element_by_xpath(class_grades[idx])
				item.click()
				break
		if not found:
			print("Command not recognized. Check setup.py and the setup instructions to setup commands.")
			if not at:
				browser.get(gradebook_link)
				at = True