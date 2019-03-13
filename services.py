import pyodbc, pandas
from sqlalchemy import create_engine
import re

#create services here
def sqlLogin(ip_address, username, password):
    hasErrors = False
    errors = ''
    returnedData = {}
    databases = []
    try:
        con = pyodbc.connect('DRIVER={SQL Server};SERVER='+ ip_address +';DATABASE=master;UID='+ username +';PWD=' + password)
        cursor = con.cursor()
        cursor.execute("select name from sys.databases")
        dbs = cursor.fetchall()
        for db in dbs:
            databases.append(db.name)
    except Exception as e:
        hasErrors = True
        errors = e
    finally:
        #cursor.close()
        returnedData['hasErrors'] = hasErrors
        returnedData['errors'] = errors
        returnedData['databases'] = databases
        return returnedData

def connectToSqlDb(ip_address, username, password, db_name):
    hasErrors = False
    errors = ''
    returnedData = {}
    databases = []
    try:
        con = pyodbc.connect('DRIVER={SQL Server};SERVER='+ ip_address +';DATABASE='+ db_name +';UID='+ username +';PWD=' + password)
        cursor = con.cursor()
        cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE' AND TABLE_CATALOG='" + db_name +"'")
        dbs = cursor.fetchall()
        for db in dbs:
            databases.append(db.TABLE_NAME)
    except Exception as e:
        hasErrors = True
        errors = e
    finally:
        #cursor.close()
        returnedData['hasErrors'] = hasErrors
        returnedData['errors'] = errors
        returnedData['databases'] = databases
        return returnedData

def CreateTableFromExcel(ip_address, username, password, db_name, table_name, excel_file):
    returnedData = {}
    hasErrors = False
    success = True
    errors = ''
    messages = ''
    try:
        #check table_name
        if checkColumnNames(table_name):
            table_name = str(table_name).replace(' ', '_')
        else:
            hasErrors = True
            success = False
            errors = 'Invalid table name. Table name must start with upper or lowwer letter (a-z) or underscore. Table name can contain only upper or lower letters (a-z), digits (0-9), underscores or spaces.'
            returnedData['success'] = success
            returnedData['hasErrors'] = hasErrors
            returnedData['errors'] = errors
            returnedData['messages'] = messages
            return returnedData

        #reads the excel file and check column names and column types
        data = pandas.read_excel(excel_file)
        columns = list(data)
        columnTypes = []
        for item in data.dtypes:
            columnTypes.append(str(item))
        columnsSql = []
        for col in columns:
            if checkColumnNames(str(col)):
                columnsSql.append(str(col).replace(' ', '_'))
            else:
                hasErrors = True
                success = False
                errors = 'Invalid column names. Column name must start with upper or lowwer letter (a-z) or underscore. Column name can contain only upper or lower letters (a-z), digits (0-9), underscores or spaces.'
                returnedData['success'] = success
                returnedData['hasErrors'] = hasErrors
                returnedData['errors'] = errors
                returnedData['messages'] = messages
                return returnedData
        columnTypesSql = []
        for colType in columnTypes:
            if 'int' in colType:
                columnTypesSql.append('int')
            elif 'object' in colType:
                columnTypesSql.append('nvarchar(MAX)')
            elif 'float' in colType:
                columnTypesSql.append('float')
            elif 'datetime' in colType:
                columnTypesSql.append('datetime')
            else:
                columnTypesSql.append('nvarchar(MAX)')
        createTableQuery = "Create table " + table_name + " ("
        i = 0
        while i<len(columnsSql):
            createTableQuery += str(columnsSql[i]) + ' ' + str(columnTypesSql[i]) + ','
            i += 1
        createTableQuery += ")"
        
        #connect to sql server and create a table
        con = pyodbc.connect('DRIVER={SQL Server};SERVER='+ ip_address +';DATABASE='+ db_name +';UID='+ username +';PWD=' + password)
        cursor = con.cursor()     
        cursor.execute(createTableQuery)
        con.commit()

        #connect to sql server and insert data from excel to a created table
        data.columns = columnsSql
        engine = create_engine('mssql+pymssql://'+ username +':'+ password +'@'+ ip_address +':1433/'+ db_name)
        data.to_sql(table_name, engine, if_exists='append', index=False)
        messages = 'Table ' + table_name + ' created successfully'
        success = True
    except Exception as e:
        success = False
        hasErrors = True
        errors = str(e)
    finally:
        returnedData['success'] = success
        returnedData['hasErrors'] = hasErrors
        returnedData['errors'] = errors
        returnedData['messages'] = messages
        return returnedData

def updateSqltableFromExcel(ip_address, username, password, db_name, table_name, excel_file, drop_table):
    returnedData = {}
    hasErrors = False
    success = True
    errors = ''
    messages = ''
    try:
        #connect to sql server and get table columns and data types
        con = pyodbc.connect('DRIVER={SQL Server};SERVER='+ ip_address +';DATABASE='+ db_name +';UID='+ username +';PWD=' + password)
        cursor = con.cursor()
        cursor.execute("SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH FROM "+ db_name +".INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = N'"+ table_name +"'")
        result = cursor.fetchall()
        columnNamesSql = []
        columnTypesSql = []
        for r in result:
            columnNamesSql.append(r.COLUMN_NAME)
            columnTypesSql.append(r.DATA_TYPE)
        
        #read excel file and get columns and data types
        data = pandas.read_excel(excel_file)
        columns = list(data)
        columnTypes = []
        for item in data.dtypes:
            columnTypes.append(str(item))
        
        #check column names
        if columnNamesSql != columns:
            hasErrors = True
            success = False
            errors = 'Columns in excel file and sql table must have the same order and names'
            returnedData['hasErrors'] = hasErrors
            returnedData['success'] = success
            returnedData['messages'] = messages
            returnedData['errors'] = errors
            return returnedData

        #connect to sql and update table
        engine = create_engine('mssql+pymssql://'+ username +':'+ password +'@'+ ip_address +':1433/'+ db_name)
        if drop_table:
            #delete all records from table
            cursor.execute("DELETE FROM " + table_name)
            con.commit()
        #update table
        data.to_sql(table_name, engine, if_exists='append', index=False) 
        messages = 'Table ' + table_name + ' updated successfully'
        success = True

    except Exception as e:
        hasErrors = True
        success = False
        errors = str(e)
    finally:
        returnedData['success'] = success
        returnedData['hasErrors'] = hasErrors
        returnedData['errors'] = errors
        returnedData['messages'] = messages
        return returnedData

def checkColumnNames(col_name):
    if re.match("^[a-zA-Z_][a-zA-Z0-9_\s]+$", col_name):
        return True
    return False