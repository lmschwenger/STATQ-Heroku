import io
import os

import boto3
from flask import render_template, request, Blueprint, redirect, current_app, flash, url_for
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from STATQ import s3
from STATQ.program.forms import ProcesFileForm
from STATQ.program.utils import (parse_data, parse_databasedata,
                                 plotly_hydro, plotly_QH, plotly_kemi, plotly_season, plotly_bar, plotly_stoftransport)

program = Blueprint('program', __name__)


@program.route('/StatQ/dine-filer/', methods=['GET', 'POST'])
@login_required
def upload_file():
    s3_resource = boto3.resource('s3')
    my_bucket = s3_resource.Bucket(os.environ.get('S3_BUCKET_NAME'))
    files = my_bucket.objects.filter(Prefix=str(current_user.username) + "/")
    filenames = []
    for objects in files:
        obj = objects.key
        obj = obj.removeprefix(str(current_user.username) + '/')
        filenames.append(obj)
    user_folder = current_user.username + '/'

    if request.files:
        file = request.files['myFile']
        if file.filename == "":
            flash("Filen skal have et navn", 'danger')
            return redirect(request.url)

        if not allowed_filetype(file.filename):
            flash("Filtype er ikke understøttet", 'danger')
            return redirect(request.url)

        else:
            filename = secure_filename(file.filename)
        try:
            s3.upload_fileobj(file, 'statq-bucket', str(user_folder) + str(filename))
        except Exception as e:
            flash("Noget gik galt: " + e, 'danger')
        # s3_resource.meta.client.upload_file(str(file.filename), 'statq-bucket',str(user_folder)+str(filename))
        flash("Fil er uploadet", 'success')
        return redirect(url_for('program.your_files'))

    return render_template('program/proces_file.html', files=files, filenames=filenames)


@program.route('/StatQ/dine-filer/', methods=['GET', 'POST'])
@login_required
def your_files():
    s3_resource = boto3.resource('s3')
    my_bucket = s3_resource.Bucket(os.environ.get('S3_BUCKET_NAME'))
    files = my_bucket.objects.filter(Prefix=str(current_user.username) + "/")
    return render_template('program/proces_file.html', files=files, filepaths=filepaths)


@program.route('/StatQ/dine-filer/<string:filename>/slet-fil')
@login_required
def delete_file(filename):
    s3.delete_object(Bucket=os.environ.get('S3_BUCKET_NAME'), Key=str(current_user.username) + '/' + str(filename))
    flash(str(filename) + " er blevet slettet", 'success')
    return redirect(url_for('program.your_files'))


@program.route('/StatQ/dine-filer/<string:filename>', methods=['GET', 'POST'])
@login_required
def proces_file(filename):
    form = ProcesFileForm
    file = s3.get_object(Bucket=os.environ.get('S3_BUCKET_NAME'), Key=str(current_user.username) + '/' + str(filename))
    df = parse_data(io.BytesIO(file['Body'].read()))
    if isinstance(df, str):
        flash(df, 'danger')
        return redirect(url_for('program.your_files'))
    if type(df) == list:
        graphJSONseason = plotly_stoftransport(df)
        # file_path = io.BytesIO(file['Body'].read())
        # print(file_path)
        # new_df = pd.read_csv(file_path, encoding = "ISO-8859-1", decimal=',', delimiter=";")
        # newsub_df = df.head(1)
        # newsub_df.pop("År")
        # newsub_df.pop("Måned")
        # newsub_df.pop("Resultat")

        # headings = list(newsub_df.columns)
        # information = list(newsub_df.iloc[0])
        headings = ['Filbeskrivelse ']
        information = ['Kommer snart']
        infolist = zip(headings, information)
        graphJSONraw = None
    else:
        sub_df = df.head(1)
        sub_df.pop("Resultat")
        # parameters = str(set(df['Parameter']))
        # sub_df['Parameter'] = parameters
        headings = list(sub_df.columns)
        information = list(sub_df.iloc[0])

        infolist = zip(headings, information)
        string_test = str(df['Parameter'].iloc[0])
        cond1 = 'Vandføring'
        cond2 = 'Vandstand'

        if string_test == cond1 or string_test == cond2:
            graphJSONseason = plotly_season(df)
            graphJSONraw = plotly_hydro(df)
            graphJSONbar = plotly_bar(df)
        elif string_test != cond1 and string_test != cond2:
            graphJSONseason = None
            graphJSONbar = None
            graphJSONraw = plotly_kemi(df)

    return render_template('program/file_results.html', graphJSONbar=graphJSONbar, graphJSONraw=graphJSONraw,
                           graphJSONseason=graphJSONseason, form=form, infolist=infolist, filename=filename)


