# TODO: always use isort
# TODO: remove unused imports
# TODO: format doc using the shortcut
# TODO: use pylint on files when you finish a major work
# TODO: always use auto save
# TODO: use winkey+V
import json
from random import randint


import utils
from flask import Flask, render_template, request, send_file
from fpdf import FPDF
from werkzeug.utils import secure_filename
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import _thread
import os

app = Flask(__name__)
json_file = open("config.json", encoding="utf8")
json_data = json.load(json_file)

UPLOAD_FOLDER = json_data["docker_upload_folder"]
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_PATH"] = json_data["MAX_CONTENT_PATH"]
app.config["TIME_OUT"] = json_data["TIME_OUT"]


@app.route("/")
def index():
    """Starts the website"""
    return render_template("index.html")


@app.route("/LoopStarter", methods=["POST"])
def loop_starter():
    """Sends the user to his destination, with the needed information"""
    if request.method == "POST":
        file_id = randint(
            json_data["id_random_range"][0], json_data["id_random_range"][1]
        )
        current_time = utils.get_current_time()
        open(
            utils.generate_text_file_name(file_id, current_time), "a", encoding="utf-8"
        ).close()

        app.logger.info(
            "Each line in the info file is in the following order, seperated by a '*' : page number, amount of images, template name, text, path of each image"
        )

        if request.form.get("Mixed"):
            template_name = json_data["3_images_mixed_html_template_name"]
        elif request.form.get("Horizontal"):
            template_name = json_data["3_images_Horizontal_html_template_name"]
        elif request.form.get("Vertical") : 
            template_name = json_data["4_images_vertical_html_template_name"]

        return render_template(
            template_name,
            FileID = file_id,
            Time = current_time,
            PageNumber = 1,
            PageCounter = 1,
        )


@app.route("/LoopContinue", methods=["POST"])
def loop_continue():
    """Continues the loop or ending it, creating the pictures and the pdf"""
    if request.method == "POST":
        # Extracting all the info from the form, both the hidden and the shown
        title_text1 = request.form.get("TitleTextF1")
        first_pic = request.files.get("FirstPic")
        second_pic = request.files.get("SecondPic")
        third_pic = request.files.get("ThirdPic")
        current_time = request.form.get("CurrentTime")
        file_id = request.form.get("FileID")
        template_type = request.form.get("TemplateType")
        page_number = request.form.get("PageNumber")
        page_counter = request.form.get("PageCounter")

        is_new_3_mix_page = request.form.get("NewMix3")
        is_new_3_horizontal_page = request.form.get("NewHorizontal3")
        is_new_4_vertical_page = request.form.get("NewVertical4")

        is_4_image_page =  (str(template_type) == "4ImagesVertical")

        fourth_pic = "temp"

        if is_4_image_page:
           title_text2 = request.form.get("TitleTextF2")
           fourth_pic = request.files.get("FourthPic")


        if (
            "application/octet-stream" in str(first_pic)
            or "application/octet-stream" in str(second_pic)
            or "application/octet-stream" in str(third_pic)
            or "application/octet-stream" in str(fourth_pic)
        ):            
            app.logger.info("Page number %s is missing at least one image", page_number)

        else:

            temp_info = ""
            # "Information" has the following data: page number,
            #  pic amount, html template, title text, the pictures
            temp_info = str(template_type[0])
            temp_info = temp_info + "*" + str(template_type)
            temp_info = utils.get_fixed_title_text(temp_info, title_text1)

            if is_4_image_page:
                temp_info = utils.get_fixed_title_text(temp_info, title_text2)

            # Saving the first picure with the id
            # ,time and number and page number and saving in in the information array
            file_type = utils.get_file_type(secure_filename(first_pic.filename))
            temp_info = temp_info + utils.save_image(
                file_type, file_id, current_time, page_counter, 1, first_pic, app
            )
            # Saving the second picure with the id,
            # time and number and page number and saving in in the information array

            file_type = utils.get_file_type(secure_filename(second_pic.filename))
            temp_info = temp_info + utils.save_image(
                file_type, file_id, current_time, page_counter, 2, second_pic, app
            )

            # Saving the third picure with the id,
            # time and number and page number and saving in in the information array

            file_type = utils.get_file_type(secure_filename(third_pic.filename))
            temp_info = temp_info + utils.save_image(
                file_type, file_id, current_time, page_counter, 3, third_pic, app
            )

            # Saving the fourth picure with the id,
            # time and number and page number and saving in in the information array
            if is_4_image_page:
                file_type = utils.get_file_type(secure_filename(fourth_pic.filename))
                temp_info = temp_info + utils.save_image(
                    file_type, file_id, current_time, page_counter, 4, fourth_pic, app
                )

            app.logger.info("Page %s information : %s", page_number, temp_info)

            with open(
                utils.generate_text_file_name(file_id, current_time),
                "a",
                encoding="utf-8",
            ) as text_file:
                text_file.write(temp_info + "\n")

            page_number = int(page_number)
            page_counter = int(page_counter)

            page_number += 1
            page_counter += 1
            print(temp_info)


        if is_new_3_mix_page or is_new_3_horizontal_page or is_new_4_vertical_page:            
            if is_new_3_horizontal_page:
                temp_template = json_data["3_images_Horizontal_html_template_name"]
            elif is_new_3_mix_page :
                temp_template = json_data["3_images_mixed_html_template_name"]
            else:
                temp_template = json_data["4_images_vertical_html_template_name"]
            return render_template(
                temp_template,
                FileID = file_id,
                Time = current_time,
                PageNumber = page_number,
                PageCounter = page_counter,
            )

        else:

            information = []
            with open(
                utils.generate_text_file_name(file_id, current_time),
                "r+",
                encoding="utf-8",
            ) as text_file:
                for line in text_file:
                    information.append(line.split("*"))

            if not information:
                app.logger.info("0 pages were submitted, sending to home page")
                return render_template("index.html")

            app.logger.info("this project`s info : %s", information)

            _thread.start_new_thread(
                utils.information_to_pdf,
                (
                    information,
                    file_id,
                    current_time,
                    json_data,
		            app,
                ),
            )

        return render_template(
            "wait.html",
            pdf_name=utils.generate_pdf_file_name(file_id, current_time),
            info_file=utils.generate_text_file_name(file_id, current_time),
            time = current_time,
            file_id = file_id,
        )


