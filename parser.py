import urllib.request
from urllib3.contrib.socks import SOCKSProxyManager
import os, re, time, jsonlines
import xlsxwriter
from bs4 import BeautifulSoup

#   CONSTANTS!!!
BASE_URL = 'http://mymd.ae/listing/doctor'
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0'
DOCTOR_URL_TEMPLATE = 'http://mymd.ae/docdetail/'
MAIN_FIELDS = ['Name', 'Specialty', 'Email', 'Emirates', 'Contact', 'Fax', 'Postal Code', 'Website', 'Address', 'Link']
PROXY_SITE = 'https://hidemy.name/ru/proxy-list/?country=RUUAUS&maxtime=250&type=45#list'


def get_html_proxy(url):
    http = urllib.request.Request(url, headers={
        'User-Agent': USER_AGENT
    })
    response = urllib.request.urlopen(http)
    return response.read()


def get_html(url):
    # proxy = SOCKSProxyManager('socks' + str(proxy_dict[2]) + "://" + str(proxy_dict[0]) + ':' + str(proxy_dict[1]) + '/')
    # response = proxy.request('GET', url)
    # return response.data
    http = urllib.request.Request(url, headers={
        'User-Agent': USER_AGENT
    })
    response = urllib.request.urlopen(http)
    return response.read()


def conv_str(sr):
    """Converting proxy strings"""
    if re.search('[A-Z]+4', sr):
        sr = str(4)
    elif re.search('[A-Z]+5', sr):
        sr = str(5)
    return sr


def read_proxies(filepath):
    proxy_list = []
    with jsonlines.open(filepath) as reader:
        for i, state in enumerate(reader):
            proxy_list.append(state)
        reader.close()
    return proxy_list


def get_proxy(html):
    soup = BeautifulSoup(html, 'lxml')
    table = soup.find('table', class_='proxy__t')

    with jsonlines.open('proxy/proxy.jsonl', 'w') as f:
        tbody = table.find('tbody')
        for i, tr in enumerate(tbody.find_all('tr')):
            pr_list = []
            for k, td in enumerate(tr.find_all('td')):
                if (k == 0) or (k == 1):
                    pr_list.append(td.text)
                elif k == 4:
                    pr_list.append(conv_str(td.text))
                else:
                    pass
            f.write(pr_list)
        f.close()
    return 'proxy/proxy.jsonl'


def cut_url(url):
    """Cuts received url and returns last part (id of doctor)"""
    pieces = re.split('/', url)
    return pieces[-1:]


def get_page_count(html):
    """Returns last page index. Type: int"""
    soup = BeautifulSoup(html)
    paggination = soup.find(id='paging')
    last_link_id = cut_url(paggination.find_all('a')[-1].get('href'))
    return int(last_link_id[0])


def parse_single_doctor(url):
    """Applies doctor`s url and parses data"""
    # doctor_link = get_html(url, plist)
    doctor_link = get_html(url)
    soup = BeautifulSoup(doctor_link)
    mainBlock = soup.find('div', class_='p_top_10 t_xs_align_l')
    doc_name = mainBlock.find('h2', class_='color_dark').text
    table = mainBlock.find('table', class_='description_table')

    result_info = {}
    result_info['Name'] = doc_name
    for row in table.find_all('tr'):
        try:
            h_col = row.find_all('td')[0].text.strip()
            col = row.find_all('td')[1].text.strip()
        except IndexError:
            pass
        if len(col) > 500:
            col = ''

        result_info[''+h_col+''] = col

    result_info['Link'] = url

    return result_info


def parse(html):
    soup = BeautifulSoup(html)
    mainBlock = soup.find('section', class_='products_container')
    items = mainBlock.find_all('div', class_='product_item')

    page_group = []

    for item in items:
        link = cut_url(item.find('a', class_='color_dark').get('href'))
        single_doctor = parse_single_doctor(DOCTOR_URL_TEMPLATE + link[0])
        page_group.append(single_doctor)

    return page_group


