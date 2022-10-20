import matplotlib.pyplot as plt
import pandas as pd
from dotenv import load_dotenv
import os
import json
import http.client
from flagit.src.flagit import flagit
from datetime import datetime, timedelta
import glob

load_dotenv()

api_connection = http.client.HTTPSConnection('api.precisionsustainableag.org')


class SoilFlagger:
    def __init__(self):
        self.save_as_excel = True
        self.chart_moisture = True
        self.codes = ['bii', 'bgp', 'hvq', 'sos',
                      'pqt', 'rkm', 'sjc', 'tcc', 'hfe', 'alr']

        data_path = r'C:\Users\mspinega\Documents\repos\test\soil-moisture\ccsp_data'
        file_names = glob.glob(data_path + "\*.xlsx")

        # for loop to iterate all excel files
        for file_name in file_names:
            # reading excel files
            print("Reading file = ", file_name)
            self.read_ars_data(pd.read_excel(file_name),
                               file_name.split("\\")[-1])

        # self.chart_versions()

    def read_ars_data(self, df, file_name):
        df.rename(columns={'SensorIDNum': 'uid', 'Timestamp': 'index', 'VWC': 'soil_moisture',
                           'Ts': 'soil_temp', 'Rain_mm_HrlySum': 'precipitation'}, inplace=True)

        dfs = dict(tuple(df.groupby('uid')))

        self.data_by_serial_number = dfs

        # print(dfs)

        self.flag_ars_soil_data(file_name)

    def flag_ars_soil_data(self, file_name):
        rejoined_df = pd.DataFrame()
        # for each key and value in self.data_by_serial_number create a new dataframe and process it
        for key, value in self.data_by_serial_number.items():
            df = pd.DataFrame(value)

            df = df.dropna()
            df['soil_moisture'] = 100 * df['soil_moisture']
            # print(df)
            if df.empty:
                continue
            # print(df)

            df = df.sort_values(by='index')
            df = df.set_index('index')
            df = df[~df.index.duplicated(keep='first')]

            try:
                df['timestamp'] = pd.to_datetime(df.index)
            except Exception:
                print('hello')
                # print(df)

            if '2017' in file_name:
                interface = flagit.Interface(
                    df, frequency=1)
            else:
                interface = flagit.Interface(
                    df, frequency=0.25)
            new_df = interface.run()

            # print(new_df)
            rejoined_df = rejoined_df.append(new_df)

        # print(file_name)
        rejoined_df['soil_moisture'] = rejoined_df['soil_moisture'] / 100

        rejoined_df.rename(columns={'uid': 'SensorIDNum', 'index': 'Timestamp', 'soil_moisture': 'VWC',
                           'soil_temp': 'Ts', 'precipitation': 'Rain_mm_HrlySum'}, inplace=True)

        rejoined_df.sort_values(["PlotNum", "SensorIDNum", "timestamp"],
                                inplace=True)

        rejoined_df = rejoined_df.reset_index()

        rejoined_df = rejoined_df.drop('index', axis=1)

        print(rejoined_df)

        if self.save_as_excel:
            rejoined_df.to_excel(file_name.split('.')[0] + ' Flagged.xlsx')


sf = SoilFlagger()
