# -*- coding: utf-8 -*-
"""
    :author: Grey Li (李辉)
    :url: http://greyli.com
    :copyright: © 2019 Grey Li
    :license: MIT, see LICENSE for more details.
"""
import os
import uuid
import re

from flask import Flask, render_template, flash, redirect, url_for, request, send_from_directory, session
from flask_ckeditor import CKEditor, upload_success, upload_fail
from flask_dropzone import Dropzone
# from flask_wtf.csrf import validate_csrf
from wtforms import ValidationError

from forms import LoginForm, SecurityForm, FortyTwoForm, NewPostForm, UploadForm, MultiUploadForm, SigninForm, \
    RegisterForm, SigninForm2, RegisterForm2, RichTextForm

from backend.read_word_metric import create_score_table, create_baseline_list, create_element_table, count_phone_sequence, search_f1, search_f2, search_f3, get_score

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'secret string')

# Custom config
app.config['UPLOAD_PATH'] = os.path.join(app.root_path, 'uploads')
app.config['ALLOWED_EXTENSIONS'] = ['png', 'jpg', 'jpeg', 'gif']

# Flask config
# set request body's max length
# app.config['MAX_CONTENT_LENGTH'] = 3 * 1024 * 1024  # 3Mb

# Flask-CKEditor config
app.config['CKEDITOR_SERVE_LOCAL'] = True
app.config['CKEDITOR_FILE_UPLOADER'] = 'upload_for_ckeditor'

# Flask-Dropzone config
app.config['DROPZONE_ALLOWED_FILE_TYPE'] = 'image'
app.config['DROPZONE_MAX_FILE_SIZE'] = 3
app.config['DROPZONE_MAX_FILES'] = 30

ckeditor = CKEditor(app)
dropzone = Dropzone(app)


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/html', methods=['GET', 'POST'])
def html():
    form = LoginForm()
    if request.method == 'POST':
        username = request.form.get('username')
        flash('Welcome home, %s!' % username)
        return redirect(url_for('index'))
    return render_template('pure_html.html')


@app.route('/basic', methods=['GET', 'POST'])
def basic():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        flash('Welcome home, %s!' % username)
        return redirect(url_for('index'))
    return render_template('basic.html', form=form)

@app.route('/bootstrap', methods=['GET', 'POST'])
def bootstrap():
    # form = SecurityForm(csrf_enabled=False) # 提示 FlaskWTFDeprecationWarning: "csrf_enabled" is deprecated and will be removed in 1.0. Pass meta={'csrf': False} instead.
    form = SecurityForm(meta={'csrf': False})
    sec_level = 0
    
    if form.validate_on_submit():
        sentence = form.sentence.data
        model = form.model.data
        sentence = re.sub('[\u4e00-\u9fa50-9’!"#$%&\'()*+,-./:;<=>?@，。?★、…【】《》？“”‘’！[\\]^_`{|}~\s]+', "", sentence)
        # 去除不可见字符
        sentence = re.sub('[\001\002\003\004\005\006\007\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a]+', '', sentence)
        sentence = sentence.strip('\n').replace(' ','').replace('ʔ','')
        # sentence = sentence.split('\t')[0].replace(' ','').replace('ʔ','')
        # print(sentence)

        if model == 1:
            model = 'iv'
            table = create_score_table(model)
            baseline_list = create_baseline_list(model)
            element_table = create_element_table(model)
        elif model == 2:
            model = 'xv'
            table = create_score_table(model)
            baseline_list = create_baseline_list(model)
            element_table = create_element_table(model)
        elif model == 3:
            model = 'vgg'
            table = create_score_table(model)
            baseline_list = create_baseline_list(model)
            element_table = create_element_table(model)

        try:
            command = "echo {} | phonemize".format(sentence)
            process = os.popen(command)
            sentence = process.readlines()[0]
            sentence = sentence.strip('\n').replace(' ','').replace('ʔ','')
            # print(sentence)
            process.close()
            
            # NPT, NP, res_word = count_phone_sequence('həloʊ bɹiːnoʊ') # ɐɐɐɐɐɛːʌ   |   oʊkeɪ bɹiːnoʊ   |   həloʊ bɹiːnoʊ  
            NPT, NP, res_word = count_phone_sequence(sentence) # ɐɐɐɐɐɛːʌ   |   oʊkeɪ bɹiːnoʊ   |   həloʊ bɹiːnoʊ  
            f1 = search_f1(NP, NPT, table)
            f2 = search_f2(NP, baseline_list)
            f3, word_dic = search_f3(NP, res_word, element_table)
            s = get_score(f1, f2, f3)
            sec_level = get_sec_level(model, s)

            recommendation = get_recommend(sec_level, model, NP, NPT, f1, f2, f3, word_dic, s)
            # print('yes')
            # return render_template('boot321strap.html', form=form, score=round(s,4), sec_level=sec_level, recommend=recommendation)
            return render_template('bootstrap.html', form=form, score=round(s,4), sec_level=sec_level, recommend=recommendation, phoneme=sentence)
        except Exception as e:
            print(e)
            return render_template('bootstrap.html', form=form, sec_level=0, recommend="Input Error!")
    return render_template('bootstrap.html', form=form, sec_level=sec_level)

