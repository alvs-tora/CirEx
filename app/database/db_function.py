import pymysql
import math
import random
from datetime import datetime
from app.database.db_connector import DatabaseConnection

class DatabaseFunction:
    def __init__(self):
        self.db = DatabaseConnection(use_local=True)

    def get_fullname(self, pro_id):
        connection = self.db.connect_to_db()
        if connection:
            try:
                cursor = connection.cursor()
                query = "SELECT s_name, f_name FROM profile_info WHERE pro_id = %s;"
                cursor.execute(query, (pro_id,))
                result = cursor.fetchone()

                if result:
                    s_name, f_name = result  # Unpack both values
                    return s_name, f_name    # Return both
                else:
                    return None, None
            except pymysql.MySQLError as e:
                print(f"Database query error: {e}")
                return None
            finally:
                connection.close()

    def input_start_operation_data(self, pro_id, formatted_name, formatted_time):
        connection = self.db.connect_to_db()
        if connection:
            try:
                cursor = connection.cursor()
                query = """INSERT INTO `start_operation` (
                        `pro_id`,
                        `f_name`,
                        `created_at`
                        )
                        VALUES (%s,%s,%s);"""
                cursor.execute(query, (pro_id,formatted_name,formatted_time,))
                connection.commit()

                # Get the last inserted ID (operation_id)
                operation_id = cursor.lastrowid
                
                return operation_id  # Return the operation_id of the inserted row

            except pymysql.MySQLError as e:
                print(f"Database query error: {e}")
                return None
            finally:
                connection.close()

        return None
    

    def input_stop_operation_data(self, operation_id):
        now = datetime.now() # Get current date and time
        formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")# Format it as "YYYY-MM-DD HH:MM:SS"
        connection = self.db.connect_to_db()
        if connection:
            try:
                cursor = connection.cursor()
                query = """UPDATE `start_operation`
                            SET
                            `ends_at` = %s,
                            `runtime` = TIMESTAMPDIFF(MINUTE, `created_at`, `ends_at`)
                            WHERE `operation_id` = %s;
                            """
                cursor.execute(query, (formatted_time, operation_id,))
                connection.commit()
            except pymysql.MySQLError as e:
                print(f"Database query error: {e}")
                return None
            finally:
                connection.close()

        return None
    

    def wpcb_info(self, operation_id, category):
        
        now = datetime.now()  # Get current date and time
        formatted_time = now.strftime("%Y-%m-%d-%H:%M:%S")  # Format it properly for SQL
        image_name = f"IMG-{formatted_time}"

        # Retrieve counts for each class, default to 0 if not found
        BGA = category.get('BGA', 0)
        DIP = category.get('DIP', 0)
        Inductor = category.get('Inductor', 0)
        QFP = category.get('QFP', 0)
        REC = category.get('REC', 0)
        SMD_EC = category.get('SMD EC', 0)
        SOP = category.get('SOP', 0)

        # Sum the counts from each class
        total = BGA + DIP + Inductor + QFP + REC + SMD_EC + SOP

        connection = self.db.connect_to_db()
        if connection:
            try:
                cursor = connection.cursor()

                # Step 1: Find current max wpcb_id_per_operation for this operation_id
                cursor.execute("""
                    SELECT MAX(wpcb_id_per_operation)
                    FROM wpcb_info
                    WHERE operation_id = %s
                """, (operation_id,))
                max_per_operation = cursor.fetchone()[0]
                if max_per_operation is None:
                    max_per_operation = 0

                next_wpcb_id_per_operation = max_per_operation + 1

                # Step 2: Insert new data including wpcb_id_per_operation
                query = """
                    INSERT INTO wpcb_info (
                        operation_id,
                        wpcb_id_per_operation,
                        created_at,
                        image_name,
                        BGA,
                        DIP,
                        Inductor,
                        QFP,
                        REC,
                        `SMD EC`,
                        SOP,
                        total_class
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                """
                cursor.execute(query, (
                    operation_id,
                    next_wpcb_id_per_operation,
                    formatted_time,
                    image_name,
                    BGA,
                    DIP,
                    Inductor,
                    QFP,
                    REC,
                    SMD_EC,
                    SOP,
                    total,
                ))
                connection.commit()

                wpcb_id = cursor.lastrowid  # Get the last inserted ID
                return wpcb_id

            except pymysql.MySQLError as e:
                print(f"Database query error: {e}")
                return None
            finally:
                connection.close()

        return None
    

    def get_detected_components(self, wpcb_id):
        connection = self.db.connect_to_db()
        if connection:
            try:
                cursor = connection.cursor()
                query = """
                    SELECT BGA, DIP, Inductor, QFP, REC, `SMD EC`, SOP 
                    FROM wpcb_info 
                    WHERE wcpb_id = %s;
                """
                cursor.execute(query,(wpcb_id,))
                result = cursor.fetchone()

                if result:
                    return result  # Tuple of numbers
                else:
                    return None
            except pymysql.MySQLError as e:
                print(f"Database query error: {e}")
                return None
            finally:
                connection.close()

        return None
    



    def get_detected_wpcb(self, operation_id):
        """Retrieve all detected PCB data based on operation_id."""

        connection = self.db.connect_to_db()
        if connection:
            try:
                cursor = connection.cursor()
                query = """
                    SELECT wpcb_id_per_operation, total_class
                    FROM wpcb_info
                    WHERE operation_id = %s
                    ORDER BY created_at ASC;  -- Fetch all entries ordered by timestamp
                """

                cursor.execute(query, (operation_id,))
                results = cursor.fetchall()  # Fetch all rows for the given operation_id

                if results:
                    return results  # Return all the rows as a list of tuples
                else:
                    return None
            except pymysql.MySQLError as e:
                print(f"Database query error: {e}")
                return None
            finally:
                connection.close()

        return None

    def convert_bboxes_to_mm(self,detections):

        """
        Convert detected bounding boxes into real-world width and length in mm,
        using a fixed reference DIP component for calibration.

        Parameters:
            detections (list): List of dicts with 'class_id' and 'bbox' in [x1, y1, x2, y2] format.

        Returns:
            List[dict]: Each dict contains 'class_id', 'width_mm', and 'length_mm'.
        """
        # Reference bounding box (pixels) from the image of the 8-pin DIP
        # This is the bounding box in pixels for an 8-pin DIP used for calibration
        ref_bbox = [384.45968, 110.78724, 413.61536, 136.94418]
        
        # Calculate the width and length of the reference bounding box in pixels
        ref_width_px = ref_bbox[2] - ref_bbox[0]
        ref_length_px = ref_bbox[3] - ref_bbox[1]

        # Actual physical dimensions of the reference 8-pin DIP (in mm)
        ref_width_mm = 7.9  # Width of an 8-pin DIP in mm
        ref_length_mm = 9.22  # Length of an 8-pin DIP in mm

        # Calculate scaling factors (pixels per mm) based on the reference
        px_per_mm_width = ref_width_px / ref_width_mm
        px_per_mm_length = ref_length_px / ref_length_mm

        # Process detections and convert to millimeters
        output = []
        for det in detections:
            class_id = det['class_id']
            x1, y1, x2, y2 = det['bbox']
            
            # Calculate width and length in pixels
            width_px = x2 - x1
            length_px = y2 - y1

            size_px = sorted([width_px, length_px]) 

            width_px = size_px[0]
            length_px = size_px[1]

            # Convert pixels to millimeters using the scaling factors
            width_mm = round(width_px / px_per_mm_width, 2)
            length_mm = round(length_px / px_per_mm_length, 2)

            # Add converted data to the output list
            output.append({
                'class_id': class_id,
                'width_mm': width_mm,
                'length_mm': length_mm
            })

        return output

    def insert_to_db(self, wpcb_id, detections):
            """
            Insert detection data into the ec_info table.

            Parameters:
                wpcb_id (int): The PCB ID associated with the detection data.
                detections (dict): Dictionary with category names and bounding boxes.
            """
            # Flatten the detections into a list of dictionaries
            flattened_detections = []
            for category, data in detections.items():
                for bbox in data['bboxes']:
                    flattened_detections.append({'class_id': category, 'bbox': bbox})


            # Convert bounding boxes to millimeters
            detections_in_mm = self.convert_bboxes_to_mm(flattened_detections)

            # Connect to the database
            connection = self.db.connect_to_db()
            print("connected")
            if connection:
                try:
                    cursor = connection.cursor()

                    # Insert each detection into the database
                    for detection in detections_in_mm:
                        class_id = detection['class_id']
                        width = detection['width_mm']
                        length = detection['length_mm']

                        # Prepare the SQL query to insert data
                        sql = "INSERT INTO ec_info (wpcb_id, category, width, length) VALUES (%s, %s, %s, %s);"
    
                        values = (wpcb_id, class_id, width, length)

                        # Execute the query
                        cursor.execute(sql, values)

                    # Commit the changes to the database
                    connection.commit()
                    print("Data inserted successfully.") 
                except pymysql.MySQLError as e:
                    print(f"Database query error: {e}")
                finally:
                    # Close the connection and cursor
                    cursor.close()
                    connection.close()
            else:
                print("Failed to connect to the database.")

    def fetch_predefined_components(self):
        """
        Fetch predefined components data from predefined_components_info.
        Returns a dictionary mapping category -> list of (class_id, width, length, metal values...).
        """
        connection = self.db.connect_to_db()
        category_mapping = {}

        try:
            cursor = connection.cursor()
            query = """
            SELECT class_id, category, width, length, 
                gold, silver, copper, aluminum, `lead`, 
                nickel, tin, zinc, platinum, palladium, 
                chromium, iron 
            FROM predefined_components_info;
            """
            cursor.execute(query)
            result = cursor.fetchall()

            for row in result:
                (class_id, category, width, length, 
                gold, silver, copper, aluminum, lead, 
                nickel, tin, zinc, platinum, palladium, 
                chromium, iron) = row

                if category not in category_mapping:
                    category_mapping[category] = []
                category_mapping[category].append((
                    class_id, width, length, gold, silver, copper, aluminum, lead,
                    nickel, tin, zinc, platinum, palladium, chromium, iron
                ))

        except pymysql.MySQLError as e:
            print(f"Error fetching predefined components: {e}")
        finally:
            connection.close()

        return category_mapping

    def calculate_distance(self,width1, length1, width2, length2):
        return math.sqrt((width1 - width2) ** 2 + (length1 - length2) ** 2)

    def match_closest_component(self,width, length, category, predefined_components):
        """
        Match closest component inside the same category by width and length.
        Returns (class_id, metal contents...).
        """
        min_distance = float('inf')
        best_match = None

        if category in predefined_components:
            for component in predefined_components[category]:
                (class_id, comp_width, comp_length, 
                gold, silver, copper, aluminum, lead, 
                nickel, tin, zinc, platinum, palladium, chromium, iron) = component

                distance = self.calculate_distance(width, length, comp_width, comp_length)

                if distance < min_distance:
                    min_distance = distance
                    best_match = {
                        'class_id': class_id,
                        'gold': gold,
                        'silver': silver,
                        'copper': copper,
                        'aluminum': aluminum,
                        'lead': lead,
                        'nickel': nickel,
                        'tin': tin,
                        'zinc': zinc,
                        'platinum': platinum,
                        'palladium': palladium,
                        'chromium': chromium,
                        'iron': iron
                    }

        return best_match
    
    def insert_record(self, operation_id, matched_data, category, width, length):
        connection = self.db.connect_to_db()
        try:
            with connection.cursor() as cursor:
                # Step 1: Retrieve wpcb_id_per_operation
                sql = """
                SELECT wpcb_id_per_operation
                FROM wpcb_info
                WHERE operation_id = %s
                ORDER BY created_at ASC
                """
                cursor.execute(sql, (operation_id,))
                data = cursor.fetchall()

                if not data:
                    print(f"No wpcb_id_per_operation found for wpcb_id={operation_id}")
                    return None

                wpcb_id_per_operation = len(data)

                # Step 2: Prepare INSERT query
                query = """
                INSERT INTO record_info (
                    operation_id, wpcb_id_per_operation, class_id, date_logged, category, width, length,
                    gold, silver, copper, aluminum, `lead`,
                    nickel, tin, zinc, platinum, palladium,
                    chromium, iron
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """

                date_logged = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                values = (
                    operation_id,
                    wpcb_id_per_operation,
                    matched_data['class_id'],
                    date_logged,
                    category,
                    width,
                    length,
                    matched_data['gold'],
                    matched_data['silver'],
                    matched_data['copper'],
                    matched_data['aluminum'],
                    matched_data['lead'],
                    matched_data['nickel'],
                    matched_data['tin'],
                    matched_data['zinc'],
                    matched_data['platinum'],
                    matched_data['palladium'],
                    matched_data['chromium'],
                    matched_data['iron'],
                )

                cursor.execute(query, values)
                connection.commit()
                

        except pymysql.MySQLError as e:
            print(f"Error inserting record: {e}")
            return None
        finally:
            connection.close()

    def process_ec_info(self, wpcb_idx, operation_id):
            """
            Process ec_info records, match components, and insert into record_info.
            """
            predefined_components = self.fetch_predefined_components()
            connection = self.db.connect_to_db()

            try:
                cursor = connection.cursor()
                query = "SELECT wpcb_id, category, width, length FROM ec_info WHERE wpcb_id=%s;"
                cursor.execute(query,(wpcb_idx,))
                ec_info_records = cursor.fetchall()

                for record in ec_info_records:
                    wpcb_id, category, width, length = record

                    matched_data = self.match_closest_component(width, length, category, predefined_components)

                    if matched_data:
                        self.insert_record(operation_id, matched_data, category, width, length)
                    else:
                        print(f"No match found for wpcb_id {wpcb_id} with category {category}.")

            except pymysql.MySQLError as e:
                print(f"Error fetching ec_info: {e}")
            finally:
                connection.close()


    def fetch_metal_prices(self):
        connection = self.db.connect_to_db()
        if connection:
            try:
                cursor = connection.cursor()
                query = "SELECT metal, price_php_per_mg FROM metal_price_info;"
                cursor.execute(query)
                results = cursor.fetchall()  # Fetch all rows

                # Example result: [('gold', 6.200201), ('silver', 0.062115), ...]
                return results

            except pymysql.MySQLError as e:
                print(f"Database query error: {e}")
                return []
            finally:
                connection.close()

        return []

    def insert_total_price_value(self, operation_id):
        connection = self.db.connect_to_db()
        if connection:
            try:
                cursor = connection.cursor()

                # Metals to sum
                metals = [
                    'gold', 'silver', 'copper', 'aluminum', '`lead`', 'nickel',
                    'tin', 'zinc', 'platinum', 'palladium', 'chromium', 'iron'
                ]

                # Get unique wpcb_id_per_operation for this operation_id
                get_wpcb_query = """
                    SELECT DISTINCT wpcb_id_per_operation
                    FROM record_info
                    WHERE operation_id = %s
                    ORDER BY wpcb_id_per_operation ASC;
                """
                cursor.execute(get_wpcb_query, (operation_id,))
                wpcb_ids = cursor.fetchall()
                wpcb_id = wpcb_ids[-1][0]  # Get first wpcb_id (can be modified for multiple wpcb_ids)
           

                # Fetch metal prices
                price_watch = self.fetch_metal_prices()
         

                # Iterate over metals to calculate total weights and market prices
                for i, metal in enumerate(metals):
                    print("inside the loop")
                    print(metal)
                    sum_query = f"""
                        SELECT SUM({metal})
                        FROM record_info
                        WHERE operation_id = %s AND wpcb_id_per_operation = %s;
                    """
                    cursor.execute(sum_query, (operation_id, wpcb_id,))
                    result = cursor.fetchone()
                    total_weight = result[0] if result[0] is not None else 0

                    price_watch_by_one = price_watch[i][1]


                    market_price = round(float(price_watch_by_one), 10) * round(float(total_weight), 10)
                    market_price = round(float(market_price), 10)

                    if market_price == 0:
                        perturbed_expected = 0.0  
                    else:
                        variation = random.uniform(-0.05, 0.05)
                        perturbed_expected = round(market_price * (1 + variation), 10)

                    

                    insert_query = """
                        INSERT INTO total_price_value (
                            operation_id, wpcb_id_per_operation, metals, weight, price
                        ) VALUES (%s, %s, %s, %s, %s);
                    """
                    cursor.execute(insert_query, (operation_id, wpcb_id, f"total_{metal}", total_weight, perturbed_expected))

                # Commit the transaction
                connection.commit()
                print(f"Inserted total price values for operation_id {wpcb_id}.")
                #return wpcb_id

            except Exception as e:
                print(f"Error during insert_total_price_value: {e}")
            finally:
                connection.close()


    def insert_total_price(self, operation_id,total_price_list):
        connection = self.db.connect_to_db()
        if connection:
            try:
                cursor = connection.cursor()
  
                # Get unique wpcb_id_per_operation for this operation_id
                sum_query = f"""
                        SELECT SUM(price)   
                        FROM total_price_value
                        WHERE operation_id = %s;
                    """
                cursor.execute(sum_query, (operation_id,))
                result = cursor.fetchone()
                total_price = round(float(result[0]),5)
                total_price_list.append(total_price)
                
      
                if len(total_price_list) == 1:
                    insert_query = """
                        INSERT INTO total_price (
                            operation_id, total
                        ) VALUES (%s, %s);
                    """
                    cursor.execute(insert_query, (operation_id, total_price))

                else:
                    data = total_price_list[-1]
                    print("Data")
                    print(data)
                    update_query = f"""

                        UPDATE total_price
                        SET total = {data}
                        WHERE operation_id = %s;
                    """
                    cursor.execute(update_query, (operation_id))

                connection.commit()
    

            except Exception as e:
                print(f"Error during insert_total_price_value: {e}")
            finally:
                connection.close()

