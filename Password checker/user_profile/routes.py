import os
from flask import render_template, request, redirect, url_for, session, current_app
from werkzeug.utils import secure_filename
from . import profile_bp

UPLOAD_FOLDER = os.path.join('static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Dummy profile data (ideally should be from database)
profile_data = {
    'name': 'Himanshu Negi',
    'email': 'itsnegii7@gmail.com',
    'profile_pic': None
}

@profile_bp.route('/profile', methods=['GET', 'POST'])
def profile():
    global profile_data

    if request.method == 'POST':
        profile_data['name'] = request.form.get('name')
        profile_data['email'] = request.form.get('email')

        if 'profile_pic' in request.files:
            file = request.files['profile_pic']
            if file.filename != '':
                filename = secure_filename(file.filename)
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                file.save(filepath)
                profile_data['profile_pic'] = filename

        return redirect(url_for('profile_bp.profile'))

    return render_template('profile.html', user=profile_data)
