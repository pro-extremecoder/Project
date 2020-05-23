import os
from flask import redirect, url_for, request, render_template, abort
from flask import send_from_directory, make_response
from flask_security import current_user, logout_user
from flask_login import login_required
from flask_wtf import Form
from app import app, db
from models import User, Tag, Project
from forms import ExtendedRegisterForm, ProjectForm
from additional import randomString, get_ending

@app.route('/')
def index():
	return render_template('home.html')

@app.errorhandler(404)
def not_found(e):
	return render_template('404.html'), 404

# For user model
@app.route('/change-user')
def change_user():
	logout_user()
	return redirect(url_for('security.login'))

@app.route('/users/<username>')
def get_profile(username):
	user = User.query.filter(User.nickname==username).first()
	if not user:
		abort(404)
	nickname = user.nickname
	print(nickname)
	about = user.about_me
	avatar_file = user.avatar
	subs = user.subscriptions
	projects = user.myprojects
	return render_template('for_user_model/profile.html',
							nickname=nickname,
							about=about,
							avatar_file=avatar_file,
							subs=subs,
							projects=projects)


@app.route('/edit',methods=['GET','POST'])
@login_required
def edit():
	#BotVasy
	bot = User.query.filter_by(nickname='BotVasy').first()
	if request.method == 'POST':
		status = request.form.get('status')
		user = User.query.filter(User.nickname==current_user.nickname).first()
		if status == 'for_avatar':
			avatar_file = request.files['avatar_file']
			filename = f'avatars/{randomString(20)}{get_ending(avatar_file.filename)}'
			print(f"[DEBUG]::{app.config['UPLOAD_FOLDER']}")
			avatar_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

			

			os.remove(os.path.join(app.config['UPLOAD_FOLDER'],f"avatars/{user.avatar.replace('/static/avatars','')}"))
			user.avatar = url_for('static',filename=filename)
			db.session.commit()
			print('[INFO] :: Success setting new avatar')
			return make_response({'filename' : filename}, 200)
		elif status == 'delete':
			print('[INFO]::STATUS DELETE')

			#db.session.add(bot)
			for project in user.ownprojects:
				project.admin = bot
			db.session.delete(user)
			db.session.commit()
			return make_response('Success',200)
		else:
			form = ExtendedRegisterForm(request.form)
			is_nick_edit = False
			is_email_edit = False
			if user.nickname != request.form['nickname']:
				is_nick_edit = True 
			if user.email != request.form['email']:
				is_email_edit = True 
			is_valid = True
			validation = Form.validate(form)
			form.password.errors.clear()
			form.password_confirm.errors.clear()
			'''if not validation:
				is_valid = False'''
			if form.email.errors != []:
				is_valid = False
			if not form.nick_validate(is_nick_edit):
				is_valid = False
			if not form.email_validate(is_email_edit):
				is_valid = False
			if not form.about_me_validate():
				is_valid = False
			print(f'[DEBUG]::is_nick_edit:{is_nick_edit}')
			print(f'[DEBUG]::is_email_edit:{is_email_edit}')


			if is_valid:
				print('[INFO]::IS VALID EDIT')
				user.nickname = form.nickname.data
				user.email =  form.email.data
				user.about_me =  form.about_me.data
				db.session.commit()
				return redirect(url_for('get_profile',username=user.nickname))
			else:
				nickname = current_user.nickname
				email = current_user.email
				avatar_path = current_user.avatar
				print(f'[DEBUG]:: {avatar_path}')
				about_me = current_user.about_me
				
				return render_template('for_user_model/edit_profile.html',
					form=form,
					nickname=nickname,
					email=email,
					avatar_path=avatar_path,
					about_me=about_me
				)


	form = ExtendedRegisterForm()
	nickname = current_user.nickname
	email = current_user.email
	avatar_path = current_user.avatar
	print(f'[DEBUG]:: {avatar_path}')
	about_me = current_user.about_me
	
	print(f'[DEBUG]::input about {about_me}')
	return render_template('for_user_model/edit_profile.html',
		form=form,
		nickname=nickname,
		email=email,
		avatar_path=avatar_path,
		about_me=about_me
	)


