from flask import Flask, render_template, request, flash, redirect, url_for, send_from_directory, jsonify
from werkzeug.utils import secure_filename
import os
from config import app_config_dict as cfg
from app.rfm import rfm_analysis as rfm, list_all_files as rfm_files


def create_app(config_name):
	# Create application object
	app = Flask(__name__.split('.')[0], instance_relative_config=True)
	app.config.from_object(cfg[config_name])  # Stand Flask and Flask_extension Configuration
	app.config.from_pyfile('config.cfg')

	def allowed_file(filename):
		return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config.get('ALLOWED_EXTENSIONS')

	@app.route("/")
	def index():
		return redirect(url_for('upload'))

	@app.route("/upload", methods=['GET', 'POST'])
	def upload():
		if request.method == 'POST':
			# check if the post request has the file part
			if 'file' not in request.files:
				flash('No file part exist in the request', 'error')
				return redirect(request.url)
				# msg = """<div class="alert alert-danger" role="alert">No file part</div>"""
				# render_template('index.html', msg=msg)
			file = request.files['file']

			# if user does not select file, browser also
			# submit an empty part without filename
			if file.filename == '':
				flash('No file Selected', 'warning')
				return redirect(request.url)
				# msg = """<div class="alert alert-danger" role="alert">You didn't select any file</div>"""
				# render_template('index.html', msg=msg)

			if file and allowed_file(file.filename):
				filename = secure_filename(file.filename)
				save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
				if os.path.exists(save_path):
					flash('File {} already exists, and it will be replaced by the new upload'.format(filename), 'warning')
				file.save(save_path)
				flash('File {} was uploaded successfully'.format(filename), 'success')
				return redirect(request.url)

		elif request.method == 'GET':
			return render_template('upload.html', files=rfm_files())

		return render_template('upload.html')

	@app.route('/rfm/<filename>')
	def show_rfm_single(filename):
		return render_template('result.html', filename=filename)

	@app.route('/api/rfm/<filename>')
	def data_rfm_single(filename):
		dic = rfm(filename)
		from .schema import SingleSegmentSchema
		schema = SingleSegmentSchema()
		print(dic)
		result = schema.dump(rfm(filename))
		print(result)
		return jsonify(result.data)

	@app.route('/rfm')
	def show_rfm_all():
		data = rfm()
		return render_template('result.html', filename=None, data=data)

	@app.route('/uploads/<filename>')
	def uploaded_file(filename):
		# redirect(url_for('uploaded_file', filename=filename))
		return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

	@app.template_filter('fname')
	def filter_filename(value):
		file_path, file_extension = os.path.splitext(value)
		filename = file_path.split('\\')[-1]  # Get rid of containing folders
		return filename+file_extension


	return app
