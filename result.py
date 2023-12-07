'''the program provides informarion on plant care, including infromation on watering and sunlight'''

import grovepi
import time
import requests

#a file where all the details about the plant will be written  
with open("plant_project.txt", "w") as file:
    pass  # The file is empty (does not store past data)

grovepi.set_bus('RPI_1')

buttonPort = 3  # Connect the button sensor to D3
lightSensorPort = 1  # Connect the analog light sensor to A1

grovepi.pinMode(buttonPort, "INPUT")
button_presses = []
condition = [0]


#function for writing information to a file
def write_to_file(content):
    with open("plant_project.txt", "a") as file:
        file.write(content + "\n")


#get dates from a website 
def get_plant_details(api_key, plant_id):
    # Retrieve plant watering, and sunlight information
    url = f"https://perenual.com/api/species/details/{plant_id}"
    params = {
        "key": api_key,
    }
    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        watering_info = data.get("watering")
        sunlight_info = data.get("sunlight")
        write_to_file(f"Plant ID: {plant_id}")
        write_to_file("-----------------------------------------------------")

 
#writing the frequeny of plants watering (with explanation)
        if watering_info:
            write_to_file(f"Watering Information: {watering_info}")

            if watering_info == "Frequent":
                write_to_file("(Frequent: Daily or every other day)")

            if watering_info == "Average":
                write_to_file("(Average: Every 2-3 days or as needed)")

            if watering_info == "Minimum":
                write_to_file("(Minimum: Once a week or less)")

            if watering_info == "None":
                print("(None: Rarely, only during extended dry spells)")
                write_to_file("(None: Rarely, only during extended dry spells)")
        else:
            print("Watering Information: Data not available")
            write_to_file("Watering Information: Data not available")

        write_to_file("-----------------------------------------------------")


#receiving the information about sunlight 

        if sunlight_info:
            initial_light_sensor_value = grovepi.analogRead(lightSensorPort)
            print("Initial Light Sensor Value:", initial_light_sensor_value)
            write_to_file("Initial Light Sensor Value: {}".format(initial_light_sensor_value))

        #every light-value is corresponding to the certain "state" (shade, full sun..)
            if initial_light_sensor_value <= 200:
                print("the plant is currently in full shade")
                write_to_file("the plant is currently in full shade")
                write_to_file("-----------------------------------------------------")

            if 200 < initial_light_sensor_value <= 1000:
                print("the plant is currently in Part Shade")
                write_to_file("the plant is currently in Part Shade")

            if 1000 < initial_light_sensor_value <= 5000:
                print("the plant is currently in Sun-Part Shade")
                write_to_file("the plant is currently in Sun-Part Shade")

            if initial_light_sensor_value > 5000:
                print("the plant is currently in Full Sun")
                write_to_file("the plant is currently in Full Sun")

            write_to_file(f"Sunlight Information: {sunlight_info}")


        #explaining what "full sun", "part shade" etc mean (in relation to the light-sensor value)
        #condition: checks if the state of the plant corresponds to the right one 
            if "full sun" in sunlight_info or "Full sun" in sunlight_info:
                write_to_file("(Full Sun: Above 5000 lux)")
                if initial_light_sensor_value > 5000:
                    condition.append(1)

            if "part shade" in sunlight_info or "Part shade" in sunlight_info:
                write_to_file("(Part Shade: 200-1000 lux)")
                if 200 < initial_light_sensor_value <= 1000:
                    condition.append(1)

            if "sun-part shade" in sunlight_info or "Sun-part shade" in sunlight_info:
                write_to_file("(Sun-Part Shade: 1000-5000 lux)")
                if 1000 < initial_light_sensor_value <= 5000:
                    condition.append(1)

            if "Full shade" in sunlight_info or "full shade" in sunlight_info:
                write_to_file("(Full Shade: 0-200 lux)")
                if initial_light_sensor_value <= 200:
                    condition.append(1)
        else:
            print("Sunlight Information: Data not available")
        write_to_file("-----------------------------------------------------")
    else:
        print("Failed to fetch plant information.")


#button should be pressed every time the plant is being watered 
def handle_button_press():
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S") #at what time the plant was watered
    event = "The plant was watered"

#to prevent "long pressing" of the button, it is fixed that the interval between watering 
#should be at least a minute 

    if len(button_presses) > 0:
        last_timestamp = button_presses[-1][0]
        last_timestamp_obj = time.strptime(last_timestamp, "%Y-%m-%d %H:%M:%S")
        current_timestamp_obj = time.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
        time_diff = time.mktime(current_timestamp_obj) - time.mktime(last_timestamp_obj)
        if time_diff < 60:
            return  
    button_presses.append((timestamp, event))

    # Open the file in append mode and write the event details
    with open("plant_project.txt", "a") as file:
        file.write(f"{timestamp}: {event}\n")
      


#the report is generated to sum up the amoout of watering per day 
#by default time is set to 00:00 
def generate_report():
    unique_presses = len(set([event[0] for event in button_presses]))
    print(f"At 00:00, the plant was watered {unique_presses} times.")
    write_to_file("-----------------------------------------------------")
    write_to_file(f"At 00:00, the plant was watered {unique_presses} times.")



if __name__ == "__main__":
    api_key = "sk-znXo650c485dacfa52244"  
    #details from the plant can be obtained via ID
    plant_id = input("Enter plant ID: ")
    get_plant_details(api_key, plant_id)
    pressing_button = 0
    last_watering_time = time.time()  # Initialize the time of last watering

    if 1 in condition:
        print("the plant is in the right place")
        write_to_file("the plant is in the right place")
        write_to_file("-----------------------------------------------------")

    else:
        print("your plant might not receiving the right amount of the sun, please check the data")
        write_to_file("your plant might not receiving the right amount of the sun, please check the data")
        write_to_file("-----------------------------------------------------")


    try:
        while True:
            button_value = grovepi.digitalRead(buttonPort)

            if button_value == 1:
                handle_button_press()
                pressing_button += 1
                last_watering_time = time.time()  # Update the time of last watering
                print("Button pressed at:", time.strftime("%Y-%m-%d %H:%M:%S"))
            

            current_time = time.strftime("%H:%M")

            # Check if it's time to generate the report
            #should be 00:00
            if current_time == "15:50":
                generate_report()
                time.sleep(60)  # Wait for a minute to avoid repetitive reports

            time.sleep(0.2)
            # Check if it's time to print the watering count
          

        

    except KeyboardInterrupt:
        print('Program stopped by the user (Ctrl+C)')
