from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from azure.data.tables import TableServiceClient
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config.from_object('config.Config')

# Azure Table Storage Client
connect_str = app.config['CONNECTION_STRING']
table_service = TableServiceClient.from_connection_string(connect_str)
table_client = table_service.get_table_client("DeviceTest01")

# Function: Get data by date range
def get_data_by_date_range(start_date, end_date):
    query = f"TS ge '{start_date.isoformat()}Z' and TS lt '{end_date.isoformat()}Z'"
    data = table_client.query_entities(query, select=['ImageUrl', 'Description', 'TS', 'Weevil_number'])
    return sorted(data, key=lambda x: x['TS'])

# Function: Find the earliest date in the dataset
def find_earliest_data():
    all_data = table_client.query_entities(query_filter="", select=['TS', 'Weevil_number'])
    all_dates = [datetime.fromisoformat(entry['TS'].replace('Z', '')) for entry in all_data]
    return min(all_dates) if all_dates else datetime.today() - timedelta(days=365)

# Function: Aggregate data by month or day
def aggregate_data(data, by='month'):
    aggregated = {}
    for entry in data:
        timestamp = datetime.fromisoformat(entry['TS'].replace('Z', ''))
        key = timestamp.strftime('%Y-%m') if by == 'month' else timestamp.strftime('%Y-%m-%d')
        aggregated[key] = aggregated.get(key, 0) + entry.get('Weevil_number', 0)
    return aggregated

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data')
def data():
    selected_date = request.args.get('date', datetime.today().isoformat())
    start_date = datetime.fromisoformat(selected_date)
    end_date = start_date + timedelta(days=1)
    data = get_data_by_date_range(start_date, end_date)
    return render_template('data.html', data=data, selected_date=selected_date)

@app.route('/chart-data')
def chart_data():
    start_date = find_earliest_data()
    end_date = datetime.today()
    data = get_data_by_date_range(start_date, end_date)
    aggregated = aggregate_data(data, by='day')
    chart_data = [{'date': k, 'count': v} for k, v in aggregated.items()]
    return jsonify(chart_data)

@app.route('/update_weevil_number/<partition_key>/<row_key>', methods=['POST'])
def update_weevil_number(partition_key, row_key):
    new_value = request.form.get('weevil_count')
    entity = table_client.get_entity(partition_key=partition_key, row_key=row_key)
    entity['Weevil_number'] = int(new_value)
    table_client.update_entity(entity)
    flash('Weevil number updated successfully', 'success')
    return redirect(url_for('data'))

if __name__ == '__main__':
    app.run(debug=True)
