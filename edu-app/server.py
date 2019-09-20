from flask import Flask, render_template, request
from eduscripts import get_output

# Create the application object
app = Flask(__name__)

app.config["CACHE_TYPE"] = "null"

@app.route("/")
def home_page():
	return render_template('edu-cater-app.html')

# start the server with the 'run()' method
if __name__ == "__main__":
	app.run(debug=True) #will run locally http://127.0.0.1:5000/

@app.route('/output')

def tag_output():
	# pull input
   some_input1 =request.args.get('user_input1')
   some_input2 =request.args.get('user_input2')

   # Case if empty
   if some_input1 == '' or some_input2 == '':
       return render_template("index.html",
                              my_input1 = '',
							  my_input2 = '',
                              my_form_result="Empty")
   else:
	   return render_template("edu-cater-app.html", my_input1=some_input1, my_input2=some_input2, my_output=get_output(some_input1, some_input2)[1], myimg="coursera_lda_network_output.png", my_form_result="NotEmpty")

@app.after_request
def add_header(response):
    response.headers['Pragma'] = 'no-cache'
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Expires'] = '0'
    return response
