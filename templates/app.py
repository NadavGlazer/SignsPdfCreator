from flask.helpers import send_from_directory
import pdfextract
from flask import Flask, render_template, request, send_file
from werkzeug.utils  import secure_filename
from pdfextract import pdf_to_txt, write_data_in_information_file
import time
from datetime import date
import _thread
from multiprocessing import Process
import platform

app = Flask(__name__)

UPLOAD_FOLDER= "'uploads\'"
app.config['UPLOAD_FOLDER']=UPLOAD_FOLDER
app.config['MAX_CONTENT_PATH']= 10000
app.config['TIME_OUT'] = 0


@app.route('/')
def index():
  print(request.cookies)
  print(request.remote_addr)
  write_data_in_information_file("Browser IP: "+ request.remote_addr + " User: "+str(request.remote_user)+" Agent: "+ str(request.user_agent) + " Cookies: "+str(request.cookies))
  return render_template('index.html')

@app.route('/Start', methods = ['GET', 'POST'])
def InformationExtruderAndLoopStarter():
  if request.method == 'POST':
    f = request.files['file']
   
    if f.filename[-4:] !='.pdf':
      return(f.filename[-4:])
   
    f.save(secure_filename(f.filename))   
    filename= secure_filename(f.filename)[:-4] + "_" + str(date.today().strftime("%d/%m/%Y")) + "_" + str(time.strftime("%H:%M:%S", time.localtime())) +".pdf"
    filename=filename.replace("/", '_')
    filename=filename.replace(":", '_')
    filename=filename.replace(" ", "")
  
    _thread.start_new_thread( pdfextract.pdf_to_txt, (filename, ) )
    return render_template('wait.html', value1=filename,value2 = "page : 0")    


@app.route('/End', methods = ['GET', 'POST'])
def LoopAndFileUploader():
  if request.method == "POST":
    file_name = request.form.get("filename")
    xl_result= secure_filename(file_name)[:-4]+" result.xlsx"
    try:
      with open(file_name[:-4]+".txt") as file:
        for line in file:
          pass
        last_line = line  
      file.close()
    except:
      last_line="error"
    if "Finished" in last_line: 
      return render_template('Finish.html', value1 = xl_result)
    else:
      return render_template('wait.html', value1 = file_name, value2=last_line)

# @app.route('/temp', methods = ['GET', 'POST'])
# def a(val):
#   return render_template('wait.html', value = f)

@app.route('/Finish', methods = ['GET', 'POST'])
def EndAndUploadFile():
  if request.method == "POST":
    file_name = request.form.get("filename")
    if(platform=="linux"):
      return send_file(str(file_name) +" result.xlsx", as_attachment=True)
    else:
       return send_file("../"+str(file_name) +" result.xlsx", as_attachment=True)

if __name__ == '__main__':
    app.run(debug=False)
