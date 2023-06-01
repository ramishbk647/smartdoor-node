from flask import Flask, render_template
import boto3

# AWS credentials and region 
# configuration
aws_access_key_id = 'AKIA4YPVYXHWKNHSR2YX'
aws_secret_access_key = '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'
aws_region_name = 'ap-southeast-2' 

# DynamoDB table and column names
table_name = 'sensors_data'
id_column = 'ID'
sonar_column = 'sonar'
pir_column = 'pir'

# Connect to AWS DynamoDB
try:
    dynamodb = boto3.resource('dynamodb',
                              aws_access_key_id=aws_access_key_id,
                              aws_secret_access_key=aws_secret_access_key,
                              region_name=aws_region_name)
    print('Successfully connected to AWS DynamoDB')
except Exception as e:
    print('Error connecting to AWS DynamoDB:', str(e))
    exit()

# Connect to DynamoDB table
try:
    table = dynamodb.Table(table_name)
    print('Successfully connected to DynamoDB table:', table_name)
except Exception as e:
    print('Error connecting to DynamoDB table:', str(e))
    exit()

app = Flask(__name__)

@app.route('/')
def home_page():
    response = table.scan()
    items = response['Items']
    if items:
        # Sort the items based on timestamp (ID) in descending order
        items.sort(key=lambda x: x[id_column], reverse=True)
        latest_value = items[0].get(sonar_column)
    else:
        latest_value = None

    # Render the template with the latest value
    return render_template('index.html', latest_value=latest_value)

# Route for the webpage
@app.route('/analytics')
def display_data():
    response = table.scan()
    items = response['Items']
    
    # Analytics calculations
    sonar_values = [int(item[sonar_column]) for item in items]
    pir_values = [item[pir_column] for item in items]
    
    max_sonar = max(sonar_values)
    min_sonar = min(sonar_values)
    below_12_count = sum(1 for value in sonar_values if value < 12)
    pir_1_count = pir_values.count(1)
    total_data = len(items)
    
    return render_template('analytics.html', items=items, max_sonar=max_sonar, min_sonar=min_sonar,
                           below_12_count=below_12_count, pir_1_count=pir_1_count, total_data=total_data)

if __name__ == '__main__':
    app.run(debug=True)