@program.route('/StatQ/database/<string:Vandloeb>/<string:filename>', methods=['GET', 'POST'])
# @login_required
def proces_databasefile(Vandloeb, filename):
    sted = filename
    print(sted)
    # filename = filename.split(",")[1][1:].replace(";",",")
    # print(filename)
    if filename == '#':
        flash('De ønskede data findes ikke...', 'danger')
        return redirect(url_for('program.station_files', filename=Vandloeb))
    form = ProcesFileForm
    file = s3.get_object(Bucket=os.environ.get('S3_BUCKET_NAME'),
                         Key=str('Alle Data/') + str(Vandloeb) + '/' + str(sted))
    df = parse_databasedata(io.BytesIO(file['Body'].read()))
    if isinstance(df, str):
        flash(df, 'danger')
        return redirect(url_for('program.your_files'))
    if type(df) == list:
        graphJSONseason = plotly_stoftransport(df)
        # file_path = io.BytesIO(file['Body'].read())
        # print(file_path)
        # new_df = pd.read_csv(file_path, encoding = "ISO-8859-1", decimal=',', delimiter=";")
        # newsub_df = df.head(1)
        # newsub_df.pop("År")
        # newsub_df.pop("Måned")
        # newsub_df.pop("Resultat")

        # headings = list(newsub_df.columns)
        # information = list(newsub_df.iloc[0])
        headings = ['Filbeskrivelse ']
        information = ['Kommer snart']
        infolist = zip(headings, information)
        graphJSONraw = None
    else:
        sub_df = df.head(1)
        sub_df.pop("Resultat")
        # parameters = str(set(df['Parameter']))
        # sub_df['Parameter'] = parameters
        headings = list(sub_df.columns)
        information = list(sub_df.iloc[0])

        infolist = zip(headings, information)
        string_test = str(df['Parameter'].iloc[0])
        cond1 = 'Vandføring'
        cond2 = 'Vandstand'

        if string_test == cond1 or string_test == cond2:
            graphJSONseason = plotly_season(df)
            graphJSONraw = plotly_hydro(df)
            graphJSONbar = plotly_bar(df)
        elif string_test != cond1 and string_test != cond2:
            graphJSONseason = None
            graphJSONbar = None
            graphJSONraw = plotly_kemi(df)

    return render_template('program/file_results.html', graphJSONbar=graphJSONbar, graphJSONraw=graphJSONraw,
                           graphJSONseason=graphJSONseason, form=form, infolist=infolist, filename=filename)


@program.route('/StatQ/database/<string:Vandloeb>/QH-kurver/<string:Q_file>/<string:H_file>/', methods=['GET', 'POST'])
# @login_required
def proces_databaseQH(Vandloeb, Q_file, H_file):
    if Q_file == '#' or H_file == '#':
        flash('De ønskede data findes ikke...', 'danger')
        return redirect(url_for('program.station_files', filename=Vandloeb))
    form = ProcesFileForm
    Q_file = s3.get_object(Bucket=os.environ.get('S3_BUCKET_NAME'),
                           Key=str('Alle Data/') + str(Vandloeb) + '/' + str(Q_file))
    Q = parse_databasedata(io.BytesIO(Q_file['Body'].read()))
    H_file = s3.get_object(Bucket=os.environ.get('S3_BUCKET_NAME'),
                           Key=str('Alle Data/') + str(Vandloeb) + '/' + str(H_file))
    H = parse_databasedata(io.BytesIO(H_file['Body'].read()))
    graphJSONQH = plotly_QH(Q, H)
    return render_template('program/QH_results.html', graphJSONQH=graphJSONQH)


