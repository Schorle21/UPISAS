import requests
def SWITCH_bootup():
    #Run the scripts 
    print("Invoking process.py scripts...")
    url = "http://localhost:3001/execute-python-script"
    response = requests.post(url)
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.text}")

    print("Setting Naive model")
    url = "http://localhost:3001/useNaiveKnowledge"
    response = requests.post(url)
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.text}")

    print("Uploading files and starting processing...")

    #Upload the form data
    url = "http://localhost:3001/api/upload"
    files = {
        "zipFile": open("./images/photos1.zip", "rb") if "./images/photos1.zip" else None,
        "csvFile": open("./images/intervals.csv", "rb"),
    }
    data = {
        "approch": "NAVIE",  # Replace with the actual value of `selectedOption`
        "folder_location": ""  # Replace with the actual value of `loc`, or remove if None
    }

    # Send POST request
    response = requests.post(url, files=files, data=data)

    # Handle response
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.text}")