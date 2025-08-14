
import sys, os, threading, cv2, pymysql, traceback
from PyQt5.QtWidgets import (QApplication, QLabel, QPushButton, QVBoxLayout, QWidget, 
                             QMainWindow, QTableWidgetItem, QFrame, QGroupBox,QHBoxLayout, QStyleOptionTabWidgetFrame,
                             QListWidget, QSpacerItem, QSizePolicy, QMessageBox, QHeaderView, QTableWidget)
from PyQt5.QtGui import QImage, QPixmap, QPainter, QColor, QFont, QGuiApplication, QIcon
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt5 import uic, QtWidgets, QtCore
from ultralytics import YOLO
from datetime import datetime
from app.database import DatabaseConnection                     # type: ignore
from app.database import DatabaseFunction                       # type: ignore
from app.gui import run_login_window                            # type: ignore
from app.gui import DashboardWidget                             # type: ignore
from app.gui import userHistorydWidget                          # type: ignore
from app import MODEL_PATH, UI_PATH, RESOURCES_PATH             # type: ignore                                                                                 

class MyApp(QMainWindow):
    def __init__(self, pro_id):
        super().__init__()
    
        # Load Model
        self.model = YOLO(MODEL_PATH)

        # Load UI dynamically
        uic.loadUi(os.path.join(UI_PATH, "main.ui"), self)  
        self.showFullScreen()

        # Database connection
        self.db_connection = DatabaseConnection(use_local=True)
        self.db_function = DatabaseFunction()

        # Load test widget and extract 'dashboard'
        component = DashboardWidget()
        self.dashboard = component.dashboard
        self.saved_record = component.saved_record
        self.live_detection_btn = component.live_detection_btn
        self.user_name_label = component.user_name_label
        self.logout = component.logout

        userHistoryComponent = userHistorydWidget()
        self.saved_records = userHistoryComponent.saved_records
        self.operation_tab = userHistoryComponent.operation_tab
        self.operation_content = userHistoryComponent.operation_content

        self.saved_records.hide()


        self.layout = self.centralwidget.layout()
        self.layout.insertWidget(1, self.dashboard)
        self.layout.insertWidget(3, self.saved_records)

        self.dashboard.hide()
        self.mini_dashboard.show()

        # Enable mouse tracking
        self.setMouseTracking(True)
        self.mini_dashboard.setMouseTracking(True)
        self.dashboard.setMouseTracking(True)

        self.hover_enabled = True
        
        self.mini_dashboard.installEventFilter(self)
        self.dashboard.installEventFilter(self)


        ######Current user/admin#####
        s_name, f_name = self.db_function.get_fullname(pro_id)
        fullnaame = f"{s_name}, {f_name}"
        self.formatted_name = ', '.join(part.strip().capitalize() for part in fullnaame.split(','))
        self.user_name_label.setText(str(self.formatted_name))       

        now = datetime.now() # Get current date and time
        self.formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")# Format it as "YYYY-MM-DD HH:MM:SS"

        self.pro_id = pro_id


        #self.output_dir = f"{self.BASE_DIR}/saved-image"
        #os.makedirs(self.output_dir, exist_ok=True)

        self.wpcb_detection.horizontalHeader().setVisible(True)

        self.components = ['Ball Grid Array (BGA)', 
                        'Dual In-Line Package (DIP)', 
                        'Inductor', 
                        'Quad Flat Package (QFP)',
                        'Radial Electrolytic Capacitor (REC)', 
                        'SMD Electrolytic Capacitor (SMD EC)', 
                        'Small Outline Package (SOP)']
        row_count = len(self.components)  # Use the length of the components list


        self.hide_btn.setIcon(QIcon("icon/chevrons-right.svg"))
        self.hide_btn.setIconSize(QSize(20, 15))
    
        self.mini_icon.setPixmap(QPixmap("icon/logo4.png"))
        self.logout_btn.setIcon(QIcon("icon/log-out.svg"))
        self.live_detection_min.setIcon(QIcon("icon/camera.svg"))
        self.saved_detection_min.setIcon(QIcon("icon/bookmark.svg"))
        self.settings_min.setIcon(QIcon("icon/settings.svg"))


        self.hide_btn.clicked.connect(self.hide_dashboard_func)
    
        self.saved_record.clicked.connect(self.dashboard_btn_saved_record)
        self.saved_detection_min.clicked.connect(self.dashboard_btn_saved_record)
        self.live_detection_btn.clicked.connect(self.dashboard_btn_live_detection)
        self.live_detection_min.clicked.connect(self.dashboard_btn_live_detection)

        for row, component_name in enumerate(self.components):
            item_name = QTableWidgetItem(str(component_name))
            item_name.setTextAlignment(Qt.AlignCenter)
            self.component_detection.setItem(row, 0, item_name)

            item_value = QTableWidgetItem('0')
            item_value.setTextAlignment(Qt.AlignCenter)
            self.component_detection.setItem(row, 1, item_value)

        self.component_detection.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.component_detection.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)

        self.wpcb_detection.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.wpcb_detection.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)


        #Combo Box
        self.filter_class.addItems([
            "Default: All classes", 
            "Class 1: BGA", 
            "Class 2: DIP", 
            "Class 3: Inductor", 
            "Class 4: QFP", 
            "Class 5: REC", 
            "Class 6: SMD EC", 
            "Class 7: SOP", 
        ])
        
        #Indicator label set to hide
        self.detection_status.setText("")
        
    
        #Start detection button connection
        self.start_detection.clicked.connect(self.starting_detection)

        #Logout button connection
        self.logout.clicked.connect(self.handle_exit)
        self.logout_btn.clicked.connect(self.handle_exit)

        # Connect list widget to stacked widget
        self.operation_tab.currentRowChanged.connect(self.operation_content.setCurrentIndex)

        #####Variable#####
        self.model = YOLO(MODEL_PATH)
        self.pcb_data = []
        self.pcb_id = 0
        self.thread = None
        self.state = 0
        self.dashboard_state = 0
        self.running = False
        self.frame_count = 0
        self.skip_frames = 15
        self.last_results = None
        self.cap = None
        self.loop = 0
        self.detected_components = None

        self.filter_currentIndex = 0
        self.operation_id = None
        self.wpcb_id = None
        self.wpcb_id_per_operation = None

        self.total_price_list = []

    def eventFilter(self, source, event):
        if not self.hover_enabled:
            # If hover disabled, do nothing special
            return super().eventFilter(source, event)
        
        if source == self.mini_dashboard:
            if event.type() == event.Enter:
                self.mini_dashboard.hide()
                self.dashboard.show()
        elif source == self.dashboard:
            if event.type() == event.Leave:
                self.dashboard.hide()
                self.mini_dashboard.show()
        return super().eventFilter(source, event)


    def dashboard_btn_live_detection(self):
        self.saved_records.hide()
        self.live_detection.show()

    def dashboard_btn_saved_record(self):
        self.live_detection.hide()
        self.saved_records.show()

    def handle_exit(self):
        self.running = False
        if self.cap:
            self.cap.release()
        self.close()
        

    def hide_dashboard_func(self):
        if self.dashboard_state % 2 == 0:
            self.hover_enabled = False
            self.mini_dashboard.hide()
            self.dashboard.show()
            self.hide_btn.setIcon(QIcon("icon/chevrons-left.svg"))
            self.hide_btn.setIconSize(QSize(20, 15))
   
        else:
            self.hover_enabled = True
            self.dashboard.hide()
            self.mini_dashboard.show()
            self.hide_btn.setIcon(QIcon("icon/chevrons-right.svg"))
            self.hide_btn.setIconSize(QSize(20, 15))
     
        self.dashboard_state = (self.dashboard_state + 1) % 2

        

        

    #First Tab ----------------------------------------------
    def update_detected_component_table(self,wpcb_id):
        data = self.db_function.get_detected_components(wpcb_id)
        if data is None:
            return  # No data to update

        self.component_detection.setRowCount(len(self.components))

        for row, (component_name, detected_count) in enumerate(zip(self.components, data)):
            item_name = QTableWidgetItem(str(component_name))
            item_name.setTextAlignment(Qt.AlignCenter)
            self.component_detection.setItem(row, 0, item_name)

            item_value = QTableWidgetItem(str(detected_count))
            item_value.setTextAlignment(Qt.AlignCenter)
            self.component_detection.setItem(row, 1, item_value)

        self.component_detection.viewport().update()

    def update_detected_wpcb_table(self, operation_id):
        """Update the QTableWidget with all detected WPCB data based on operation_id."""
        data = self.db_function.get_detected_wpcb(operation_id)
        if data is None:
            return  # No data to update

        # Define the components for the table
        components = ['Waste PCB', 'Total']

        # Set the row count to match the number of results
        self.wpcb_detection.setRowCount(0)

        # Iterate through all rows and set column 2 (index 1) to 0
        for row, (wcpb_id, total_class) in enumerate(data):
            self.wpcb_detection.insertRow(row)

            item_name = QTableWidgetItem(str(wcpb_id))
            item_name.setTextAlignment(Qt.AlignCenter)
            self.wpcb_detection.setItem(row, 0, item_name)

            item_value = QTableWidgetItem(str(total_class))
            item_value.setTextAlignment(Qt.AlignCenter)
            self.wpcb_detection.setItem(row, 1, item_value)



        # Optional: Refresh the table to reflect changes
        self.wpcb_detection.viewport().update()

        recent_key = data[-1][0]
        return recent_key

    #Second Tab -------------------------------------------
    def update_metal_content_table(self, operation_id):
            connection = self.db_connection.connect_to_db()

            if connection:
                try:
                    cursor = connection.cursor()

                    # Fetch only the data we want
                    sql = """
                        SELECT 
                            wpcb_id_per_operation, class_id, category, width, length,
                            gold, silver, copper, aluminum, `lead`,
                            nickel, tin, zinc, platinum, palladium, chromium, iron
                        FROM record_info
                        WHERE operation_id = %s;
                        
                    """
                    cursor.execute(sql, (operation_id,))
                    data = cursor.fetchall()

                    if not data:
                        return  # No data to update

                    self.metal_content_table.setRowCount(0)

                    for row_idx, row_data in enumerate(data):
                        self.metal_content_table.insertRow(row_idx)
                        for col_idx, value in enumerate(row_data):
                            item_name = QTableWidgetItem(str(value))
                            item_name.setTextAlignment(Qt.AlignCenter)
                            self.metal_content_table.setItem(row_idx, col_idx, item_name)

                    self.metal_content_table.viewport().update()

                except pymysql.MySQLError as e:
                    print(f"Database query error: {e}")

                finally:
                    cursor.close()
                    connection.close()
            else:
                print("Failed to connect to the database.")

    #Third Tab -------------------------------------------

    def update_price_estimation_content_table(self, operation_id):
            connection = self.db_connection.connect_to_db()

            if connection:
                try:
                    cursor = connection.cursor()

                    # Fetch only the data we want
                    sql = """
                        SELECT 
                            wpcb_id_per_operation, metals, weight, price
                        FROM total_price_value
                        WHERE operation_id = %s;
                        
                    """
                    cursor.execute(sql, (operation_id,))
                    data = cursor.fetchall()

                    if not data:
                        return  # No data to update

                    self.price_estimation_table.setRowCount(0)

                    for row_idx, row_data in enumerate(data):
                        self.price_estimation_table.insertRow(row_idx)     
                        for col_idx, value in enumerate(row_data):
                            item_name = QTableWidgetItem(str(value))
                            item_name.setTextAlignment(Qt.AlignCenter)
                            self.price_estimation_table.setItem(row_idx, col_idx, item_name)


                    self.price_estimation_table.viewport().update()

                except pymysql.MySQLError as e:
                    print(f"Database query error: {e}")

                finally:
                    cursor.close()
                    connection.close()
            else:
                print("Failed to connect to the database.")

    def update_price_estimation_total_price_table(self, operation_id):
            connection = self.db_connection.connect_to_db()

            if connection:
                try:
                    cursor = connection.cursor()

                    # Fetch only the data we want
                    sql = """
                        SELECT 
                            operation_id, total
                        FROM total_price
                        WHERE operation_id = %s;
                        
                    """
                    cursor.execute(sql, (operation_id,))
                    data = cursor.fetchall()

                    if not data:
                        return  # No data to update

                    self.price_total_table.setRowCount(0)

                    for row_idx, row_data in enumerate(data):
                        self.price_total_table.insertRow(row_idx)
                        for col_idx, value in enumerate(row_data):
                            item_name = QTableWidgetItem(str(value))
                            item_name.setTextAlignment(Qt.AlignCenter)
                            self.price_total_table.setItem(row_idx, col_idx, item_name)

                    self.price_total_table.viewport().update()

                    print("from inside update table function")

                except pymysql.MySQLError as e:
                    print(f"Database query error: {e}")

                finally:
                    cursor.close()
                    connection.close()
            else:
                print("Failed to connect to the database.")

 
    def starting_detection(self):
        """Starts the camera feed and YOLO detection in a separate thread."""
        
        if self.state % 2 == 0:  # Start
            if not self.running:
                #Status of detection
                self.running = True

                #Updating the button start detection
                self.start_detection.setText("STOP DETECTION") 
                self.start_detection.setStyleSheet("""
                                                QPushButton {
                                                    background-color: rgb(255, 26, 26);
                                                    color: rgb(255, 255, 255);
                                                    border-radius: 20px;
                                                }

                                                QPushButton:hover {
                                                    background-color: rgb(170, 0, 0);
                                                }""")  
                
                #Disabling the button of filter class
                self.filter_class.setEnabled(False)
                currentText = self.filter_class.currentText()
                self.status.addItem(f"Filter is currently set to '{currentText}'")
                

                #Fetching current text and index from combo box
                filter_class = self.filter_class.currentIndex()
                self.status.addItem(f"Index is currently set to '{filter_class}'")
                self.filter_currentIndex = int(filter_class) - 1  

                #Call the function of run detection on thread
                self.thread = threading.Thread(target=self.run_detection, args=(self.filter_currentIndex,), daemon=True)
                self.thread.start()

                
                self.operation_id = self.db_function.input_start_operation_data(self.pro_id, self.formatted_name, self.formatted_time)

                return self.operation_id

                
        else:  # Stop
            self.start_detection.setText("START DETECTION")  # Change button text
            self.start_detection.setStyleSheet("""
                                            QPushButton {
                                                background-color: rgb(0, 170, 127);
                                                color: rgb(255, 255, 255);
                                                border-radius: 20px;
                                            }

                                            QPushButton:hover {
                                                background-color: rgb(0, 150, 110); /* Darker green on hover */
                                            }""")  
            self.status.addItem("Detection stopped.")
            self.filter_class.setEnabled(True)
            self.detection_status.setText("")
            
            self.db_function.input_stop_operation_data(self.operation_id)

            self.total_price_list.clear()
            self.loop = 0

            self.running = False  # Signal the thread to stop   
            if self.thread and self.thread.is_alive():
                self.thread.join()  # Wait for the thread to exit
            self.thread = None  # Clean up thread reference

            #self.camera.setScaledContents(False)
            self.camera.setPixmap(QPixmap())  # Clear the last frame
            self.camera.setPixmap(QPixmap("icon/video-off.svg"))
            self.camera.setStyleSheet("")

            row_count = len(self.components)  # Use the length of the components list

            # Iterate through all rows and set column 2 (index 1) to 0
            for row, component_name in enumerate(self.components):
                item_name = QTableWidgetItem(str(component_name))
                item_name.setTextAlignment(Qt.AlignCenter)
                self.component_detection.setItem(row, 0, item_name)

                item_value = QTableWidgetItem('0')
                item_value.setTextAlignment(Qt.AlignCenter)
                self.component_detection.setItem(row, 1, item_value)
            
            self.component_detection.viewport().update()

            #Clear row at tab 1 component 2 table.
            for row in range(self.wpcb_detection.rowCount() - 1, -1, -1):
                self.wpcb_detection.removeRow(row)
            self.wpcb_detection.viewport().update()

            #Clear row at tab 2 table.
            for row in range(self.metal_content_table.rowCount() - 1, -1, -1):
                self.metal_content_table.removeRow(row)
            self.metal_content_table.viewport().update()

            #Clear row at tab 3 table 1.
            for row in range(self.price_estimation_table.rowCount() - 1, -1, -1):
                self.price_estimation_table.removeRow(row)
            self.price_estimation_table.viewport().update()

            #Clear row at tab 3 table 2.
            for row in range(self.price_total_table.rowCount() - 1, -1, -1):
                self.price_total_table.removeRow(row)
            self.price_total_table.viewport().update()

        self.state = (self.state + 1) % 2  # Toggle state


    def run_detection(self, selected_class_index):
        """Runs YOLOv8 detection on the camera feed and filters by a selected class (if any)."""
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.status.addItem("Detection is now running...")

        # Mapping from class ID to readable names
        class_id_to_name = {
            0: "BGA",
            1: "DIP",
            2: "Inductor",
            3: "QFP",
            4: "REC",
            5: "SMD EC",
            6: "SOP"
        }

        # Color for each class
        class_colors = {
            0: (255, 0, 0),      # Red
            1: (0, 255, 0),      # Green
            2: (0, 0, 255),      # Blue
            3: (255, 255, 0),    # Cyan
            4: (255, 0, 255),    # Magenta
            5: (0, 255, 255),    # Yellow
            6: (255, 255, 255),  # White
        }

        # Class-specific confidence thresholds
        class_thresholds = {
            "SOP": 0.2,
            "SMD EC": 0.3,
            "QFP": 0.2,
            "DIP": 0.1,
            "REC": 0.6,
            "Inductor": 0.2,
            "BGA": 0.3 # Extend this if needed
        }

        frame_buffer = []
        try:
            while self.running:
                ret, frame = self.cap.read()
                if not ret or frame is None:
                    print("Error: Failed to grab frame.")
                    continue

                self.frame_count += 1
                annotated_frame = frame.copy()

                if self.frame_count % self.skip_frames == 0:
                    results = self.model(frame, device="cpu", conf=0.5, iou=0.5, verbose=False)

                    filtered_results = []
                    grouped_data = {}

                    for result in results:
                        for box in result.boxes:
                            class_id = int(box.cls.item())
                            class_name = class_id_to_name.get(class_id, "Unknown")
                            confidence = float(box.conf.item())
                            threshold = class_thresholds.get(class_name, 0.1)

                            # Apply confidence threshold
                            if confidence >= threshold and (selected_class_index == -1 or class_id == selected_class_index):
                                x1, y1, x2, y2 = map(lambda v: round(float(v), 5), box.xyxy[0])
                                filtered_results.append({
                                    "class_id": class_id,
                                    "class_name": class_name,
                                    "confidence": confidence,
                                    "bbox": (x1, y1, x2, y2)
                                })

                                if class_name not in grouped_data:
                                    grouped_data[class_name] = {"count": 0, "bboxes": []}

                                grouped_data[class_name]["count"] += 1
                                grouped_data[class_name]["bboxes"].append([x1, y1, x2, y2])
        

                    if filtered_results:
                        try:
                            frame_buffer.append(grouped_data)
                    
                            #Show indicator for complete detection
                            if len(frame_buffer) == 7:
                                #self.detectionFeed.setStyleSheet("""QWidget#detectionFeed {background-color: rgb(225, 225, 225);border-radius: 15px;}""")
                                self.camera.setStyleSheet("border: 20px solid rgb(0, 220, 161); border-radius:30px;")
                                self.detection_status.setText("Detection Complete")

                        except Exception as e:
                            print(f"Error in Indicator: {e}")
                                                    
                    else:
                        if frame_buffer:
                            if len(frame_buffer) >=4:
                                self.camera.setStyleSheet("")
                                
                                self.detection_status.setText("")
                                last_data = frame_buffer[3]
                                result = {key: value['count'] for key, value in last_data.items()}
                                frame_buffer.clear()
                    
                                #self.wpcb_id = self.wpcb_info(self.operation_id, result)
                                self.wpcb_id = self.db_function.wpcb_info(self.operation_id, result)
                                print("Done wpcb_id")

                                #Update the first tab tables for detected compoents
                                self.update_detected_component_table(self.wpcb_id)
                                self.update_detected_wpcb_table(self.operation_id)
                                print("Done First Tab")

                                #update the second tab table for metal content
                                self.db_function.insert_to_db(self.wpcb_id, last_data)
                                self.db_function.process_ec_info(self.wpcb_id, self.operation_id)
                                self.update_metal_content_table(self.operation_id)

                                #update the third tab table for price estimation
                                self.db_function.insert_total_price_value(self.operation_id)
                                self.update_price_estimation_content_table(self.operation_id)
                                self.db_function.insert_total_price(self.operation_id, self.total_price_list)
                                self.update_price_estimation_total_price_table(self.operation_id)

                    #Display the annotated object to the frame
                    for item in filtered_results:
                        class_id = item["class_id"]
                        class_name = class_id_to_name.get(class_id, "Unknown")
                        #confidence = item["confidence"]
                        x1, y1, x2, y2 = item["bbox"]
                        #label = f"{class_name} {round(confidence, 2)}"
                        label = f"{class_name}"
                        color = class_colors.get(class_id, (255, 255, 255))

                        cv2.rectangle(annotated_frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
                        cv2.putText(annotated_frame, label, (int(x1), int(y1) - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                        
                    #For displaying the last frame in the feed
                    self.last_filtered_serialized_results = filtered_results
                    self.last_results = results

                elif self.last_results:
                    annotated_frame = frame.copy()
                    for item in self.last_filtered_serialized_results:
                        class_id = item["class_id"]
                        class_name = class_id_to_name.get(class_id, "Unknown")
                        #confidence = item["confidence"]
                        x1, y1, x2, y2 = item["bbox"]
                        #label = f"{class_name} {round(confidence, 2)}"
                        label = f"{class_name}"
                        color = class_colors.get(class_id, (255, 255, 255))

                        cv2.rectangle(annotated_frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
                        cv2.putText(annotated_frame, label, (int(x1), int(y1) - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

                self.display_frame(annotated_frame)

            self.cap.release()
        except Exception as e:
            print("Unhandled Exception:", e)
            traceback.print_exc()
            self.cap.release()


    def display_frame(self, frame):
        """Displays a frame in the PyQt5 window."""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w
        q_img = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)

        # Convert to pixmap and scale it to a fixed larger size (e.g., 960x720)
        pixmap = QPixmap.fromImage(q_img).scaled(
            900, 500,  # You can adjust this size
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        self.camera.setPixmap(pixmap)
        #self.camera.setScaledContents(True)

    
def run_main_window(pro_id):
    app = QApplication(sys.argv)
    main_window = MyApp(pro_id)
    main_window.show()
    sys.exit(app.exec_())  # Run the event loop for the main window


def run_application():
    pro_id = run_login_window()  # Get the returned pro_id
    if pro_id is not None:
        run_main_window(pro_id)
    else:
        print("Login failed or canceled.")


if __name__ == '__main__':
    run_application()  # Start the application with login