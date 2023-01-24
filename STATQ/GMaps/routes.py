from flask import render_template, request, Blueprint, redirect, current_app, flash, url_for
from flask_googlemaps import GoogleMaps
from flask_googlemaps import Map
from STATQ import s3
import os
import io
import boto3

GMaps = Blueprint('GMaps', __name__)
@GMaps.route('/Kort/Målestationer/')
def mapview():
    Filsti = s3.get_object(Bucket=os.environ.get('S3_BUCKET_NAME'), Key=str('Alle Data/Maalestationer_liste.txt'))
    body = Filsti['Body'].read().decode()
    #print(body)
    marker_liste=[]
    icon_url='http://maps.google.com/mapfiles/ms/icons/green-dot.png'
    Firstline = 1
    for lines in body.split("\n"):
        parts = lines.split("\t")
        if Firstline==0:
            try:
                vandloeb = parts[0]
                vandloeb_og_sted = parts[1]
                sted = vandloeb_og_sted.split(',')[1][1:]
                marker_liste.append(dict({
                    'lat':float(parts[-1]),
                    'lng':float(parts[-2]),
                    'infobox':f"""<b>{vandloeb_og_sted}<b><br> <a href='/redirect/{vandloeb}/{sted}'> Se data </a>""",
                    'icon':icon_url
                    }))
            except IndexError:
                Damn = 1
                #print(lines)
        Firstline=0
    
    # creating a map in the view

    sndmap = Map(
        zoom=7.5,
        identifier="sndmap",
        lat=56.1985,
        lng=10.0482,
        style="height:82vh;width:73.6vw;margin:0;", # hardcoded!
        markers = marker_liste
    )

    return render_template('map.html', sndmap=sndmap)

@GMaps.route('/redirect/<string:vandloeb>/<string:valgt_sted>')
def station_chosen(vandloeb, valgt_sted):
    filename = vandloeb
    # Creating grouped-tuple to go to proces file.
    s3_resource = boto3.resource('s3')
    my_bucket = s3_resource.Bucket(os.environ.get('S3_BUCKET_NAME'))
    files = my_bucket.objects.filter(Prefix=str('Alle Data/')+str(filename) +'/')
    filnavne=[]
    Q = []
    H = []
    stationer=[]
    for objects in files:
        sep = '_' #The separator fx FLADBRO KRO_VANDFORING.csv.
        obj = objects.key
        obj = obj.removeprefix('Alle Data/'+str(filename)+'/')
        stationer.append(obj)
    one_group = []; grouped = []
    steder = list(set([x.split('_', 1)[0] for x in stationer]))
    QH_name = None
    for sted in steder:
        #print(f'{sted} == {valgt_sted}')
        if sted.split(',')[1][1:] == valgt_sted: #

            if f'{sted}_VANDSTAND.csv' in stationer:
                
                H_filename = f'{vandloeb}, {valgt_sted}_VANDSTAND.csv'
                H_name = ('Vandstand')
            else:

                H_name = ('Ingen Vandstand')
                H_filename = '#'
            
            if f'{sted}_VANDFORING.csv' in stationer:
                
                Q_filename = f'{vandloeb}, {valgt_sted}_VANDFORING.csv'
                print(Q_filename)
                Q_name = ('Vandføring')
            
            else:
                
                Q_name = ('Ingen Vandføring')
                Q_filename = '#'

            if Q_filename != '#' and H_filename != '#':
               
                QH_name = 'Se QH-kurver'
            
            else:
                
                if Q_filename == '#':
                
                    mangel = 'Ingen vandføringsdata'
                
                elif H_filename == '#':
                    
                    mangel = 'Ingen vandstandsdata'
               
                QH_name = 'QH kurver ikke tilgængelige (%s)' % (mangel)
    try:
        stednavn = valgt_sted.split(';')[1][:]
    except IndexError:
        stednavn = valgt_sted
    grouped.append([stednavn, H_name, H_filename, Q_name, Q_filename, QH_name])
    return render_template('program/one_station_file.html', stationer = stationer, Vandloeb = filename, grouped = grouped, QH_name = QH_name)
