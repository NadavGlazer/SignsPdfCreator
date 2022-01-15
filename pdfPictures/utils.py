from datetime import datetime
import os
from re import match
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from fpdf import FPDF
import app
import time

def generate_text_file_name(file_id, current_time):
    """Returns file name, generated by given parameters and in a specific pattern"""
    return str(file_id) + "__" + str(current_time) + ".txt"


def get_fixed_title_text(temp_info, title_text):
    """Adding the fixed title text to the string and returning it"""
    return temp_info + "*" + str(title_text).replace("  ", " ").replace("*", "@").replace("$","@").replace("\r","").replace("\n","$").replace(" $","$")


def save_image(
    file_type, file_id, current_time, page_number, serial_number, picture, app
):
    """Gets the picuture and the needed parameters and saves it, returns the requird data"""
    file_name = generate_picture_file_name(
        file_type, file_id, current_time, page_number, serial_number
    ).replace(".", "_", 2)    
    picture.save(os.path.join(app.config["UPLOAD_FOLDER"], file_name))
    return "*" + app.config["UPLOAD_FOLDER"] + file_name


def get_file_type(file_name):
    """Gets file name and returns it`s type"""
    return file_name.split(".", 1)[1]


def generate_picture_file_name(
    file_type, file_id, current_time, page_number, serial_number
):
    """Returns file name, generated by given parameters and in a specific pattern"""
    return (
        page_number
        + "_"
        + str(serial_number)
        + "__"
        + file_id
        + "__"
        + current_time
        + "."
        + file_type
    )


def set_html_template_3_images(
    pic_one, pic_two, pic_three, text, page_num, page_amount, file_type
):
    """Returns html string, generated by given templates and parameters"""
    html_template_name = "templates/" + file_type + ".html"
    with open(html_template_name, "r", encoding="utf-8") as html_file:
        html_template = html_file.read()

    return (
        html_template.replace("pic_one", ("/" + pic_one))
        .replace("pic_two", ("/" + pic_two))
        .replace("pic_three", ("/" + pic_three))
        .replace("text_from_form", text)
        .replace("page_number", "עמוד " + str(page_num) + " מתוך " + str(page_amount))
        .replace("$", "\n")
    )

def set_html_template_4_images(
    pic_one, pic_two, pic_three, pic_four, text1, text2, page_num, page_amount, file_type
):
    """Returns html string, generated by given templates and parameters"""
    html_template_name = "pdfPictures/templates/" + file_type + ".html"
    with open(html_template_name, "r", encoding="utf-8") as html_file:
        html_template = html_file.read()

    return (
        html_template
        .replace("text_from_form1", text1)
        .replace("pic_one", ("/" + pic_one.split("/",3)[-1]))
        .replace("pic_two", ("/" + pic_two.split("/",3)[-1]))
        .replace("text_from_form2",text2)
        .replace("pic_three",("/" + pic_three.split("/",3)[-1]))
        .replace("pic_four",("/" + pic_four.split("/",3)[-1]))        
        .replace("page_number", "עמוד " + str(page_num) + " מתוך " + str(page_amount))
        .replace("$", "\n")
    )


def generate_page_image_file_name(page_number, file_id, current_time, file_type):
    """Returns image file name, generated by given parameters and in a specific pattern"""
    return page_number + "__" + file_id + "__" + current_time + "." + file_type


def generate_pdf_file_name(file_id, current_time):
    """Returns pdf file name, generated by given parameters and in a specific pattern"""
    return file_id + "__" + current_time + ".pdf"


def get_current_time():
    """Returns the current time in a specific pattern"""
    return datetime.now().strftime("%d_%m_%Y_%H_%M_%S")


def information_to_pdf(information, file_id, current_time, json_data, application):
    """Gets the current project information and creates the pdf, returns pdf file name"""
    #Creating the update file
    options = Options()
    options.headless = True

    options.add_argument("--window-size=1024,1200")
    options.add_argument("--hide-scrollbars")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    time.sleep(0.1)

    driver = webdriver.Chrome(executable_path="C:\\Users\\Nadav1\\Downloads\\chromedriver_win32\\chromedriver.exe", options=options)
    while not driver.service.is_connectable():
        driver = webdriver.Chrome(executable_path="C:\\Users\\Nadav1\\Downloads\\chromedriver_win32\\chromedriver.exe", options=options)
    driver.implicitly_wait(0.5)

    final_images = []
    page_amount = len(information)
    page_number = 1
    for part in information:
        html_template = ""
        if part[0] == "3":
            html_template = set_html_template_3_images(
                part[3],
                part[4],
                part[5],
                part[2],
                page_number,
                page_amount,
                part[1],
            )
        elif part[0] == "4":
            html_template = set_html_template_4_images(
                part[4],
                part[5],
                part[6],
                part[7],
                part[2],
                part[3],
                page_number,
                page_amount,
                part[1],
            )
        image_file_name = generate_page_image_file_name(
            str(page_number), file_id, current_time, json_data["page_image_type"]
        )
        temp_html_file_name = image_file_name[:-3] + "html"
        with open(
            "templates/" + temp_html_file_name,
             "w",
             encoding="utf-8",
        ) as temp_html_file:
            temp_html_file.write(html_template)
            
        
        with application.app_context():
            app.load_temp_html_file(html_file=temp_html_file_name)
        url = "http://192.168.0.117:"+ str(json_data["port"]) + "/TempHtmlFile/" + temp_html_file_name
        driver.get(url)

        write_in_update_text_file(file_id, current_time, "page "+ str(page_number) + " out of " + str(page_amount)+" is being converted to image")  
       
        driver.save_screenshot(image_file_name)

        final_images.append(image_file_name)
        page_number += 1
        
    driver.close()
    
    pdf = FPDF("P", "mm", "A4")
    image_counter = 1
    for image in final_images:

        write_in_update_text_file(file_id, current_time, "page "+ str(image_counter) + " out of " + str(page_amount)+ " is being converted to pdf")         

        pdf.add_page()
        pdf.image(
            json_data["header_picture_path"],
            w=json_data["header_picure_size"][0],
            h=json_data["header_picure_size"][1],
        )
        pdf.image(
            image,        
            x=json_data["pdf_body_x"],
            w=json_data["pdf_body_size"][0],
            h=json_data["pdf_body_size"][1],
            type=json_data["page_image_type"],
        )

        image_counter += 1
    write_in_update_text_file(file_id, current_time, "generating pdf..")  
   
    pdf_file_name = generate_pdf_file_name(file_id, current_time)
    pdf.output(pdf_file_name, "F")

    write_in_update_text_file(file_id, current_time, "Finished")   
    write_in_overall_information_file("Finished generating " + pdf_file_name)

    return pdf_file_name

def generate_update_text_file_name(file_id, current_time):
    """Returns file name, generated by given parameters and in a specific pattern"""
    return "update_" + str(file_id) + "__" + str(current_time) + ".txt"

def write_in_update_text_file(file_id, current_time, message):
    """Gets update file and msg and writes it in it"""
    with open(
        generate_update_text_file_name(file_id, current_time),
        "a",
        encoding="utf-8",
    ) as text_file:
        text_file.write(message + "\n")

def write_in_overall_information_file(message):
    """Gets the update and writes it in the information file"""
    with open(
        "Information.txt",
        "a",
        encoding="utf-8",
    ) as information_file:
        information_file.write(str(message) + "\n")


