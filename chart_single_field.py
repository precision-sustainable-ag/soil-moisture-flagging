import matplotlib.pyplot as plt
import pandas as pd
from dotenv import load_dotenv
import os
import json
import http.client
from flagit.src.flagit import flagit
from datetime import datetime, timedelta

load_dotenv()

api_connection = http.client.HTTPSConnection('api.precisionsustainableag.org')


class SoilFlagger:
    def __init__(self):
        self.save_as_excel = True
        self.chart_moisture = True

        self.code = 'QZT'
        self.subplot = 1
        self.treatment = 'b'

        self.fetch_single_field()

    def fetch_single_field(self):
        soil_data = self.fetch_onfarm_api(
            '/onfarm/soil_moisture?output=json&type=tdr&code={}&subplot={}&treatment={}'.format(self.code, self.subplot, self.treatment))

        # call extract_soil_data() with the data previously fetched
        data_by_field = self.extract_soil_data(soil_data)
        # print(soil_data)
        dfs = self.run_flagit(data_by_field)
        # dfs = [flagit_df_5, flagit_df_15, flagit_df_45, flagit_df_80]
        # print(dfs)
        for df in dfs:
            self.chart_soil_data(df)

    def fetch_onfarm_api(self, uri, code=None):
        if code is not None:
            uri += code

        # get api key from .env
        api_key = os.environ.get('X_API_KEY')

        # append api key to headers
        api_headers = {'x-api-key': api_key}

        # request the soil moisture endpoint
        api_connection.request('GET', uri, headers=api_headers)

        # get response
        api_res = api_connection.getresponse()
        api_data = api_res.read()

        # print(api_data)

        # convert to json
        json_api_data = api_data.decode('utf8')
        try:
            api_json_data = json.loads(json_api_data)
            # send back response
            return(api_json_data)
        except Exception:
            print(json_api_data)

    def extract_soil_data(self, soil_data):
        # used to organize data by serial number
        data_by_field = {
            'soil_moisture': [],
            'soil_temperature': [],
            'uid': [],
            'index': [],
            'is_vwc_outlier': [],
            'center_depth': [],
            'vwc_outlier_who_decided': [],
        }

        # iterate each row returned by the api
        for item in soil_data:
            if item.get('node_serial_no') and item.get('center_depth'):
                # get vwc, uid, and timestamp and append it to data_by_field[<current items serial number>][<vwc/uid/timestamp>]
                if item.get('vwc'):
                    data_by_field['soil_moisture'].append(
                        float(item.get('vwc')))
                    data_by_field['soil_temperature'].append(
                        item.get('soil_temp'))
                    data_by_field['uid'].append(
                        int(item.get('uid')))
                    data_by_field['index'].append(
                        item.get('timestamp'))
                    data_by_field['is_vwc_outlier'].append(
                        item.get('is_vwc_outlier'))
                    data_by_field['center_depth'].append(
                        item.get('center_depth'))
                    data_by_field['vwc_outlier_who_decided'].append(
                        item.get('vwc_outlier_who_decided'))

        return data_by_field

    def run_flagit(self, data_by_field):
        # for each key and value in data_by_field create a new dataframe and process it

        # make df
        df = pd.DataFrame(data_by_field)
        # print(df)
        if df.empty:
            return

        df = df.sort_values(by='index')
        df = df.set_index('index')
        df = df[~df.index.duplicated(keep='first')]
        # df.to_csv("test.csv")
        
        try:
            df['timestamp'] = pd.to_datetime(df.index)
        except Exception:
            print('hello')
            print(df)

        flagit_df_5 = df[df['center_depth'] == -5]
        flagit_df_15 = df[df['center_depth'] == -15]
        flagit_df_45 = df[df['center_depth'] == -45]
        flagit_df_80 = df[df['center_depth'] == -80]

        if not flagit_df_5.empty:
            interface_5 = flagit.Interface(
                flagit_df_5, frequency=0.25)
            flagit_df_5 = interface_5.run()

        if not flagit_df_15.empty:
            interface_15 = flagit.Interface(
                flagit_df_15, frequency=0.25)
            flagit_df_15 = interface_15.run()

        if not flagit_df_45.empty:
            interface_45 = flagit.Interface(
                flagit_df_45, frequency=0.25)
            flagit_df_45 = interface_45.run()
        
        if not flagit_df_80.empty:
            interface_80 = flagit.Interface(
                flagit_df_80, frequency=0.25)
            flagit_df_80 = interface_80.run()

        # print(flagit_df_5)
        # print(flagit_df_15)
        # print(flagit_df_45)
        # print(flagit_df_80)

        return flagit_df_5, flagit_df_15, flagit_df_45, flagit_df_80

    def chart_soil_data(self, df):
        index = 0
        # fig, axs = plt.subplots(1, 2)
        print(df)

        if df.empty:
            return

        both_good = df.loc[(df['is_vwc_outlier'] == False) & (df['qflag'] == {'G'})]
        human_bad = df.loc[(df['is_vwc_outlier'] == True) & (df['qflag'] == {'G'})]
        flagit_bad = df.loc[(df['is_vwc_outlier'] == False) & (df['qflag'] != {'G'})]
        both_bad = df.loc[(df['is_vwc_outlier'] == True) & (df['qflag'] != {'G'})]


        # other = df.loc[(df['qflag'] != {'D06'}) & (df['qflag'] != {'D07'}) & (df['qflag'] != {
        #     'D08'}) & (df['qflag'] != {'D09'}) & (df['qflag'] != {'D10'}) & (df['qflag'] != {'D11'}) & (df['qflag'] != {'G'})]

        # d06 = df.loc[df['qflag'] == {'D06'}]
        # d07 = df.loc[df['qflag'] == {'D07'}]
        # d08 = df.loc[df['qflag'] == {'D08'}]
        # d11 = df.loc[df['qflag'] == {'D11'}]

        # filter out all rows that are not marked good and save the to an excel file
        # filtered_df = df.loc[df['qflag'] != {'G'}]
        filtered_df = df.loc[df['is_vwc_outlier'] == True]
        # filtered_df.to_excel('results_filtered{}.xlsx'.format(index))

        percentage_flagged = round(df.loc[df['qflag'] != {
            'G'}, 'qflag'].count() / df['qflag'].count() * 100, 3)
        # print(percentage_flagged)

        # axs[0].scatter(df['timestamp'].values,
        #                 df['soil_moisture'].values, color='blue')
        # axs[0].scatter(filtered_df['timestamp'].values,
        #                 filtered_df['soil_moisture'].values, color='red')
        # axs[0].set_title(self.code + ' ' + str(self.code) + ' original')

        # axs[1].scatter(df['timestamp'].values,
        #                 df['soil_moisture'].values, color='blue')

        # axs[1].scatter(d06['timestamp'].values,
        #                 d06['soil_moisture'].values, color='red')
        # axs[1].scatter(d07['timestamp'].values,
        #                 d07['soil_moisture'].values, color='green')
        # axs[1].scatter(d08['timestamp'].values,
        #                 d08['soil_moisture'].values, color='yellow')

        # axs[1].scatter(d11['timestamp'].values,
        #                 d11['soil_moisture'].values, color='gray')
        # axs[1].scatter(other['timestamp'].values,
        #                 other['soil_moisture'].values, color='brown')

        plt.scatter(both_good['timestamp'].values,
                        both_good['soil_moisture'].values, color='black')
        plt.scatter(human_bad['timestamp'].values,
                        human_bad['soil_moisture'].values, color='blue')
        plt.scatter(flagit_bad['timestamp'].values,
                        flagit_bad['soil_moisture'].values, color='red')
        plt.scatter(both_bad['timestamp'].values,
                        both_bad['soil_moisture'].values, color='gray')

        # plt.set_title(self.code + ' ' + str(self.code) + ' flagit' +
        #                     ' %flag ' + str(percentage_flagged))

        # increase timestamp
        index += 1

        plt.show()

sf = SoilFlagger()
