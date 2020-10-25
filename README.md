# Use Selenium and Chromium to scrape a web page via AWS Lambda

                           A quick piece of code to run a scraper in the cloud.  You can run it daily as a `cron` job.


Constructs a docker container that mimics the AWS runtime envioment to build out and test your app, then uploads an AWS CloudFormationStack project to AWS, creating a function and a layer. You must create a bucket to hook it up to and also add a CloudWatch Event trigger to run it daily. 

Uses the tiny "html_table_parser" module to convert an HTML table to an array of python lists, as pandas (what I'd usually use) is too large to fit within the 250 MB size restriction for the AWS layer once I add the essential binary files (selenium, my webdriver, chromium). 

## Requirements: 
- Python 3.7
- Chromium 86.0.4240.0
- Chromedriver 86.0.4240.22.0
- Selenium 3.14

## Layer: 
- Selenium
- Chromium
- pygsheets module
- google sheet JSON authorization file
- time module
- datetime module (yes both are needed)
- [this HTML table parsing module](https://pypi.org/project/html-table-parser-python3/)

## Usage:
1. Adapt the file `/src/lambda_function.py` for your target URI
2. Type `make` to build
3. **Max: anything else?  How to upload, etc?**
4. **How to set it to run as a cron job**

## License

This package is licenced under the GPL v3.  See the file LICENSE.

It is a fork of Vittorio Nardone's `pychromeless` scraper that just makes an image of the result ([link](https://github.com/21Buttons/pychromeless "github repo")).
