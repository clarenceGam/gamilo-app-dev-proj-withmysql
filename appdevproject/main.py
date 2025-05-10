import sys
import os
import mysql.connector
from mysql.connector import errorcode
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QLabel,
    QPushButton, QListWidget, QMessageBox, QComboBox, QFileDialog, QListWidgetItem,
    QGroupBox, QSpacerItem, QSizePolicy
)
from PyQt5.QtGui import QPixmap, QIcon, QFont
from PyQt5.QtCore import Qt, QSize
from PIL import Image

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Owner Login")
        self.setGeometry(100, 100, 360, 220)
        self.setMinimumSize(360, 220)
        self.setMaximumSize(360, 220)
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 30, 40, 30)
        main_layout.setSpacing(15)
        title_label = QLabel("Car Manager Login")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title_label.setStyleSheet("color: #2E86C1; margin-bottom: 10px;")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.username_input.setFixedHeight(35)
        self.username_input.setFont(QFont("Segoe UI", 10))
        self.username_input.setStyleSheet(self.input_style())
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFixedHeight(35)
        self.password_input.setFont(QFont("Segoe UI", 10))
        self.password_input.setStyleSheet(self.input_style())
        self.login_btn = QPushButton("Log In")
        self.login_btn.setFixedHeight(40)
        self.login_btn.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.login_btn.setStyleSheet(self.button_style())
        self.login_btn.clicked.connect(self.check_login)
        main_layout.addWidget(title_label)
        main_layout.addWidget(self.username_input)
        main_layout.addWidget(self.password_input)
        main_layout.addWidget(self.login_btn)
        self.setLayout(main_layout)
        self.setStyleSheet("background-color: #f4f6f8;")

    def input_style(self):
        return """
            QLineEdit {
                border: 2px solid #ced4da;
                border-radius: 8px;
                padding-left: 12px;
                background-color: white;
                transition: border-color 0.3s ease;
            }
            QLineEdit:focus {
                border-color: #2E86C1;
            }
        """

    def button_style(self):
        return """
            QPushButton {
                background-color: #2E86C1;
                color: white;
                border-radius: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #21618C;
            }
            QPushButton:pressed {
                background-color: #1B4F72;
            }
        """

    def check_login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        if username == "admin" and password == "admin":
            self.accept_login()
        else:
            QMessageBox.critical(self, "Login Failed", "Invalid username or password.", QMessageBox.Ok, QMessageBox.Ok)

    def accept_login(self):
        self.hide()
        self.manager = CarManager(self)
        self.manager.show()