def get_recommend(sec_level, model, NP, NPT, f1, f2, f3, word_dic, s):
    analy_res = ""
    recom_res = ""

    if sec_level == 1 or sec_level == 2:
        analy_res = "Analysis:\n"
        recom_res = "Recommendation:\n"
        recom_flag = "" # 如果recom_flag = 1，说明触发了 f2<f3的条件

        # recom_flag 2，3 主要是用于判断后续应该加, or .
        if (model=='iv' and NPT<16):
            recom_flag += '2'
        elif (model=='xv' and NPT<16):
            recom_flag += '2'
        elif (model=='vgg' and NPT<11):
            recom_flag += '2'

        if (model=='iv' and NP<23):
            recom_flag += '3'
        if (model=='xv' and NP<21):
            recom_flag += '3'
        if (model=='vgg' and NP<13):
            recom_flag += '3'


        if f2<f3:
            recom_flag += '1'
            word_dic = sorted(word_dic.items(), key=lambda x: x[1], reverse=True)
            bad_phones = [item[0] for item in word_dic[:3]]
            analy_res += "The elements of the input are poor distinctiveness.\n"
            if '2' in recom_flag or '3' in recom_flag:
                recom_res += "You had better select words avoiding phones such as: [{}], ".format(', '.join(bad_phones))
            else:
                recom_res += "You had better select words avoiding phones such as: [{}].".format(', '.join(bad_phones))

        if (model=='iv' and NP<23):
            analy_res += "The length of the input is short.\n"
            if '1' in recom_flag and '2' in recom_flag:
                recom_res += "add {} phones, ".format(23-NP)
            elif '1' in recom_flag:
                recom_res += "add {} phones.".format(23-NP)
            elif '2' in recom_flag:
                recom_res += "You'd better add {} phones, ".format(23-NP)
        elif (model=='xv' and NP<21):
            analy_res += "The length of the input is short.\n" 
            if '1' in recom_flag and '2' in recom_flag:
                recom_res += "add {} phones, ".format(21-NP)
            elif '1' in recom_flag:
                recom_res += "add {} phones.".format(21-NP)
            elif '2' in recom_flag:
                recom_res += "You'd better add {} phones, ".format(21-NP)
        elif (model=='vgg' and NP<13):
            analy_res += "The length of the input is short.\n"
            if '1' in recom_flag and '2' in recom_flag:
                recom_res += "add {} phones, ".format(13-NP)
            elif '1' in recom_flag:
                recom_res += "add {} phones.".format(13-NP)
            elif '2' in recom_flag:
                recom_res += "You'd better add {} phones, ".format(13-NP)
        
        if (model=='iv' and NPT<16):
            analy_res += "The richness of the input is low.\n"
            recom_res += "including {} different phones. ".format(16-NPT) if '1' in recom_flag or '2' in recom_flag else "You'd better add {} different phones. ".format(16-NPT)
        elif (model=='xv' and NPT<16):
            analy_res += "The richness of the input is low.\n"
            recom_res += "including {} different phones. ".format(16-NPT) if '1' in recom_flag or '2' in recom_flag else "You'd better add {} different phones. ".format(16-NPT)
        elif (model=='vgg' and NPT<11):
            analy_res += "The richness of the input is low.\n"
            recom_res += "including {} different phones. ".format(11-NPT) if '1' in recom_flag or '2' in recom_flag else "You'd better add {} different phones. ".format(11-NPT)
        
    return analy_res + "\n" + recom_res


def get_sec_level(model, s):
    sec_level = ""
    if model=='iv':
        if s>=8.1: sec_level = 'High!'
        elif s<6.2: sec_level = 'Low!'
        else: sec_level = 'Medium!'
    elif model == 'xv':
        if s>=8.1: sec_level = 'High!'
        elif s<6.5: sec_level = 'Low!'
        else: sec_level = 'Medium!'
    else:
        if s>=9.35: sec_level = 'High!'
        elif s<8.8: sec_level = 'Low!'
        else: sec_level = 'Medium!'
    
    if sec_level == 'High!': return 3
    elif sec_level == 'Medium!': return 2
    else: return 1

@app.route('/custom-validator', methods=['GET', 'POST'])
def custom_validator():
    form = FortyToForm()
    if form.validate_on_submit():
        flash('Bingo!')
        return redirect(url_for('index'))
    return render_template('custom_validator.html', form=form)


@app.route('/uploads/<path:filename>')
def get_file(filename):
    return send_from_directory(app.config['UPLOAD_PATH'], filename)