#---------------------------------
#For project model

@app.route('/projects/create', methods=['GET','POST'])
@login_required
def create_project():
	form = ProjectForm()
	if form.validate_on_submit():
		team_name = form.team_name.data
		project_name = form.project_name.data
		selected_tags = form.tags.data
		about = form.about.data
		user = User.query.filter_by(nickname=current_user.nickname).first()

		project = Project(team_name=team_name,
						  project_name=project_name,
						  about=about,
						  admin=user,
						  logo=url_for('static', filename=f'project_logos/{team_name}.jpg')
		)

		filename = form.team_name.data+'.jpg'
		logo_file = open(os.getcwd()+'/static/project_logos/'+filename,'wb')
		default_logo = open(os.getcwd()+'/static/site-images/'+'default-project-logo.jpg','rb')
		logo_file.write(default_logo.read())
		project.members.append(user)
		logo_file.close()
		default_logo.close()
		for tag in selected_tags:
			t = Tag.query.filter_by(name=tag).first()
			project.tags.append(t)
		db.session.add(project)
		db.session.commit()
		return redirect(url_for('get_project',p=project.team_name)) #!!!!!Change 

	tags = Tag.query.all()
	return render_template('for_project_model/create.html',form=form,tags=tags)

@app.route('/projects/<p>')
def get_project(p):
	project = Project.query.filter_by(team_name=p).first()
	if project:
		return render_template('for_project_model/project_page.html', project=project)
	abort(404)

@app.route('/projects/<p>/edit', methods=['GET', 'POST'])
@login_required
def edit_project(p):
	project = Project.query.filter_by(team_name=p).first()
	if project.admin.nickname != current_user.nickname:
		abort(403)
	else:
		form = ProjectForm()
		if request.method == 'POST':
			status = request.form.get('status')
			if status == "for_avatar":
				avatar_file = request.files['avatar_file']
				filename = f'project_logos/{randomString(20)}{get_ending(avatar_file.filename)}'
				print(f"[DEBUG]::{app.config['UPLOAD_FOLDER']}")

				avatar_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

				os.remove(os.path.join(app.config['UPLOAD_FOLDER'],f"project_logos/{project.logo.replace('/static/project_logos','')}"))
				project.logo = url_for('static',filename=filename)
				db.session.commit()
				print('[INFO] :: Success setting new project logo')
				return make_response({'filename' : filename}, 200)
			elif status == "delete":
				print('[INFO] :: status - project deleted')
				#!!! [WARNING]:: YOU MUST DELETE ALL POSTS, COMMENTS AND CHATS
				db.session.delete(project)
				db.session.commit()
				return make_response('Success', 200)
			else:
				validation = Form.validate(form)

				if form.validate(instance=project):
					project.team_name = form.team_name.data
					project.project_name = form.project_name.data
					project.tags.clear()
					for tag in form.selected_tags:
						t = Tag.query.filter_by(name=tag).first()
						project.tags.append(t)
					project.about = form.about.data
					db.session.commit()
					return redirect(url_for('get_project',p=project.team_name))
				else:
					tags = Tag.query.all()
					logo = project.logo
					return render_template('for_project_model/edit.html', form=form, tags=tags, logo=logo)
					
		form.team_name.data = project.team_name
		form.project_name.data = project.project_name
		form.tags.data = [i.name for i in project.tags]
		form.about.data = project.about
		form.selected_tags = [i.name for i in project.tags]
		print(f'[DEBUG]::{form.selected_tags}')
		tags = Tag.query.all()
		logo = project.logo
		return render_template('for_project_model/edit.html', form=form, tags=tags, logo=logo)

#--------------------------
@app.route('/base')
def index1():
	return render_template('base.html')

@app.route('/test', methods=['GET','POST'])
def test():
	form = ProjectForm()
	return render_template('test.html', form=form)
