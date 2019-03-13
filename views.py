from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from excelToSqlApp import forms
from datetime import datetime
from excelToSqlApp import services
import json

# Create your views here.
@require_http_methods(['GET', 'POST'])
def sqlServerLogin(request):
    if request.method == 'POST':
        form = forms.SqlServerLogInForm(request.POST)
        if form.is_valid():
            success = services.sqlLogin(request.POST['ip_address'], request.POST['username'], request.POST['password'])
            if success.get('hasErrors') == False:
                #return HttpResponse(content=success.get('databases'))
                request.session['ip_address'] = request.POST['ip_address']
                request.session['username'] = request.POST['username']
                request.session['password'] = request.POST['password']
                request.session.set_expiry = 0
                databases = success.get('databases')
                return render(
                    request,
                    'excelToSqlApp/sql_server_content.html',
                    {
                        'databases': databases,
                        'sql_server_address': request.session['ip_address'],
                        'sql_server_user': request.session['username']
                    }
                )
                '''json_data = json.dumps(success)
                return JsonResponse(data = json_data, safe=False)'''
            else:
                return HttpResponse(content=success.get('errors'))
    else:
        form = forms.SqlServerLogInForm()
    return render(
        request,
        'excelToSqlApp/sql_server_login.html',
        {
            'form': form
        }
    )

@require_http_methods(['GET'])
def connectToSqlDb(request, db_name):
    success = services.connectToSqlDb(request.session['ip_address'], request.session['username'], request.session['password'], db_name)
    if success.get('hasErrors') == False:
        request.session['db_name'] = db_name
        tables = success.get('databases')
        return render(
            request,
            'excelToSqlApp/sql_server_db_tables.html',
            {
                'tables': tables,
                'database_name': db_name,
                'sql_server_address': request.session['ip_address'],
                'sql_server_user': request.session['username']
            }
        )
    else:
        return HttpResponse(content=success.get('errors'))

@require_http_methods(['GET', 'POST'])
def createSqlTable(request):
    if request.method == 'POST':
        form = forms.CreateSqlTableForm(request.POST, request.FILES)
        if form.is_valid():
            response = services.CreateTableFromExcel(request.session['ip_address'], request.session['username'], request.session['password'], request.session['db_name'], request.POST['table_name'], request.FILES['excel_file'])
            return JsonResponse(data=response)
    else:
        form = forms.CreateSqlTableForm()
    return render(
        request,
        'excelToSqlApp/_sql_server_create_table.html',
        {
            'form': form
        }
    )

@require_http_methods(['GET', 'POST'])
def updateSqlTable(request):
    data = services.connectToSqlDb(request.session['ip_address'], request.session['username'], request.session['password'], request.session['db_name'])
    if request.method == 'POST':
        form = forms.UpdateSqlTableForm(request.POST, request.FILES, table_list=data.get('databases'))
        if form.is_valid():
            response = services.updateSqltableFromExcel(request.session['ip_address'], request.session['username'], request.session['password'], request.session['db_name'], request.POST['table_name_u'], request.FILES['excel_file_u'], bool(int(request.POST['drop_table'])))
            return JsonResponse(data=response)
    else:
        form = forms.UpdateSqlTableForm(table_list=data.get('databases'))
    return render(
        request,
        'excelToSqlApp/_sql_server_update_table.html',
        {
            'form': form
        }
    )