@program.route('/StatQ/kom-godt-i-gang')
def kom_godt_i_gang():
    return render_template('program/kom-godt-i-gang.html')


@program.route('/StatQ/database')
# @login_required
def database():
    s3_resource = boto3.resource('s3')
    my_bucket = s3_resource.Bucket(os.environ.get('S3_BUCKET_NAME'))
    Q_files = my_bucket.objects.filter(Prefix="/Alle Data/Q/")
    Q_filenames = []
    for objects in Q_files:
        obj = objects.key
        obj = obj.removeprefix('/')
        Q_filenames.append(obj)
    H_files = my_bucket.objects.filter(Prefix="/Alle Data/H/")
    H_filenames = []
    for objects in H_files:
        obj = objects.key
        obj = obj.removeprefix('/')
        H_filenames.append(obj)
        print(H_filenames)
    s3 = boto3.client('s3')

    Q_path = s3.get_object(Bucket=os.environ.get('S3_BUCKET_NAME'), Key=str('Alle Data/Q_stationer.txt'))

    filestr = Q_path['Body'].read().decode('latin-1')
    Q_files = filestr.split("\n")
    Q_files = sorted([x.strip('\r') for x in Q_files])

    H_path = s3.get_object(Bucket=os.environ.get('S3_BUCKET_NAME'), Key=str('Alle Data/Q_stationer.txt'))
    filestr = H_path['Body'].read().decode('latin-1')
    H_files = filestr.split("\n")
    H_files = sorted([x.strip('\r') for x in H_files])

    return render_template('program/database.html', Q_filenames=Q_filenames, H_filenames=H_filenames, Q_files=Q_files,
                           H_files=H_files)


@program.route('/StatQ/database/<string:filename>')
def station_files(filename):
    s3_resource = boto3.resource('s3')
    my_bucket = s3_resource.Bucket(os.environ.get('S3_BUCKET_NAME'))
    files = my_bucket.objects.filter(Prefix=str('Alle Data/') + str(filename) + '/')
    filnavne = []
    Q = []
    H = []
    stationer = []
    for objects in files:
        sep = '_'  # The separator fx FLADBRO KRO_VANDFORING.csv.
        obj = objects.key
        obj = obj.removeprefix('Alle Data/' + str(filename) + '/')
        stationer.append(obj)
    one_group = [];
    grouped = []
    steder = list(set([x.split('_', 1)[0] for x in stationer]))
    print(steder)
    for sted in steder:
        if str(sted) + '_VANDSTAND.csv' in stationer:
            H_filename = (sted) + '_VANDSTAND.csv'
            H_name = ('Vandstand')
        else:
            H_name = ('Ingen Vandstand')
            H_filename = '#'
        if str(sted) + '_VANDFORING.csv' in stationer:
            Q_filename = (sted) + '_VANDFORING.csv'
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
        grouped.append([sted, H_name, H_filename, Q_name, Q_filename, QH_name])
    # stripped = [x.split('_', 1)[0] for x in stationer]
    # list_of_sets = list(set(stripped))
    # grouped = [list(i) for j, i in itertools.groupby(sorted(stationer))]
    return render_template('program/station_files.html', stationer=stationer, Vandloeb=filename, grouped=grouped,
                           QH_name=QH_name)


@program.route('/StatQ/hjaelp')
def help():
    return render_template('program/help.html')


def allowed_filetype(filename):
    if not "." in filename:
        return False

    ext = filename.rsplit(".", 1)[1]

    if ext.upper() in current_app.config["ALLOWED_FILE_EXTENSIONS"]:
        return True

    else:
        return False
