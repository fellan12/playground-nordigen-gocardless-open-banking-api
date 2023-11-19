import configparser
import requests
import pprint
import json
import webbrowser
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

def get_token(userid, userkey):
    # Get token
    raw = {"secret_id": userid, "secret_key": userkey}
    requestOptions = {
        'headers': {"accept": "application/json", "Content-Type": "application/json"},
        'json': raw
    }
    response = requests.post("https://ob.nordigen.com/api/v2/token/new/", **requestOptions)
    jsonResponse = response.json()
    #pprint.pprint(jsonResponse)

    # Get access token
    return jsonResponse["access"]

def get_institutions_ids(token, country):
    # Get institution details for country
    banks = {}
    url = "https://ob.nordigen.com/api/v2/institutions/?country=" + country
    headers = {
        "accept": "application/json",
        "Authorization": "Bearer " + token
    }
    response = requests.get(url, headers=headers)
    jsonResponse = response.json()
    #pprint.pprint(jsonResponse)

    for i in range(len(jsonResponse)):
        bank = jsonResponse[i]
        bank_id = jsonResponse[i]["id"]
        name = jsonResponse[i]["name"]
        banks[name] = bank_id

    #pprint.pprint(banks)
    return banks

def create_link(token, institution_id, redirect_url):
    requestOptions = {
        'headers': {
    "accept": "application/json",
    "Content-Type": "application/json",
    "Authorization": "Bearer " + token
    },
        'data': json.dumps({"redirect": redirect_url, "institution_id": institution_id})
    }
    response = requests.post("https://ob.nordigen.com/api/v2/requisitions/", **requestOptions)
    jsonResponse = response.json()
    #pprint.pprint(jsonResponse)
    requisition_id = jsonResponse["id"]
    link = jsonResponse["link"]
    return requisition_id, link

def get_accounts(token, requisition_id):
    url = "https://ob.nordigen.com/api/v2/requisitions/" + requisition_id + "/"
    headers = {
        "accept": "application/json",
        "Authorization": "Bearer " + token
    }
    response = requests.get(url, headers=headers)
    jsonResponse = response.json()
    accounts = jsonResponse["accounts"]
    pprint.pprint(accounts)
    return accounts

def waitUntilauthenticated(link, requisition_id, redirect_url):
    final_url = redirect_url + "?ref=" + str(requisition_id)
    driver = webdriver.Chrome()
    driver.get(link)
    wait = WebDriverWait(driver, 120)
    wait.until(expected_conditions.url_to_be(final_url))

def get_transactions(token, account_id): 
    url = "https://ob.nordigen.com/api/v2/accounts/" + account_id + "/transactions/"
    headers = {
        "accept": "application/json",
        "Authorization": "Bearer " + token
    }
    response = requests.get(url, headers=headers)
    jsonResponse = response.json()
    #pprint.pprint(jsonResponse)
    return jsonResponse["transactions"]

if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read("config.ini")
    user_id = config["credentials"]["user_id"]
    user_key = config["credentials"]["user_key"]
    redirect_url = config["utility"]["redirect_url"]
    country = config["utility"]["country"]
    institution = config["utility"]["institution"]

    token = get_token(user_id, user_key)
    institutions_ids = get_institutions_ids(token, country)
    swedbank_id = institutions_ids[institution]
    requisition_id, link = create_link(token, swedbank_id, redirect_url)
    waitUntilauthenticated(link, requisition_id, redirect_url)
    accounts = get_accounts(token, requisition_id)
    bookedTransactionType = {}
    for i in range(len(accounts)):
        transactions = get_transactions(token,  accounts[i])
        booked = transactions["booked"]
        pending = transactions["pending"]
        print("\nAccount " + str(accounts[i]))
        print("Booked")
        pprint.pprint(booked)
        print("Pending")
        pprint.pprint(booked)
