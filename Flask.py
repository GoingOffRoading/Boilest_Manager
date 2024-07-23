# app.py

from flask import Flask, render_template, request
import mysql.connector, subprocess, os

app = Flask(__name__)

# Database connection details
config = {
    'user': os.getenv('sql_user'),
    'password': os.getenv('sql_pswd'),
    'host': os.getenv('sql_host'),
    'port': os.getenv('sql_port'),
    'database': os.getenv('sql_database'),
}

# Function to connect to the MariaDB database
def connect_db():
    return mysql.connector.connect(**config)

# Function to retrieve metrics and table data from the database
def get_data_from_db():
    with connect_db() as conn:
        cursor = conn.cursor()

        # Query 1
        cursor.execute('SELECT SUM(new_file_size_difference) AS space_saved FROM ffmpeghistory')
        result_1 = cursor.fetchone()[0]

        # Query 2
        cursor.execute('SELECT COUNT(unique_identifier) AS files_processed FROM ffmpeghistory')
        result_2 = cursor.fetchone()[0]

        # Query 3
        cursor.execute('SELECT COUNT(DISTINCT(SUBSTRING(recorded_date, 1, 10))) AS day FROM ffmpeghistory')
        result_3 = cursor.fetchone()[0]

        # Query 4
        cursor.execute('SELECT ROUND(SUM(new_file_size_difference)/COUNT(unique_identifier)) AS saved_space FROM ffmpeghistory')
        result_4 = cursor.fetchone()[0]

        # Query for the first table data
        cursor.execute('SELECT substr(recorded_date, 1, 10) AS day, SUM(new_file_size_difference) AS space_saved, '
                       'COUNT(unique_identifier) AS files_processed, SUM(new_file_size) AS data_processed '
                       'FROM ffmpeghistory fr GROUP BY day ORDER BY DAY DESC limit 10;')
        table_data_1 = cursor.fetchall()

        # Query for the second table data
        cursor.execute('SELECT * FROM ffmpeghistory ORDER BY recorded_date DESC LIMIT 50;')
        table_data_2 = cursor.fetchall()

    return result_1, result_2, result_3, result_4, table_data_1, table_data_2

# Route for the home page
@app.route('/', methods=['GET', 'POST'])
def index():
    template_path = 'index.html'

    # Check for script execution
    if request.method == 'POST' and request.form.get('execute_script') == 'Execute':
        # Execute a Python script when the button is clicked
        subprocess.run(['python', 'start.py'], check=True)

    # Get data from the database
    result_1, result_2, result_3, result_4, table_data_1, table_data_2 = get_data_from_db()

    print('diagnostic1')

    # Render the template with the retrieved data
    return render_template(template_path, result_1=result_1, result_2=result_2, result_3=result_3, result_4=result_4,
                           table_data_1=table_data_1, table_data_2=table_data_2)

if __name__ == '__main__':
    app.run(debug=True)
