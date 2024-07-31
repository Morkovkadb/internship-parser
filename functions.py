import requests
from bs4 import BeautifulSoup
import telebot

url = ['https://tech.wildberries.ru/techschool', 'https://education.tbank.ru/start/']

def fetch_html(i):
    response = requests.get(url[i])
    return response.text


def parse_wildberries(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    spans = soup.find_all('span')
    return spans


def parse_tbank(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    p_tags = soup.find_all('p')
    corrected_string = []
    i = 0
    while i < len(p_tags):
        try:
            corrected_string.append(p_tags[i].get_text().encode('latin').decode('utf-8'))
            i += 1
        except Exception as e:
            i += 1
    return corrected_string


def tbank(internships):
    html_content = fetch_html(1)
    ps = parse_tbank(html_content)
    total = 0
    for i in range(len(ps)):
        if ps[i] == "Набор открыт":
            internships.append("Появился набор в Т-Банк: " + url[1])
            return internships
        elif ps[i] == "Набор закрыт":
            total += 1
            if total == 12:
                internships.append("T-Bank: все наборы закрыты")
    return internships


def wildberries(internships):
    html_content = fetch_html(0)
    spans = parse_wildberries(html_content)
    total = 0
    for span in spans:
        if span.text == "Набор закрыт":
            total += 1
    if total < 11:
        internships.append("Появился набор в WB: " + url[0])
    else:
        internships.append("WB: все наборы закрыты")


def All_internships():
    internships = []
    wildberries(internships)
    tbank(internships)
    string = ''
    for el in internships:
        string += el + "\n"
    return string