@app.route("/ReLoad", methods=["GET", "POST"])
def reload_from_id_time():
    """Sends the user the finished pdf"""
    time = request.form.get("Time")
    file_id = request.form.get("FileID")
    text_file_name = utils.generate_text_file_name(file_id,time)
    if not os.path.isfile(text_file_name):
        return render_template("index.html")

    information = []
    with open(
        text_file_name,
        "r+",
        encoding="utf-8",
    ) as text_file:
        for line in text_file:
            information.append(line.split("*"))

    if not information:
        app.logger.info("0 pages were submitted, sending to home page")
        return render_template("index.html")

    app.logger.info("this project`s info : %s", information)

    _thread.start_new_thread(
        utils.information_to_pdf,
        (
            information,
            file_id,
            time,
            json_data,
		    app,
        ),
    )
    open(
        utils.generate_update_text_file_name(file_id, time), "a", encoding="utf-8"
    ).close()   

    return render_template(
        "wait.html",
        pdf_name=utils.generate_pdf_file_name(file_id, time),
        info_file=utils.generate_text_file_name(file_id, time),
        file_id= file_id,
        time= time,
        update_msg = "Starting",
    )


@app.route("/UploadFile", methods=["GET", "POST"])
def upload_file():
    """Sends the user the finished pdf"""
    file_name = request.form.get("filename")
    return send_file(file_name, as_attachment=True)


@app.route("/TempHtmlFile/<html_file>")
def load_temp_html_file(html_file):
    """Loads the html file"""
    print(html_file)
    return render_template(html_file)


@app.route('/End', methods = ['GET', 'POST'])
def LoopAndFileUploader():
  if request.method == "POST":
    pdf_file_name = request.form.get("PDFName")
    info_file_name = request.form.get("InfoFile")
    file_id = request.form.get("FileID")
    time = request.form.get("Time")
    

    update_file_name = utils.generate_update_text_file_name(file_id, time)

    last_line = "starting"
        
    with open("/Test/templates/" + update_file_name, "r+") as update_file:
        for line in update_file:
            last_line = line 

    if "Finished" in last_line:
            return render_template('finish.html', pdf_name = pdf_file_name)    

    return render_template('wait.html', pdf_name = pdf_file_name, info_file=info_file_name, file_id = file_id, time= time, update_msg = last_line)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5300)
