# zyda
Example of scrapy crawling spider

## Installation
* Install python `virtualenv` if you don't already have it
```
$ sudo -s pip install virtualenv
```

* In the project directory roor create new virtual env (here we will name it `venv`)
```
$ virtualenv venv && source ./venv/bin/activate
```
* Install requirements
```
$ pip install -r requirements.txt
```

## Start running the spider
Here we will run the spider manually to get the result to json file
```
$ source ./venv/bin/activate
$ scrapy crawl yelp -o ./output.json
```
* The output will be appended to the file `output.json` while the spider is running
* To stop the spider press `CTRL+C` just one time and wait for it to exit gracefully
