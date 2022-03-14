import matplotlib.pyplot as plt
import pandas as pd
from dotenv import load_dotenv
import os
import json
import http.client
from flagit.src.flagit import flagit
from datetime import datetime, timedelta

load_dotenv()

api_connection = http.client.HTTPSConnection("api.precisionsustainableag.org")


def fetch_soil_data():
    # get api key from .env
    api_key = os.environ.get('X_API_KEY')

    # append api key to headers
    api_headers = {"x-api-key": api_key}

    # fetch for a single farm code for simplicity (code=jlo)
    #
    # uri = "/onfarm/soil_moisture?output=json&type=tdr&code=bii"
    uri = "/onfarm/soil_moisture?output=json&type=tdr&code=bgp"

    # request the soil moisture endpoint
    api_connection.request("GET", uri, headers=api_headers)

    # get response
    api_res = api_connection.getresponse()
    api_data = api_res.read()

    # convert to json
    json_api_data = api_data.decode('utf8')
    api_json_data = json.loads(json_api_data)

    # send back response
    return(api_json_data)


def extract_soil_data(soil_data):
    # used to organize data by serial number
    data_by_serial_number = {}

    # iterate each row returned by the api
    for item in soil_data:
        if item.get("node_serial_no") and item.get("center_depth"):
            # if the serial number is not in data_by_serial_number add it
            identifier = str(item.get("node_serial_no")) + \
                " " + str(item.get("center_depth"))

            if identifier not in data_by_serial_number:
                # print(identifier)
                data_by_serial_number[identifier] = {
                    "soil_moisture": [],
                    "soil_temperature": [],
                    "uid": [],
                    "index": [],
                }

            # get vwc, uid, and timestamp and append it to data_by_serial_number[<current items serial number>][<vwc/uid/timestamp>]
            data_by_serial_number[identifier]["soil_moisture"].append(
                item.get("vwc"))
            data_by_serial_number[identifier]["soil_temperature"].append(
                item.get("soil_temp"))
            data_by_serial_number[identifier]["uid"].append(
                int(item.get("uid")))
            data_by_serial_number[identifier]["index"].append(
                item.get("timestamp"))

    # used to distinguish excel files
    index = 0
    col_index = 0
    row_index = 0
    # obj_length = len(data_by_serial_number)
    # print(obj_length)

    # for i in range(0, obj_length):
    fig, axs = plt.subplots(8, 2)

    # print(data_by_serial_number)
    print(len(data_by_serial_number))

    # for each key and value in data_by_serial_number create a new dataframe and process it
    for key, value in data_by_serial_number.items():
        # create dataframe from the current value (one serial number)
        # print(len(value))

        if index % 2 != 0 and index != 0:
            col_index = 0
            row_index += 1

        print(row_index, col_index)

        df = pd.DataFrame(value)
        # print(df)
        df = df.sort_values(by="index")
        df = df.set_index("index")
        # df = df.iloc[::4, :]
        # print(df)

        # date_index = pd.DatetimeIndex(data=value["timestamp"], freq="infer")
        # print(date_index)

        # sorted_dates = sorted(datetime.strptime(
        #     d, '%Y-%m-%d %H:%M:%S') for d in value["timestamp"])

        # time_difference = timedelta(0)
        # counter = 0
        # for i in range(1, len(sorted_dates), 1):
        #     counter += 1
        #     time_difference += sorted_dates[i] - sorted_dates[i-1]

        # frequency = time_difference / counter
        # print("Frequency is " + str(frequency.seconds / 3600))  # freq in hours

        # instantiate the Iterface class from flagit using the dataframe and run processing
        # print(df)
        df["timestamp"] = pd.to_datetime(df.index)

        interface = flagit.Interface(df)
        new_df = interface.run()

        # save raw processing to excel file
        new_df.to_excel("results{}.xlsx".format(index))

        # filter out all rows that are not marked good and save the to an excel file
        filtered_df = new_df.loc[new_df['qflag'] == {'G'}]
        filtered_df.to_excel("results_filtered{}.xlsx".format(index))

        # plot original dataframe and processed/filtered dataframe to visually compare
        # ax = df.plot(pd.DatetimeIndex(df.index), df.soil_moisture)

        # df.plot(x="timestamp", y="soil_moisture",
        #         kind='scatter', color='red')

        # filtered_df.plot(filtered_df.index, filtered_df.soil_moisture,
        #                  kind='scatter', ax=ax, color='blue')

        # show plot
        axs[row_index, col_index].scatter(df["timestamp"].values,
                                          df["soil_moisture"].values, color='red')
        axs[row_index, col_index].scatter(filtered_df["timestamp"].values,
                                          filtered_df["soil_moisture"].values, color='blue')
        axs[row_index, col_index].set_title("Serial no " + str(key))

        # plt.scatter(df["timestamp"].values,
        #             df["soil_moisture"].values, color='red')
        # plt.scatter(filtered_df["timestamp"].values,
        #             filtered_df["soil_moisture"].values, color='blue')
        # plt.title("Serial no " + str(key))

        # increase timestamp
        index += 1
        col_index += 1

    plt.show()


# call fetch_soil_data()
soil_data = fetch_soil_data()

# call extract_soil_data() with the data previously fetched
extract_soil_data(soil_data)