@app.route('/uploaded-images')
def show_images():
    return render_template('uploaded.html')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def random_filename(filename):
    ext = os.path.splitext(filename)[1]
    new_filename = uuid.uuid4().hex + ext
    return new_filename


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    form = UploadForm()
    if form.validate_on_submit():
        f = form.photo.data
        filename = random_filename(f.filename)
        f.save(os.path.join(app.config['UPLOAD_PATH'], filename))
        flash('Upload success.')
        session['filenames'] = [filename]
        return redirect(url_for('show_images'))
    return render_template('upload.html', form=form)


@app.route('/multi-upload', methods=['GET', 'POST'])
def multi_upload():
    form = MultiUploadForm()

    if request.method == 'POST':
        filenames = []

        # check csrf token
        try:
            validate_csrf(form.csrf_token.data)
        except ValidationError:
            flash('CSRF token error.')
            return redirect(url_for('multi_upload'))

        # check if the post request has the file part
        if 'photo' not in request.files:
            flash('This field is required.')
            return redirect(url_for('multi_upload'))

        for f in request.files.getlist('photo'):
            # if user does not select file, browser also
            # submit a empty part without filename
            # if f.filename == '':
            #     flash('No selected file.')
            #    return redirect(url_for('multi_upload'))
            # check the file extension
            if f and allowed_file(f.filename):
                filename = random_filename(f.filename)
                f.save(os.path.join(
                    app.config['UPLOAD_PATH'], filename
                ))
                filenames.append(filename)
            else:
                flash('Invalid file type.')
                return redirect(url_for('multi_upload'))
        flash('Upload success.')
        session['filenames'] = filenames
        return redirect(url_for('show_images'))
    return render_template('upload.html', form=form)


@app.route('/dropzone-upload', methods=['GET', 'POST'])
def dropzone_upload():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            return 'This field is required.', 400
        f = request.files.get('file')

        if f and allowed_file(f.filename):
            filename = random_filename(f.filename)
            f.save(os.path.join(
                app.config['UPLOAD_PATH'], filename
            ))
        else:
            return 'Invalid file type.', 400
    return render_template('dropzone.html')


@app.route('/two-submits', methods=['GET', 'POST'])
def two_submits():
    form = NewPostForm()
    if form.validate_on_submit():
        if form.save.data:
            # save it...
            flash('You click the "Save" button.')
        elif form.publish.data:
            # publish it...
            flash('You click the "Publish" button.')
        return redirect(url_for('index'))
    return render_template('2submit.html', form=form)


@app.route('/multi-form', methods=['GET', 'POST'])
def multi_form():
    signin_form = SigninForm()
    register_form = RegisterForm()

    if signin_form.submit1.data and signin_form.validate():
        username = signin_form.username.data
        flash('%s, you just submit the Signin Form.' % username)
        return redirect(url_for('index'))

    if register_form.submit2.data and register_form.validate():
        username = register_form.username.data
        flash('%s, you just submit the Register Form.' % username)
        return redirect(url_for('index'))

    return render_template('2form.html', signin_form=signin_form, register_form=register_form)


@app.route('/multi-form-multi-view')
def multi_form_multi_view():
    signin_form = SigninForm2()
    register_form = RegisterForm2()
    return render_template('2form2view.html', signin_form=signin_form, register_form=register_form)


@app.route('/handle-signin', methods=['POST'])
def handle_signin():
    signin_form = SigninForm2()
    register_form = RegisterForm2()

    if signin_form.validate_on_submit():
        username = signin_form.username.data
        flash('%s, you just submit the Signin Form.' % username)
        return redirect(url_for('index'))

    return render_template('2form2view.html', signin_form=signin_form, register_form=register_form)


@app.route('/handle-register', methods=['POST'])
def handle_register():
    signin_form = SigninForm2()
    register_form = RegisterForm2()

    if register_form.validate_on_submit():
        username = register_form.username.data
        flash('%s, you just submit the Register Form.' % username)
        return redirect(url_for('index'))
    return render_template('2form2view.html', signin_form=signin_form, register_form=register_form)


@app.route('/ckeditor', methods=['GET', 'POST'])
def integrate_ckeditor():
    form = RichTextForm()
    if form.validate_on_submit():
        title = form.title.data
        body = form.body.data
        flash('Your post is published!')
        return render_template('post.html', title=title, body=body)
    return render_template('ckeditor.html', form=form)


# handle image upload for ckeditor
@app.route('/upload-ck', methods=['POST'])
def upload_for_ckeditor():
    f = request.files.get('upload')
    if not allowed_file(f.filename):
        return upload_fail('Image only!')
    f.save(os.path.join(app.config['UPLOAD_PATH'], f.filename))
    url = url_for('get_file', filename=f.filename)
    return upload_success(url, f.filename)

if __name__ == "__main__":
    app.run("0.0.0.0", port=8081, debug=True)
