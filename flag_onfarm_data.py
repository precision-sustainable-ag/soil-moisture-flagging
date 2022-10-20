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
        self.codes = pd.read_csv("possibly_shepherded_sites.csv")

        self.statistics_data = {
            "code": [],
            "subplot": [],
            "treatment": [],
            "depth": [],
            "percent_both_good": [],
            "percent_flagit_bad": [],
            "percent_human_bad": [],
            "percent_both_bad": [],
            "number_of_samples": [],
        }

        self.total_points = 0

        self.iterate_codes()

    def iterate_codes(self):
        for index, farm_row in self.codes.iterrows():
            
            self.code = farm_row["code"]
            self.subplot = farm_row["subplot"]
            self.treatment = farm_row["treatment"]
            print(self.code)
            
            soil_data = self.fetch_onfarm_api(
                '/onfarm/soil_moisture?output=json&type=tdr&code={}&subplot={}&treatment={}'.format(self.code, self.subplot, self.treatment))
            
            # print(soil_data)

            # # call extract_soil_data() with the data previously fetched
            data_by_field = self.extract_soil_data(soil_data)

            flagit_df_15, flagit_df_45, flagit_df_80 = self.run_flagit(data_by_field)

            self.calculate_statistics([flagit_df_15, flagit_df_45, flagit_df_80], self.code, self.subplot, self.treatment)

            print(self.total_points)

        print(self.total_points)

    def fetch_onfarm_api(self, uri):
        print(uri)

        # get api key from .env
        api_key = os.environ.get('X_API_KEY')

        # append api key to headers
        api_headers = {'x-api-key': api_key}

        # request the soil moisture endpoint
        api_connection.request('GET', uri, headers=api_headers)

        # get response
        api_res = api_connection.getresponse()
        api_data = api_res.read()

        print(api_data)

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

        flagit_df_15 = df[df['center_depth'] == -15]
        flagit_df_45 = df[df['center_depth'] == -45]
        flagit_df_80 = df[df['center_depth'] == -80]

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

        # print(flagit_df_15)
        # print(flagit_df_45)
        # print(flagit_df_80)

        return flagit_df_15, flagit_df_45, flagit_df_80

    def calculate_statistics(self, flagit_dfs, code, subplot, treatment):
        # self.statistics_data = {
        #     "code": [],
        #     "subplot": [],
        #     "treatment": [],
        #     "depth": [],
        #     "percent_both_good": [],
        #     "percent_flagit_bad": [],
        #     "percent_human_bad": [],
        #     "percent_both_bad": [],
        # }

        depth_dict = {
            0: "-15",
            1: "-45",
            2: "-80",
        }

        i = 0
        while i < len(flagit_dfs):
            if flagit_dfs[i].empty:
                i += 1
                continue
            self.total_points += len(flagit_dfs[i])
            self.statistics_data["code"].append(code)
            self.statistics_data["subplot"].append(subplot)
            self.statistics_data["treatment"].append(treatment)
            self.statistics_data["depth"].append(depth_dict[i])
            self.statistics_data["percent_both_good"].append(len(flagit_dfs[i][(flagit_dfs[i]['is_vwc_outlier'] == False) & (flagit_dfs[i]['qflag'] == {'G'})]) / len(flagit_dfs[i]))
            self.statistics_data["percent_flagit_bad"].append(len(flagit_dfs[i][(flagit_dfs[i]['is_vwc_outlier'] == False) & (flagit_dfs[i]['qflag'] != {'G'})]) / len(flagit_dfs[i]))
            self.statistics_data["percent_human_bad"].append(len(flagit_dfs[i][(flagit_dfs[i]['is_vwc_outlier'] == True) & (flagit_dfs[i]['qflag'] == {'G'})]) / len(flagit_dfs[i]))
            self.statistics_data["percent_both_bad"].append(len(flagit_dfs[i][(flagit_dfs[i]['is_vwc_outlier'] == True) & (flagit_dfs[i]['qflag'] != {'G'})]) / len(flagit_dfs[i]))
            self.statistics_data["number_of_samples"].append(len(flagit_dfs[i]))
            # percent_both_good = len(flagit_dfs[i][(flagit_dfs[i]['is_vwc_outlier'] == False) & (flagit_dfs[i]['qflag'] == {'G'})]) / len(flagit_dfs[i])
            # percent_flagit_bad = len(flagit_dfs[i][(flagit_dfs[i]['is_vwc_outlier'] == False) & (flagit_dfs[i]['qflag'] != {'G'})]) / len(flagit_dfs[i])
            # percent_human_bad = len(flagit_dfs[i][(flagit_dfs[i]['is_vwc_outlier'] == True) & (flagit_dfs[i]['qflag'] == {'G'})]) / len(flagit_dfs[i])
            # percent_both_bad = len(flagit_dfs[i][(flagit_dfs[i]['is_vwc_outlier'] == True) & (flagit_dfs[i]['qflag'] != {'G'})]) / len(flagit_dfs[i])

            i += 1

        # percent_both_good_45 = len(flagit_df_15[(flagit_df_15['is_vwc_outlier'] == False) & (flagit_df_15['qflag'] == {'G'})]) / len(flagit_df_15)
        # percent_flagit_bad_45 = len(flagit_df_15[(flagit_df_15['is_vwc_outlier'] == False) & (flagit_df_15['qflag'] != {'G'})]) / len(flagit_df_15)
        # percent_human_bad_45 = len(flagit_df_15[(flagit_df_15['is_vwc_outlier'] == True) & (flagit_df_15['qflag'] == {'G'})]) / len(flagit_df_15)
        # percent_both_bad_45 = len(flagit_df_15[(flagit_df_15['is_vwc_outlier'] == True) & (flagit_df_15['qflag'] != {'G'})]) / len(flagit_df_15)

        # percent_both_good_80 = len(flagit_df_15[(flagit_df_15['is_vwc_outlier'] == False) & (flagit_df_15['qflag'] == {'G'})]) / len(flagit_df_15)
        # percent_flagit_bad_80 = len(flagit_df_15[(flagit_df_15['is_vwc_outlier'] == False) & (flagit_df_15['qflag'] != {'G'})]) / len(flagit_df_15)
        # percent_human_bad_80 = len(flagit_df_15[(flagit_df_15['is_vwc_outlier'] == True) & (flagit_df_15['qflag'] == {'G'})]) / len(flagit_df_15)
        # percent_both_bad_80 = len(flagit_df_15[(flagit_df_15['is_vwc_outlier'] == True) & (flagit_df_15['qflag'] != {'G'})]) / len(flagit_df_15)
        
        stat_df = pd.DataFrame(self.statistics_data)
        stat_df.to_csv("test.csv")
    
    def chart_soil_data(self):
        index = 0

        key_list = []

        # for each key and value in self.data_by_field create a new dataframe and process it
        for key, value in self.data_by_field.items():
            # create dataframe from the current value (one serial number)
            # print(len(value))
            if self.chart_moisture:
                fig, axs = plt.subplots(1, 2)

            df = pd.DataFrame(value)
            if df.empty:
                continue

            df = df.sort_values(by='index')
            df = df.set_index('index')
           
            try:
                df['timestamp'] = pd.to_datetime(df.index)
            except Exception:
                print('hello')
                print(df)

            interface = flagit.Interface(
                df, depth=float(key.split(' ')[1]), frequency=0.25)

            new_df = interface.run()

            # new_filtered_df = new_df.loc[new_df['qflag'].str.contains(
            # "G", case = False)]
            if self.chart_moisture:
                other = new_df.loc[(new_df['qflag'] != {'D06'}) & (new_df['qflag'] != {'D07'}) & (new_df['qflag'] != {
                    'D08'}) & (new_df['qflag'] != {'D09'}) & (new_df['qflag'] != {'D10'}) & (new_df['qflag'] != {'D11'}) & (new_df['qflag'] != {'G'})]

                d06 = new_df.loc[new_df['qflag'] == {'D06'}]
                d07 = new_df.loc[new_df['qflag'] == {'D07'}]
                d08 = new_df.loc[new_df['qflag'] == {'D08'}]
                # d09 = new_df.loc[new_df['qflag'] == {'D09'}]
                # d10 = new_df.loc[new_df['qflag'] == {'D10'}]
                d11 = new_df.loc[new_df['qflag'] == {'D11'}]

            # print(new_df['qflag'].str)

            # d06 = new_df.loc[new_df['qflag'].contains("D06", case=False)]
            # d07 = new_df.loc[new_df['qflag'].contains("D07", case=False)]
            # d08 = new_df.loc[new_df['qflag'].contains("D08", case=False)]
            # d09 = new_df.loc[new_df['qflag'].contains("D09", case=False)]
            # d10 = new_df.loc[new_df['qflag'].contains("D10", case=False)]

            # save raw processing to excel file
            # new_df.to_excel('results{}.xlsx'.format(index))

            # filter out all rows that are not marked good and save the to an excel file
            # filtered_df = new_df.loc[new_df['qflag'] != {'G'}]
            filtered_df = df.loc[df['is_vwc_outlier'] == True]
            # filtered_df.to_excel('results_filtered{}.xlsx'.format(index))

            if '{}_{}_'.format(self.code, str(key)) not in key_list:
                key_list.append('{}_{}_'.format(self.code, str(key)))

            if self.save_as_excel:
                new_df.to_excel('{}_{}_0.005.xlsx'.format(
                    self.code, str(key)))
            # df.to_excel('results_original_{}.xlsx'.format(index))

            # plot original dataframe and processed/filtered dataframe to visually compare
            # ax = df.plot(pd.DatetimeIndex(df.index), df.soil_moisture)

            # df.plot(x='timestamp', y='soil_moisture',
            #         kind='scatter', color='red')

            # filtered_df.plot(filtered_df.index, filtered_df.soil_moisture,
            #                  kind='scatter', ax=ax, color='blue')

            # show plot
            # axs[row_index, col_index].scatter(df['timestamp'].values,
            #                                   df['soil_moisture'].values, color='blue')
            # axs[row_index, col_index].scatter(filtered_df['timestamp'].values,
            #                                   filtered_df['soil_moisture'].values, color='red')
            # axs[row_index, col_index].set_title('Serial no ' + str(key))

            if self.chart_moisture:
                percentage_flagged = round(new_df.loc[new_df['qflag'] != {
                    'G'}, 'qflag'].count() / new_df['qflag'].count() * 100, 3)
                print(percentage_flagged)

                axs[0].scatter(df['timestamp'].values,
                               df['soil_moisture'].values, color='blue')
                axs[0].scatter(filtered_df['timestamp'].values,
                               filtered_df['soil_moisture'].values, color='red')
                axs[0].set_title(self.code + ' ' + str(key) + ' original')

                # axs[1].scatter(new_df['timestamp'].values,
                #                new_df['soil_moisture'].values, color='blue')
                # axs[1].scatter(new_filtered_df['timestamp'].values,
                #                new_filtered_df['soil_moisture'].values, color='red')

                axs[1].scatter(new_df['timestamp'].values,
                               new_df['soil_moisture'].values, color='blue')

                axs[1].scatter(d06['timestamp'].values,
                               d06['soil_moisture'].values, color='red')
                axs[1].scatter(d07['timestamp'].values,
                               d07['soil_moisture'].values, color='green')
                axs[1].scatter(d08['timestamp'].values,
                               d08['soil_moisture'].values, color='yellow')
                # axs[1].scatter(d09['timestamp'].values,
                #                d09['soil_moisture'].values, color='orange')
                # axs[1].scatter(d10['timestamp'].values,
                #                d10['soil_moisture'].values, color='black')
                axs[1].scatter(d11['timestamp'].values,
                               d11['soil_moisture'].values, color='gray')
                axs[1].scatter(other['timestamp'].values,
                               other['soil_moisture'].values, color='brown')

                axs[1].set_title(self.code + ' ' + str(key) + ' flagit' +
                                 ' %flag ' + str(percentage_flagged))

                # increase timestamp
                index += 1
                # col_index += 1

                plt.show()
        # plt.show()
        print(key_list)


# call fetch_soil_data()
# codes = ['edf', 'ntk', 'hnz', 'xnm', 'kkd', 'bii', 'bgp', 'hvq', 'sos', 'pqt']
# codes = ['hnz', 'xnm', 'kkd', 'bii', 'bgp', 'hvq']
sf = SoilFlagger()
