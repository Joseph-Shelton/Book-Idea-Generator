import sys
import openai
import re
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QComboBox, QLineEdit, QPushButton, QTextEdit, QInputDialog, QMessageBox
from PyQt5.QtCore import QSize
from genres import genres

openai.api_key = "your-api-key"

book_name = ""
synopsis = ""


class CustomInputDialog(QInputDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def sizeHint(self):
        return QSize(1000, 400)


class BookIdeaGenerator(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Book Idea Generator')

        self.layout = QVBoxLayout()

        self.genre1_label = QLabel('Genre 1:')
        self.genre1_dropdown = QComboBox()
        self.genre1_dropdown.addItems(genres)
        

        self.genre2_label = QLabel('Genre 2:')
        self.genre2_dropdown = QComboBox()
        self.genre2_dropdown.addItems(genres)


        self.info_label = QLabel('Relevant Info:')
        self.info_input = QTextEdit()
        self.info_input.setFixedHeight(90)

        self.generate_button = QPushButton('Generate Book Idea')
        self.generate_button.clicked.connect(self.generate_idea)


        self.develop_world_button = QPushButton('Develop World', self)
        self.develop_world_button.clicked.connect(self.develop_world)

        self.develop_characters_button = QPushButton('Develop Characters', self)
        self.develop_characters_button.clicked.connect(self.develop_characters)

        self.develop_systems_button = QPushButton('Develop Systems', self)
        self.develop_systems_button.clicked.connect(self.develop_systems)
        

        self.output = QTextEdit()
        self.output.setReadOnly(True)

        self.layout.addWidget(self.genre1_label)
        self.layout.addWidget(self.genre1_dropdown)
        self.layout.addWidget(self.genre2_label)
        self.layout.addWidget(self.genre2_dropdown)
        self.layout.addWidget(self.info_label)
        self.layout.addWidget(self.info_input)
        self.layout.addWidget(self.generate_button)
        self.layout.addWidget(self.output)
        self.layout.addWidget(self.develop_world_button)
        self.layout.addWidget(self.develop_characters_button)
        self.layout.addWidget(self.develop_systems_button)

        self.setLayout(self.layout)




    def generate_idea(self):
        genre1 = self.genre1_dropdown.currentText()
        genre2 = self.genre2_dropdown.currentText()
        info = self.info_input.toPlainText()


        messages = [
            {"role": "system", "content": "You are a helpful assistant that generates book ideas."},
            {"role": "user", "content": f"Generate a book title combining {genre1} and {genre2} with the following details: {info}. Please format it as 'Title:(put title name here)''"},
        ]

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature = 1,
        )


        assistant_reply = response['choices'][0]['message']['content']
        book_title = re.search(r'Title:\s*(.*)', assistant_reply).group(1)

        input_dialog = CustomInputDialog(self)
        input_dialog.setWindowTitle("Confirm Book Title")
        input_dialog.setLabelText("Book Title:")
        input_dialog.setTextValue(book_title)
        ok_pressed = input_dialog.exec_()
        confirmed_title = input_dialog.textValue()

        if ok_pressed:
            
            messages = [
                {"role": "system", "content": "You are a helpful assistant that generates detailed book plots."},
                {"role": "user", "content": f"Generate a detailed plot for a book titled '{confirmed_title}' combining {genre1} and {genre2} with the following details: {info}. Please make the first line only be the title. Please make the plot extremely detailed covering all parts of the book."},
            ]

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature = 1,
            )

            self.process_gpt_response(response)

    def show_warning(self, message):
        warning_box = QMessageBox()
        warning_box.setIcon(QMessageBox.Warning)
        warning_box.setWindowTitle("Warning")
        warning_box.setText(message)
        warning_box.exec_()



    def process_gpt_response(self, response):

        assistant_reply = response['choices'][0]['message']['content']

        global book_name
        global synopsis
        lines = assistant_reply.strip().split('\n')
        book_name = lines.pop(0).replace("Title: ", "")
        synopsis = ' '.join(lines).strip()

        messages = [
            {"role": "system", "content": "You are a helpful assistant that generates back cover summaries for books."},
            {"role": "user", "content": f"Generate a back cover summary for a book named '{book_name}' with the following synopsis: {synopsis}. Please do not include any major plot spoilers"},
        ]

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature = 1,
        )

        back_cover_summary = response['choices'][0]['message']['content']

        self.output.setHtml(f"<b>Book Name:</b> {book_name}<br><br><b>Synopsis:</b> {synopsis}<br><br><b>Back Cover Summary:</b> {back_cover_summary}")



    def develop_world(self):
        global book_name
        global synopsis

        if book_name == "" or synopsis == "":
            self.show_warning("Please generate a book idea first.")
            return

        messages = [
            {"role": "system", "content": "You are a helpful assistant that develops the world of a book."},
            {"role": "user", "content": f"I want you to help build out the world of {book_name}. Please do not focus on the characters, but really build out an image of what the world is like. Tell us if there is any other cities or nations we need to keep in mind. Tell us what the weather is like. Tell us about the geography of the world. Etc. You can use this synopsis as reference: {synopsis}"},
        ]

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature = 1,
        )

        world_development = response['choices'][0]['message']['content']
        self.output.append(f"<br><br><br><br><b>World Development:</b><br>{world_development}")

    def develop_characters(self):
        global book_name
        global synopsis

        if book_name == "" or synopsis == "":
            self.show_warning("Please generate a book idea first.")
            return

        messages = [
            {"role": "system", "content": "You are a helpful assistant that develops out the characters of a book."},
            {"role": "user", "content": f"I want you to help build out the characters of {book_name}. One by one, go into detail of all the individual characters. I want you to provide an extensive background into who they are and what they do. If you would please seperate each character into a different paragraph for easier reading. You can use this synopsis as reference: {synopsis}"},
        ]

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature = 1,
        )

        character_development = response['choices'][0]['message']['content']
        self.output.append("<br><br><br><br><b>Character Development:</b><br>{}".format(character_development.replace('\n', '<br>')))

    def develop_systems(self):
        global book_name
        global synopsis

        if book_name == "" or synopsis == "":
            self.show_warning("Please generate a book idea first.")
            return

        messages = [
            {"role": "system", "content": "You are a helpful assistant that develops out the characters of a book."},
            {"role": "user", "content": f"I want you to help build out the systems of {book_name}. One by one, go into detail of all the individual systems. These systems may be magic, they may be technological, or they may be political. I want you to go into great detail of these systems, for example, if it is magic I want you to tell what kind of magic and how different people weild such magic. You need to be content aware and only build on systems that work within the world of the book. You can use this synopsis as reference: {synopsis}"},
        ]

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature = 1,
        )

        system_development = response['choices'][0]['message']['content']
        self.output.append("<br><br><br><br><b>Systems Development:</b><br>{}".format(system_development.replace('\n', '<br>')))



def load_stylesheet():
    with open("stylesheet.qss", "r") as f:
        return f.read()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    app.setStyleSheet(load_stylesheet())

    book_idea_generator = BookIdeaGenerator()
    book_idea_generator.showMaximized()

    sys.exit(app.exec_())

