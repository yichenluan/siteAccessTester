# siteAccessTester
---
siteAccessTester is a simple tool to test the accessible of a website.


##How to use

- Get the codes

 ```
 git clone git@github.com:yichenluan/siteAccessTester
 ```
 
- Install the libraries

 	```
 	cd siteAccessTester
 	pip install -r requirements.txt
 	```
 	
- Run

 	There are tow different version of the codes.
 	
 	---
 	
 	```
 	python run.py
 	```
 	or
 	
 	```
 	python run.py -c
 	```
 	means run the codes by the coroutine version.
 	
 	---
 	
 	```
 	python run.py -t
 	```
 	means run the codes by the multiThreading version.
 	
##Configuration

you can change common configuration by rewite the conf.py.

you can change site configuration by rewite the m_sohu.py.


##Reference

Thinks to the codes in git@github.com:ubear/URLChecker.