class CarManager(QWidget):
    def __init__(self, login_window):
        super().__init__()
        self.login_window = login_window
        self.setWindowTitle("Car Manager - Add Cars")
        self.setGeometry(100, 100, 500, 600)
        self.setMinimumSize(500, 600)

        config = {
            'user': 'root',
            'password': 'clarence03',
            'host': 'localhost',
            'database': 'car_manager_db',
            'raise_on_warnings': True
        }

        try:
            self.conn = mysql.connector.connect(**config)
            self.cursor = self.conn.cursor()
            self.create_tables()
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                QMessageBox.critical(self, "DB Error", "Invalid MySQL username or password.")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                QMessageBox.critical(self, "DB Error", "Database does not exist.")
            else:
                QMessageBox.critical(self, "DB Error", f"MySQL error: {err}")
            sys.exit(1)

        self.image_path_add = None

        self.init_ui()
        self.setStyleSheet("background-color: #f4f6f8; font-family: 'Segoe UI'; font-size: 12pt; color: #333;")

    def create_tables(self):
        create_table_query = """
        CREATE TABLE IF NOT EXISTS cars (
            id INT AUTO_INCREMENT PRIMARY KEY,
            make VARCHAR(100),
            model VARCHAR(100),
            year VARCHAR(10),
            plate VARCHAR(50) UNIQUE,
            status VARCHAR(50),
            image_path VARCHAR(255)
        )
        """
        self.cursor.execute(create_table_query)
        self.conn.commit()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        title = QLabel("Add New Car")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet("color: #2E86C1;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        self.make_input = QLineEdit()
        self.make_input.setPlaceholderText("Make")
        self.make_input.setFixedHeight(35)
        self.make_input.setStyleSheet(self.input_style())

        self.model_input = QLineEdit()
        self.model_input.setPlaceholderText("Model")
        self.model_input.setFixedHeight(35)
        self.model_input.setStyleSheet(self.input_style())

        self.year_input = QLineEdit()
        self.year_input.setPlaceholderText("Year")
        self.year_input.setFixedHeight(35)
        self.year_input.setStyleSheet(self.input_style())

        self.plate_input = QLineEdit()
        self.plate_input.setPlaceholderText("License Plate")
        self.plate_input.setFixedHeight(35)
        self.plate_input.setStyleSheet(self.input_style())

        self.status_input = QComboBox()
        self.status_input.addItems(["Available", "Rented", "Maintenance"])
        self.status_input.setFixedHeight(35)
        self.status_input.setStyleSheet(self.input_style())

        self.image_label_add = QLabel("No Image")
        self.image_label_add.setFixedSize(200, 200)
        self.image_label_add.setAlignment(Qt.AlignCenter)
        self.image_label_add.setStyleSheet(
            "border: 2px dashed #b0b0b0; border-radius: 10px; background-color: #fff; color: #999;"
        )

        btn_upload_add = QPushButton("Upload Image")
        btn_upload_add.setFixedHeight(40)
        btn_upload_add.setStyleSheet(self.button_style_primary())
        btn_upload_add.clicked.connect(self.upload_image_add)

        btn_add = QPushButton("Add Car")
        btn_add.setFixedHeight(45)
        btn_add.setStyleSheet(self.button_style_success())
        btn_add.setFont(QFont("Segoe UI", 12, QFont.Bold))
        btn_add.clicked.connect(self.add_car)

        btn_manage_cars = QPushButton("Manage Cars (View / Edit)")
        btn_manage_cars.setFixedHeight(45)
        btn_manage_cars.setStyleSheet(self.button_style_primary())
        btn_manage_cars.setFont(QFont("Segoe UI", 12, QFont.Bold))
        btn_manage_cars.clicked.connect(self.open_car_list_manager)

        widgets = [
            self.make_input, self.model_input, self.year_input, self.plate_input,
            self.status_input, self.image_label_add, btn_upload_add, btn_add, btn_manage_cars
        ]
        for w in widgets:
            layout.addWidget(w)

        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        self.setLayout(layout)

    def open_car_list_manager(self):
        self.car_list_manager = CarListManager(self.login_window, self)
        self.car_list_manager.show()
        self.hide()

    def input_style(self):
        return """
            QLineEdit, QComboBox {
                border: 1.8px solid #ccd0d5;
                border-radius: 8px;
                padding-left: 12px;
                background-color: white;
                font-size: 13px;
            }
            QLineEdit:focus, QComboBox:focus {
                border-color: #2E86C1;
                outline: none;
            }
        """

    def button_style_primary(self):
        return """
            QPushButton {
                background-color: #2E86C1;
                color: white;
                border-radius: 12px;
                font-weight: 700;
            }
            QPushButton:hover {
                background-color: #21618C;
            }
            QPushButton:pressed {
                background-color: #1B4F72;
            }
        """

    def button_style_success(self):
        return """
            QPushButton {
                background-color: #28a745;
                color: white;
                border-radius: 12px;
                font-weight: 700;
            }
            QPushButton:hover {
                background-color: #1e7e34;
            }
            QPushButton:pressed {
                background-color: #155d27;
            }
        """

    def upload_image_add(self):
        self.image_path_add = self.select_and_crop_image(self.image_label_add)

    def select_and_crop_image(self, label):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Car Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp)")
        if file_path:
            try:
                img = Image.open(file_path)
                width, height = img.size
                min_dim = min(width, height)
                left = (width - min_dim) // 2
                top = (height - min_dim) // 2
                img_cropped = img.crop((left, top, left + min_dim, top + min_dim))

                os.makedirs("cropped_images", exist_ok=True)
                base_name = os.path.splitext(os.path.basename(file_path))[0]
                ext = os.path.splitext(file_path)[1]
                cropped_path = os.path.join("cropped_images", f"{base_name}_cropped{ext}")
                img_cropped.save(cropped_path)

                pixmap = QPixmap(cropped_path)
                label.setPixmap(pixmap.scaled(label.width(), label.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
                return cropped_path
            except Exception as e:
                QMessageBox.critical(self, "Image Error", f"Could not process image:\n{str(e)}")
        return None

    def add_car(self):
        year_text = self.year_input.text().strip()
        plate_text = self.plate_input.text().strip()

        if not year_text.isdigit() or int(year_text) > 2025:
            QMessageBox.warning(self, "Invalid Year", "Year must be a number not greater than 2025.")
            return

        if self.is_plate_exists(plate_text):
            QMessageBox.warning(self, "Duplicate Plate", "A car with this license plate already exists.")
            return

        data = (
            self.make_input.text().strip(),
            self.model_input.text().strip(),
            year_text,
            plate_text,
            self.status_input.currentText(),
            self.image_path_add
        )
        if all(data[:5]):
            try:
                self.cursor.execute(
                    "INSERT INTO cars (make, model, year, plate, status, image_path) VALUES (%s, %s, %s, %s, %s, %s)",
                    data
                )
                self.conn.commit()
                QMessageBox.information(self, "Success", "Car added successfully!")
                self.clear_add_form()
            except mysql.connector.IntegrityError:
                QMessageBox.warning(self, "Duplicate Plate", "A car with this license plate already exists.")
        else:
            QMessageBox.warning(self, "Missing Data", "Please fill all fields.")

    def is_plate_exists(self, plate, exclude_id=None):
        if exclude_id:
            self.cursor.execute("SELECT id FROM cars WHERE plate = %s AND id != %s", (plate, exclude_id))
        else:
            self.cursor.execute("SELECT id FROM cars WHERE plate = %s", (plate,))
        return self.cursor.fetchone() is not None

    def clear_add_form(self):
        self.make_input.clear()
        self.model_input.clear()
        self.year_input.clear()
        self.plate_input.clear()
        self.status_input.setCurrentIndex(0)
        self.image_label_add.setText("No Image")
        self.image_label_add.clear()
        self.image_path_add = None

class CarListManager(QWidget):
    def __init__(self, login_window, parent_add_window):
        super().__init__()
        self.login_window = login_window
        self.parent_add_window = parent_add_window
        self.setWindowTitle("Manage Cars - View & Edit")
        self.setGeometry(120, 120, 900, 700)
        self.setMinimumSize(900, 700)

        self.conn = self.parent_add_window.conn
        self.cursor = self.conn.cursor()

        self.image_path_edit = None
        self.selected_car_id = None

        self.init_ui()
        self.load_data()

        self.setStyleSheet("background-color: #f4f6f8; font-family: 'Segoe UI'; font-size: 12pt; color: #333;")

    def init_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        list_box = QGroupBox("Car List")
        list_box.setStyleSheet(self.groupbox_style())
        list_layout = QVBoxLayout()
        self.car_list = QListWidget()
        self.car_list.setIconSize(QSize(160, 160))
        self.car_list.itemClicked.connect(self.load_selected)
        self.car_list.setStyleSheet("""
            QListWidget {
                background-color: white;
                border: 1.5px solid #d1d5da;
                border-radius: 8px;
                padding: 6px;
                outline: none;
            }
            QListWidget::item {
                padding: 8px;
                border-radius: 6px;
            }
            QListWidget::item:selected {
                background-color: #2E86C1;
                color: white;
            }
        """)
        list_layout.addWidget(self.car_list)
        list_box.setLayout(list_layout)
        layout.addWidget(list_box, 3)

        right_panel = QVBoxLayout()
        right_panel.setSpacing(20)

        edit_box = QGroupBox("Edit Selected Car")
        edit_box.setStyleSheet(self.groupbox_style())
        edit_layout = QVBoxLayout()

        self.make_edit = QLineEdit()
        self.make_edit.setPlaceholderText("Make")
        self.make_edit.setFixedHeight(32)
        self.make_edit.setStyleSheet(self.input_style())

        self.model_edit = QLineEdit()
        self.model_edit.setPlaceholderText("Model")
        self.model_edit.setFixedHeight(32)
        self.model_edit.setStyleSheet(self.input_style())

        self.year_edit = QLineEdit()
        self.year_edit.setPlaceholderText("Year")
        self.year_edit.setFixedHeight(32)
        self.year_edit.setStyleSheet(self.input_style())

        self.plate_edit = QLineEdit()
        self.plate_edit.setPlaceholderText("License Plate")
        self.plate_edit.setFixedHeight(32)
        self.plate_edit.setStyleSheet(self.input_style())

        self.status_edit = QComboBox()
        self.status_edit.addItems(["Available", "Rented", "Maintenance"])
        self.status_edit.setFixedHeight(32)
        self.status_edit.setStyleSheet(self.input_style())

        self.image_label_edit = QLabel("No Image")
        self.image_label_edit.setFixedSize(160, 160)
        self.image_label_edit.setAlignment(Qt.AlignCenter)
        self.image_label_edit.setStyleSheet("border: 2px dashed #b0b0b0; border-radius: 8px; background-color: #fff; color: #999;")

        btn_upload_edit = QPushButton("Upload Image")
        btn_upload_edit.setFixedHeight(36)
        btn_upload_edit.setStyleSheet(self.button_style_primary())
        btn_upload_edit.clicked.connect(self.upload_image_edit)

        btn_update = QPushButton("Update Car")
        btn_update.setFixedHeight(40)
        btn_update.setStyleSheet(self.button_style_success())
        btn_update.setFont(QFont("Segoe UI", 11, QFont.Bold))
        btn_update.clicked.connect(self.update_car)

        btn_delete = QPushButton("Delete Car")
        btn_delete.setFixedHeight(40)
        btn_delete.setStyleSheet(self.button_style_danger())
        btn_delete.setFont(QFont("Segoe UI", 11, QFont.Bold))
        btn_delete.clicked.connect(self.delete_car)

        btn_back = QPushButton("Back to Add New Car")
        btn_back.setFixedHeight(35)
        btn_back.setStyleSheet(self.button_style_secondary())
        btn_back.setFont(QFont("Segoe UI", 10, QFont.Bold))
        btn_back.clicked.connect(self.go_back)

        widgets = [self.make_edit, self.model_edit, self.year_edit, self.plate_edit,
                   self.status_edit, self.image_label_edit, btn_upload_edit,
                   btn_update, btn_delete, btn_back]

        for w in widgets:
            edit_layout.addWidget(w)

        edit_box.setLayout(edit_layout)
        right_panel.addWidget(edit_box, 1)

        right_panel.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        logout_btn = QPushButton("Logout")
        logout_btn.setFixedHeight(35)
        logout_btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
        logout_btn.setStyleSheet(self.button_style_logout_red())
        logout_btn.clicked.connect(self.logout)

        logout_layout = QHBoxLayout()
        logout_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        logout_layout.addWidget(logout_btn)

        right_panel.addLayout(logout_layout)

        layout.addLayout(right_panel, 2)

        self.setLayout(layout)

    def go_back(self):
        self.close()
        self.parent_add_window.show()

    def logout(self):
        self.close()
        self.parent_add_window.close()
        self.login_window.show()

    def input_style(self):
        return """
            QLineEdit, QComboBox {
                border: 1.8px solid #ccd0d5;
                border-radius: 8px;
                padding-left: 12px;
                background-color: white;
                font-size: 13px;
            }
            QLineEdit:focus, QComboBox:focus {
                border-color: #2E86C1;
                outline: none;
            }
        """

    def groupbox_style(self):
        return """
            QGroupBox {
                font-weight: 600;
                font-size: 14px;
                border: 1.5px solid #d1d5da;
                border-radius: 10px;
                margin-top: 15px;
                padding: 15px;
                background-color: #fff;
            }
            QGroupBox:title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 10px;
                color: #2E86C1;
            }
        """

    def button_style_primary(self):
        return """
            QPushButton {
                background-color: #2E86C1;
                color: white;
                border-radius: 12px;
                font-weight: 700;
            }
            QPushButton:hover {
                background-color: #21618C;
            }
            QPushButton:pressed {
                background-color: #1B4F72;
            }
        """

    def button_style_success(self):
        return """
            QPushButton {
                background-color: #28a745;
                color: white;
                border-radius: 12px;
                font-weight: 700;
            }
            QPushButton:hover {
                background-color: #1e7e34;
            }
            QPushButton:pressed {
                background-color: #155d27;
            }
        """

    def button_style_danger(self):
        return """
            QPushButton {
                background-color: #dc3545;
                color: white;
                border-radius: 12px;
                font-weight: 700;
            }
            QPushButton:hover {
                background-color: #bd2130;
            }
            QPushButton:pressed {
                background-color: #801427;
            }
        """

    def button_style_secondary(self):
        return """
            QPushButton {
                background-color: #6c757d;
                color: white;
                border-radius: 12px;
                font-weight: 700;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
            QPushButton:pressed {
                background-color: #545b62;
            }
        """

    def button_style_logout_red(self):
        return """
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: 600;
                padding: 7px 18px;
                max-width: 110px;
                transition: background-color 0.3s ease;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
            QPushButton:pressed {
                background-color: #bd2130;
            }
        """

    def upload_image_edit(self):
        self.image_path_edit = self.select_and_crop_image(self.image_label_edit)

    def select_and_crop_image(self, label):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Car Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp)")
        if file_path:
            try:
                img = Image.open(file_path)
                width, height = img.size
                min_dim = min(width, height)
                left = (width - min_dim) // 2
                top = (height - min_dim) // 2
                img_cropped = img.crop((left, top, left + min_dim, top + min_dim))
                os.makedirs("cropped_images", exist_ok=True)
                base_name = os.path.splitext(os.path.basename(file_path))[0]
                ext = os.path.splitext(file_path)[1]
                cropped_path = os.path.join("cropped_images", f"{base_name}_cropped{ext}")
                img_cropped.save(cropped_path)
                pixmap = QPixmap(cropped_path)
                label.setPixmap(pixmap.scaled(label.width(), label.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
                return cropped_path
            except Exception as e:
                QMessageBox.critical(self, "Image Error", f"Could not process image:\n{str(e)}")
        return None

    def load_data(self):
        self.car_list.clear()
        self.cursor.execute("SELECT * FROM cars ORDER BY id DESC")
        cars = self.cursor.fetchall()
        for car in cars:
            car_id, make, model, year, plate, status, image_path = car
            item_text = f"{make} {model} ({year}) - {plate} [{status}]"
            item = QListWidgetItem(item_text)
            if image_path and os.path.exists(image_path):
                item.setIcon(QIcon(image_path))
            else:
                item.setIcon(QIcon())
            item.setData(Qt.UserRole, car_id)
            self.car_list.addItem(item)

    def load_selected(self, item):
        car_id = item.data(Qt.UserRole)
        self.cursor.execute("SELECT * FROM cars WHERE id = %s", (car_id,))
        car = self.cursor.fetchone()
        if car:
            self.make_edit.setText(car[1])
            self.model_edit.setText(car[2])
            self.year_edit.setText(car[3])
            self.plate_edit.setText(car[4])
            self.status_edit.setCurrentText(car[5])
            self.image_path_edit = car[6]
            if car[6] and os.path.exists(car[6]):
                pixmap = QPixmap(car[6])
                self.image_label_edit.setPixmap(pixmap.scaled(self.image_label_edit.width(), self.image_label_edit.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
            else:
                self.image_label_edit.setText("No Image")
                self.image_label_edit.setPixmap(QPixmap())
            self.selected_car_id = car[0]

    def update_car(self):
        if self.selected_car_id is not None:
            year_text = self.year_edit.text().strip()
            plate_text = self.plate_edit.text().strip()
            if not year_text.isdigit() or int(year_text) > 2025:
                QMessageBox.warning(self, "Invalid Year", "Year must be a number not greater than 2025.")
                return
            if self.is_plate_exists(plate_text, exclude_id=self.selected_car_id):
                QMessageBox.warning(self, "Duplicate Plate", "A car with this license plate already exists.")
                return
            data = (
                self.make_edit.text().strip(),
                self.model_edit.text().strip(),
                year_text,
                plate_text,
                self.status_edit.currentText(),
                self.image_path_edit,
                self.selected_car_id
            )
            if all(data[:6]):
                self.cursor.execute(
                    "UPDATE cars SET make=%s, model=%s, year=%s, plate=%s, status=%s, image_path=%s WHERE id=%s",
                    data
                )
                self.conn.commit()
                self.load_data()
                self.clear_edit_form()
                self.selected_car_id = None
                QMessageBox.information(self, "Success", "Car updated successfully!")
            else:
                QMessageBox.warning(self, "Missing Data", "Please fill all fields.")
        else:
            QMessageBox.warning(self, "Selection Required", "Please select a car to update.")

    def is_plate_exists(self, plate, exclude_id=None):
        if exclude_id:
            self.cursor.execute("SELECT id FROM cars WHERE plate = %s AND id != %s", (plate, exclude_id))
        else:
            self.cursor.execute("SELECT id FROM cars WHERE plate = %s", (plate,))
        return self.cursor.fetchone() is not None

    def delete_car(self):
        if self.selected_car_id is not None:
            confirm = QMessageBox.question(self, "Confirm Delete",
                                           "Are you sure you want to delete the selected car?",
                                           QMessageBox.Yes | QMessageBox.No)
            if confirm == QMessageBox.Yes:
                self.cursor.execute("DELETE FROM cars WHERE id = %s", (self.selected_car_id,))
                self.conn.commit()
                self.load_data()
                self.clear_edit_form()
                self.selected_car_id = None
                QMessageBox.information(self, "Deleted", "Car deleted successfully!")
        else:
            QMessageBox.warning(self, "Selection Required", "Please select a car to delete.")

    def clear_edit_form(self):
        self.make_edit.clear()
        self.model_edit.clear()
        self.year_edit.clear()
        self.plate_edit.clear()
        self.status_edit.setCurrentIndex(0)
        self.image_label_edit.setText("No Image")
        self.image_label_edit.clear()
        self.image_path_edit = None

if __name__ == "__main__":
    app = QApplication(sys.argv)
    login = LoginWindow()
    login.show()
    sys.exit(app.exec_())
