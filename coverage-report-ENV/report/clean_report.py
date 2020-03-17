import config
from bs4 import BeautifulSoup
import pandas as pd

#Function wich cleans the html.index, to show only the relevant packages tests results
def report_clean():
    #output file
    new_table = BeautifulSoup('<tbody></tbody>', 'html.parser')

    #opening and reading the 'index.html'
    with open(config.LIFERAY_REPORT_HTML) as index:
            index_html = index.read()

    #parsing index.html to BeautifulSoup Object
    index_html_code = BeautifulSoup(index_html, 'html.parser')

    #getting all packages names on 'html.index'
    a_tag = index_html_code.find_all('a')

    #getting required the packages
    count = 0
    for link in a_tag:
        if link.get('href').startswith(config.LIFERAY_PACKAGES):
            new_table.tbody.insert(count, link.parent.parent)
            count += 1

    #dropping not required packages from 'html.index'
    index_html_code.tbody.replace_with(new_table)
    index_html_code = str(index_html_code)

    #opening to write the new report
    with open(config.LIFERAY_NEW_REPORT_HTML, 'w') as new_html:
        new_html.write(index_html_code)


#Function wich sum the real values of the columns
def report_sum():
    #some initial variables
    dataframe = pd.DataFrame()
    new_table_foot = BeautifulSoup('<tfoot><tr></tr></tfoot>', 'html.parser')

    #opening and reading the 'report.html'
    with open(config.LIFERAY_NEW_REPORT_HTML) as index:
        index_html = index.read()

    #parsing report.html to DataFrame Object
    index_html_code = BeautifulSoup(index_html, 'html.parser')
    table = index_html_code.find('table',{'id':'coveragetable'})
    dataframe = pd.read_html(str(table))[0]
    tfoot_tag = index_html_code.tfoot.tr.find_all('td')
    td_tags = index_html_code.tfoot.tr.find_all('td')
    del tfoot_tag[0:5]

    #deleting the totals
    drop_indexes = dataframe[dataframe['Element'] == 'Total'].index
    dataframe.drop(drop_indexes, inplace=True)

    #changing columns values to numeric type
    numeric_columns = dataframe.columns.drop(['Element', 'Missed Instructions', 'Cov.', 'Missed Branches', 'Cov..1'])
    dataframe[numeric_columns] = dataframe[numeric_columns].apply(pd.to_numeric)

    #getting sum of each comlumn
    column_sum = []
    for column in dataframe[numeric_columns]:
        column_sum.append(dataframe[column].sum())

    #replacing sum values on the td tags on the report.html
    for i in range(8):
        tfoot_tag[i].string.replace_with(str(column_sum[i]))
    for i in range(5, 13):
        td_tags[i] = tfoot_tag[i-5]
    for i in range(0, 13):
        new_table_foot.tfoot.tr.insert(i, td_tags[i])

    index_html_code.tfoot.replace_with(new_table_foot)
    index_html_code = str(index_html_code)

    #opening to write the new report
    with open(config.LIFERAY_NEW_REPORT_HTML, 'w') as new_html:
        new_html.write(index_html_code)


#Function wich calculates the percentage of the test coverage
def report_percentages():
    #access directories com.liferay.data.engine.../index.html and catch the tables' numbers
    sum_instructions = 0
    sum_missed_instructions = 0
    sum_branches = 0
    sum_missed_branches = 0
    req_directories = []
    all_td = []
    dir_dataframe = pd.DataFrame()

    #opening and reading the 'index.html'
    with open(config.LIFERAY_NEW_REPORT_HTML) as index:
            index_html = index.read()

    #parsing index.html to BeautifulSoup Object
    index_html_code = BeautifulSoup(index_html, 'html.parser')
    html_table_foot = BeautifulSoup('<tr></tr>', 'html.parser')

    #getting all packages names on 'html.index'
    all_directories = index_html_code.find_all('a')
    table_foot = index_html_code.table.tfoot.tr.find_all('td')

    #getting required the packages
    count = 0
    for link in all_directories:
        if link.get('href').startswith(config.LIFERAY_PACKAGES):
            req_directories.append(link.get('href'))

    for dic in req_directories:
        dir_path = config.LIFERAY_PACKAGES_DIRECTORIES.format(str(dic))
    
        with open(dir_path) as dir_index:
            dir_index_html = dir_index.read()

        dir_index_html_code = BeautifulSoup(dir_index_html, 'html.parser')
        table = dir_index_html_code.find('table',{'id':'coveragetable'})
        dir_dataframe = pd.read_html(str(table))[0]

        #getting the sum of total and missed instructions
        missed_instructions = dir_dataframe['Missed Instructions'].values[dir_dataframe[dir_dataframe['Element'] == 'Total'].index[0]]
        splited_missed_instructions = missed_instructions.split()
        del splited_missed_instructions[1] #deleting the 'of'
        sum_missed_instructions += int(splited_missed_instructions[0].replace(',', ''))
        sum_instructions += int(splited_missed_instructions[1].replace(',', ''))

        #getting the sum of total and missed branches
        missed_branches = dir_dataframe['Missed Branches'].values[dir_dataframe[dir_dataframe['Element'] == 'Total'].index[0]]
        splited_missed_branches = missed_branches.split()
        del splited_missed_branches[1] #deleting the 'of'
        sum_missed_branches += int(splited_missed_branches[0].replace(',', ''))
        sum_branches += int(splited_missed_branches[1].replace(',', ''))

    #calculating the percentage of coverage
    perc_miss_inst = round((1-(sum_missed_instructions/sum_instructions))*100, 2)
    perc_miss_bran = round((1-(sum_missed_branches/sum_branches))*100, 2)

    #printing percentages on the report.html
    table_foot[1].string.replace_with('{} of {}'.format(str(sum_missed_instructions), str(sum_instructions)))
    table_foot[2].string.replace_with('{}%'.format(str(perc_miss_inst)))
    table_foot[3].string.replace_with('{} of {}'.format(str(sum_missed_branches), str(sum_branches)))
    table_foot[4].string.replace_with('{}%'.format(str(perc_miss_bran)))

    for i in range(len(table_foot)):
        html_table_foot.tr.insert(i, table_foot[i])
    index_html_code.table.tfoot.tr.replace_with(html_table_foot.tr)
    index_html_code = str(index_html_code)

    with open(config.LIFERAY_NEW_REPORT_HTML, 'w') as new_html:
        new_html.write(index_html_code)