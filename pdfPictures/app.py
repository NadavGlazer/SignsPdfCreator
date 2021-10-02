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
from html2image import Html2Image
from werkzeug.utils import secure_filename

app = Flask(__name__)
# TODO: add this information to readme and move to config.json file
json_file = open("pdfPictures\config.json", encoding="utf8")
json_data = json.load(json_file)

UPLOAD_FOLDER = json_data["main_computer_upload_folder"]
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_PATH"] = json_data["MAX_CONTENT_PATH"]
app.config["TIME_OUT"] = json_data["TIME_OUT"]


# TODO: remove prints and use logger - https://flask.palletsprojects.com/en/2.0.x/logging/
@app.route("/")
def index():
    """Starts the website"""
    return render_template("index.html")


# TODO: remove get
@app.route("/LoopStarter", methods=["POST"])
def loop_starter():
    """Sends the user to his destination, with the needed information"""
    if request.method == "POST":
        # TODO: dont use saved word id
        file_id = randint(
            json_data["id_random_range"][0], json_data["id_random_range"][1]
        )
        current_time = utils.get_current_time()
        # TODO: move the file name creation to utils class
        # TODO: read about context managers (with open ....)
        open(
            utils.generate_text_file_name(file_id, current_time), "a", encoding="utf-8"
        ).close()

        app.logger.info(
            "Each line in the info file is in the following order, seperated by a '*' : page number, amount of images, template name, text, path of each image"
        )

        # TODO: read about short if
        if request.form.get("Mixed"):
            template_name = json_data["3_images_mixed_html_template_name"]
        elif request.form.get("Vertical"):
            template_name = json_data["3_images_vertical_html_template_name"]

        return render_template(
            template_name,
            FileID=file_id,
            Time=current_time,
            PageNumber=1,
        )


@app.route("/LoopContinue", methods=["POST"])
def loop_continue():
    """Continues the loop or ending it, creating the pictures and the pdf"""
    if request.method == "POST":
        # Extracting all the info from the form, both the hidden and the shown
        title_text = request.form.get("TitleTextF")
        first_pic = request.files.get("FirstPic")
        second_pic = request.files.get("SecondPic")
        third_pic = request.files.get("ThirdPic")
        current_time = request.form.get("CurrentTime")
        file_id = request.form.get("FileID")
        template_type = request.form.get("TemplateType")
        page_number = request.form.get("PageNumber")

        is_new_mix_page = request.form.get("NewMix")
        is_new_vertical_page = request.form.get("NewVertical")

        if (
            "application/octet-stream" in str(first_pic)
            or "application/octet-stream" in str(second_pic)
            or "application/octet-stream" in str(third_pic)
        ):
            app.logger.info("Page number %s is missing at least one image", page_number)
        else:

            temp_info = ""

            # "Information" has the following data: page number,
            #  pic amount, html template, title text, the pictures

            temp_info = page_number
            temp_info = temp_info + "*" + str(template_type[0])
            temp_info = temp_info + "*" + str(template_type)
            temp_info = utils.get_fixed_title_text(temp_info, title_text)

            # Saving the first picure with the id
            # ,time and number and page number and saving in in the information array
            file_type = utils.get_file_type(secure_filename(first_pic.filename))
            temp_info = temp_info + utils.save_image(
                file_type, file_id, current_time, page_number, 1, first_pic, app
            )

            # Saving the second picure with the id,
            # time and number and page number and saving in in the information array

            file_type = utils.get_file_type(secure_filename(second_pic.filename))
            temp_info = temp_info + utils.save_image(
                file_type, file_id, current_time, page_number, 2, second_pic, app
            )

            # Saving the third picure with the id,
            # time and number and page number and saving in in the information array

            file_type = utils.get_file_type(secure_filename(third_pic.filename))
            temp_info = temp_info + utils.save_image(
                file_type, file_id, current_time, page_number, 3, third_pic, app
            )

            app.logger.info("Page %s information : %s", page_number, temp_info)

            with open(
                utils.generate_text_file_name(file_id, current_time),
                "a",
                encoding="utf-8",
            ) as text_file:
                text_file.write(temp_info + "\n")

            page_number = int(page_number)
            page_number += 1

        if is_new_mix_page or is_new_vertical_page:
            temp_template = (
                json_data["3_images_vertical_html_template_name"]
                if not is_new_mix_page
                else json_data["3_images_mixed_html_template_name"]
            )
            return render_template(
                temp_template,
                FileID=file_id,
                Time=current_time,
                PageNumber=page_number,
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

            final_images = []
            for part in information[-1]:
                page_amount = part
                break

           

            for part in information:
                html_template = utils.set_html_template(
                    part[4],
                    part[5],
                    part[6],
                    part[3],
                    part[0],
                    page_amount,
                    part[2],
                )
                image_file_name = utils.generate_page_image_file_name(
                    part[0], file_id, current_time, json_data["page_image_type"]
                )
                hti = Html2Image()
                hti.screenshot(
                    html_str=html_template,
                    save_as=image_file_name,
                    size=(
                        json_data["screenshot_size"][0],
                        json_data["screenshot_size"][1],
                    ),
                )
                final_images.append(image_file_name)
            app.logger.info("Page images paths : %s", final_images)

            pdf = FPDF()
            for image in final_images:
                pdf.add_page()
                pdf.image(
                    json_data["header_picture_path"],
                    w=json_data["header_picure_size"][0],
                    h=json_data["header_picure_size"][1],
                )
                pdf.image(
                    image,
                    w=json_data["pdf_body_size"][0],
                    h=json_data["pdf_body_size"][1],
                    type=json_data["page_image_type"],
                )
            pdf_file_name = utils.generate_pdf_file_name(file_id, current_time)
            pdf.output(pdf_file_name, "F")

            app.logger.info("Final pdf name : %s", pdf_file_name)

        return render_template("finish.html", pdf_name=pdf_file_name)


@app.route("/UploadFile", methods=["GET", "POST"])
def upload_file():
    """Sends the user the finished pdf"""
    file_name = request.form.get("filename")
    return send_file("../" + file_name, as_attachment=True)


if __name__ == "__main__":
    app.run(host="0.0.0.0")
