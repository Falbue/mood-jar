from flask import Flask, render_template

app = Flask(__name__)

@app.context_processor
def inject_files():
    css_directory = os.path.join(app.static_folder, 'styles')
    js_directory = os.path.join(app.static_folder, 'scripts')
    
    css_files = get_files(css_directory, ['.css'])
    js_files = get_files(js_directory, ['.js'])
    
    return dict(css_files=css_files, js_files=js_files)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