def w_into_file(name):
    """Save data to .xlsx file."""
    workbook = xlsxwriter.Workbook('excel/' + name + '.xls')
    worksheet = workbook.add_worksheet()

    worksheet.write('A1', MAIN_FIELDS[0])  # Name
    worksheet.write('B1', MAIN_FIELDS[1])  # Specialty
    worksheet.write('C1', MAIN_FIELDS[2])  # Email
    worksheet.write('D1', MAIN_FIELDS[3])  # Emirates
    worksheet.write('E1', MAIN_FIELDS[4])  # Contact
    worksheet.write('F1', MAIN_FIELDS[5])  # Fax
    worksheet.write('G1', MAIN_FIELDS[6])  # Postal Code
    worksheet.write('H1', MAIN_FIELDS[7])  # Website
    worksheet.write('I1', MAIN_FIELDS[8])  # Address
    worksheet.write('J1', MAIN_FIELDS[9])  # Link

    items = len(os.listdir("tmp"))

    i = 0

    for itm in range(items):

        with jsonlines.open("tmp/" + str(itm) + ".jsonl") as reader:

            for k, item in enumerate(reader):
                try:
                    worksheet.write('A' + str(i + 2), item['Name'])
                except KeyError:
                    worksheet.write('A' + str(i + 2), '')
                try:
                    worksheet.write('B' + str(i + 2), item['Specialty:'])
                except KeyError:
                    worksheet.write('B' + str(i + 2), '')
                try:
                    worksheet.write('C' + str(i + 2), item['Email:'])
                except KeyError:
                    worksheet.write('C' + str(i + 2), '')
                try:
                    worksheet.write('D' + str(i + 2), item['Emirates:'])
                except KeyError:
                    worksheet.write('D' + str(i + 2), '')
                try:
                    worksheet.write('E' + str(i + 2), item['Contact:'])
                except KeyError:
                    worksheet.write('E' + str(i + 2), '')
                try:
                    worksheet.write('F' + str(i + 2), item['Fax:'])
                except KeyError:
                    worksheet.write('F' + str(i + 2), '')
                try:
                    worksheet.write('G' + str(i + 2), item['Postal Code:'])
                except KeyError:
                    worksheet.write('G' + str(i + 2), '')
                try:
                    worksheet.write('H' + str(i + 2), item['Website:'])
                except KeyError:
                    worksheet.write('H' + str(i + 2), '')
                try:
                    worksheet.write('I' + str(i + 2), item['Address:'])
                except KeyError:
                    worksheet.write('I' + str(i + 2), '')
                try:
                    worksheet.write('J' + str(i + 2), item['Link'])
                except KeyError:
                    worksheet.write('J' + str(i + 2), '')

                i += 1
    workbook.close()


def description():
    print("Hello this is a parser for ***http://mymd.ae/listing/doctor***")
    print("Now you need to setup some properties :)")
    print("1) Name your output file, e.g. (ParsedData). Don`t worry, it will be in .xls format.\n")
    print("2) Type timeouts in seconds between every 8 parsed doctors(15 e.g.). It needs to prevent from bans on site.")
    print("\t 20 seconds by default. Min 5 sec. Max 60 sec. Or press ENTER. Parameters will pass automatically.\n")
    print("3) Type page number, where are you want to start. 0 - its the first page, 1 - its the second page etc.\n")
    print("4) Type page number, where are you want to stop. Or see total pages below.\n")
    print("Remember! You can skip 3) and 4) points. Just press ENTER twice. Parameters will pass automatically.")
    print("Remember! You always can type an interval of pages!")


def main():
    description()

    page_count = get_page_count(get_html_proxy(BASE_URL))

    print('Total pages: %s \n\n' % page_count)

    file_name = str(input("Name your output file, e.g. (ParsedData): ---> "))
    t = input("Type timeouts in seconds between every 8 parsed doctors (15 e.g.): ---> ")
    start_page = input("Type page number, where are you want to start: ---> ")
    end_page = input("Type page number, where are you want to stop: ---> ")
    print("\n\n\n")

    if t == '':
        t = 20
    elif int(t) < 1:
        t = 1
    elif int(t) > 60:
        t = 60
    else:
        t = int(t)

    if start_page == '':
        start_page = 0
    else:
        start_page = int(start_page)

    if end_page == '':
        end_page = page_count
    else:
        end_page = int(end_page)

    print("Start collecting proxies...")
    proxy_list = read_proxies(get_proxy(get_html_proxy(PROXY_SITE)))
    print(proxy_list)
    print("Proxies had been collected!")

    print("Let\'s start parse:")

    pcounter = start_page

    for page in range(start_page, end_page + 1):
        doctors = []

        if page == 0:
            link = BASE_URL
        else:
            link = BASE_URL + '/' + str(page)

        doctors.extend(parse(get_html(link)))

        with jsonlines.open('tmp/' + str(pcounter) + '.jsonl', 'w') as tf:
            for item in doctors:
                tf.write(item)
            tf.close()

        pcounter += 1
        print('Parsed page: %s' % pcounter)
        print('Parsing process: %d%%' % ((page / end_page) * 100))

        time.sleep(t)   # Timeouts

    print("\n\n\nParsing end")
    print("\nStart saving parsed data...\n")

    w_into_file(file_name)

    print("Finish! Now you can to close this program. ;)\n")
    q = input("Type \'q\' and press ENTER to close this program :) ---> ")
    if q == 'q':
        quit()


if __name__ == '__main__':
    main()