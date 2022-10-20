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
        # unfiltered_code_objs = self.fetch_onfarm_api(
        #     '/onfarm/raw?output=json&table=site_information')

        # code_objs = list(filter(lambda x: x.get('protocols').get(
        #     'sensor_data') == 1, unfiltered_code_objs))

        # self.codes = list(map(lambda x: x.get('code'), code_objs))
        self.save_as_excel = True
        self.chart_moisture = True
        self.codes = ['bii', 'bgp', 'hvq', 'sos',
                      'pqt', 'rkm', 'sjc', 'tcc', 'hfe', 'alr']
        # self.codes = ['hfe', 'alr']
        # self.codes = ['bgp', 'bii']

        # self.iterate_codes()

        for i in range(2, 3):
            self.read_ars_data(i)

        # self.chart_versions()

    def iterate_codes(self):
        for code in self.codes:
            print(code)
            self.code = code
            soil_data = self.fetch_onfarm_api(
                '/onfarm/soil_moisture?output=json&type=tdr&code=', code)
            # print(soil_data)

            # call extract_soil_data() with the data previously fetched
            self.extract_soil_data(soil_data)
            self.chart_soil_data()

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

    # def fetch_soil_data(self, code):
    #     # get api key from .env
    #     api_key = os.environ.get('X_API_KEY')

    #     # append api key to headers
    #     api_headers = {'x-api-key': api_key}

    #     # fetch for a single farm code for simplicity (code=jlo)
    #     #
    #     uri = '/onfarm/soil_moisture?output=json&type=tdr&code=' + code

    #     # uri = '/onfarm/soil_moisture?output=json&type=tdr&code=bii'
    #     # uri = '/onfarm/soil_moisture?output=json&type=tdr&code=bgp'

    #     # request the soil moisture endpoint
    #     api_connection.request('GET', uri, headers=api_headers)

    #     # get response
    #     api_res = api_connection.getresponse()
    #     api_data = api_res.read()

    #     # convert to json
    #     json_api_data = api_data.decode('utf8')
    #     api_json_data = json.loads(json_api_data)

    #     # send back response
    #     return(api_json_data)

    def extract_soil_data(self, soil_data):
        # used to organize data by serial number
        self.data_by_serial_number = {}

        # iterate each row returned by the api
        for item in soil_data:
            if item.get('node_serial_no') and item.get('center_depth'):
                # if the serial number is not in self.data_by_serial_number add it
                identifier = str(item.get('node_serial_no')) + \
                    ' ' + str(item.get('center_depth'))

                if identifier not in self.data_by_serial_number:
                    # print(identifier)
                    self.data_by_serial_number[identifier] = {
                        'soil_moisture': [],
                        'soil_temperature': [],
                        'uid': [],
                        'index': [],
                        'is_vwc_outlier': [],
                    }

                # get vwc, uid, and timestamp and append it to self.data_by_serial_number[<current items serial number>][<vwc/uid/timestamp>]
                if item.get('vwc'):
                    self.data_by_serial_number[identifier]['soil_moisture'].append(
                        float(item.get('vwc')))
                    self.data_by_serial_number[identifier]['soil_temperature'].append(
                        item.get('soil_temp'))
                    self.data_by_serial_number[identifier]['uid'].append(
                        int(item.get('uid')))
                    self.data_by_serial_number[identifier]['index'].append(
                        item.get('timestamp'))
                    self.data_by_serial_number[identifier]['is_vwc_outlier'].append(
                        item.get('is_vwc_outlier'))

    def chart_versions(self):
        # keys = ['bii_18000416 -15_', 'bii_18000416 -45_', 'bii_18000416 -80_', 'bii_18000416 -5_', 'bii_18000429 -15_', 'bii_18000429 -45_', 'bii_18000429 -80_', 'bii_18000429 -5_', 'bii_18000435 -15_', 'bii_18000435 -45_', 'bii_18000435 -80_', 'bii_18000437 -15_', 'bii_18000437 -45_', 'bii_18000437 -80_', 'bgp_18000285 -15_', 'bgp_18000285 -45_', 'bgp_18000285 -80_', 'bgp_18000285 -5_', 'bgp_18000353 -15_', 'bgp_18000353 -45_', 'bgp_18000353 -80_', 'bgp_18000473 -15_', 'bgp_18000473 -45_', 'bgp_18000473 -80_', 'bgp_18000478 -15_', 'bgp_18000478 -45_', 'bgp_18000478 -80_', 'bgp_18000478 -5_', 'hvq_18000314 -15_', 'hvq_18000314 -45_', 'hvq_18000314 -80_', 'hvq_18000508 -15_', 'hvq_18000508 -45_', 'hvq_18000508 -80_', 'hvq_18000526 -15_', 'hvq_18000526 -45_', 'hvq_18000526 -80_', 'hvq_18000526 -5_', 'hvq_18000636 -15_', 'hvq_18000636 -45_', 'hvq_18000636 -80_', 'hvq_18000636 -5_', 'sos_18000539 -15_', 'sos_18000539 -45_', 'sos_18000539 -80_', 'sos_18000539 -5_', 'sos_18000566 -15_', 'sos_18000566 -45_', 'sos_18000566 -80_', 'sos_18000566 -5_', 'sos_18000581 -15_',
        #         'sos_18000581 -45_', 'sos_18000581 -80_', 'sos_18000607 -15_', 'sos_18000607 -45_', 'sos_18000607 -80_', 'pqt_18000094 -15_', 'pqt_18000094 -45_', 'pqt_18000094 -80_', 'pqt_18000218 -15_', 'pqt_18000218 -80_', 'pqt_18000218 -5_', 'pqt_18000218 -45_', 'pqt_18000278 -45_', 'pqt_18000278 -80_', 'pqt_18000287 -45_', 'pqt_18000287 -80_', 'pqt_18000287 -5_', 'sjc_nbugmdrs -15_', 'sjc_nbugmdrs -45_', 'sjc_nbugmdrs -80_', 'sjc_ncjdcwcd -15_', 'sjc_ncjdcwcd -45_', 'sjc_ncjdcwcd -80_', 'sjc_ncjdcwcd -5_', 'tcc_nbbikiwe -15_', 'tcc_nbbikiwe -45_', 'tcc_nbbikiwe -80_', 'tcc_ncqmvnmb -15_', 'tcc_ncqmvnmb -45_', 'tcc_ncqmvnmb -80_', 'tcc_ncqmvnmb -5_', 'hfe_nbcvrpxg -15_', 'hfe_nbcvrpxg -45_', 'hfe_nbcvrpxg -80_', 'hfe_nbkrhbcv -15_', 'hfe_nbkrhbcv -45_', 'hfe_nbkrhbcv -80_', 'hfe_ncmrpbkr -15_', 'hfe_ncmrpbkr -45_', 'hfe_ncmrpbkr -80_', 'hfe_ncmrpbkr -5_', 'hfe_ncparuyv -15_', 'hfe_ncparuyv -45_', 'hfe_ncparuyv -80_', 'hfe_ncparuyv -5_', 'alr_nbyuqgxl -15_', 'alr_nbyuqgxl -45_', 'alr_nbyuqgxl -80_', 'alr_nckwkzfs -15_', 'alr_nckwkzfs -45_', 'alr_nckwkzfs -80_', 'alr_nckwkzfs -5_']

        keys = ['490_-0', '491_-0', '492_-0', '493_-0', '494_-10', '495_-10', '496_-20', '497_-20', '498_-30', '499_-30', '500_-0', '501_-0', '502_-0', '503_-0', '504_-10', '505_-10', '506_-20', '507_-20', '508_-30', '509_-30',
                '510_-0', '511_-0', '512_-0', '513_-0', '514_-10', '515_-10', '516_-20', '517_-20', '518_-30', '519_-30', '520_-0', '521_-0', '522_-0', '523_-0', '524_-10', '525_-10', '526_-20', '527_-20', '528_-30', '529_-30']

        for key in keys:
            # for i in range(0, 13):
            fig, axs = plt.subplots(5, 1)

            old_df = pd.read_excel(
                '{}_ars_new_window_.0.05.xlsx'.format(key))
            # old_filtered_df = old_df.loc[old_df['qflag'] != "{'G'}"]
            old_other = old_df.loc[(old_df['qflag'] != "{'D06'}") & (old_df['qflag'] != "{'D07'}") & (old_df['qflag'] != "{'D08'}") & (
                old_df['qflag'] != "{'D09'}") & (old_df['qflag'] != "{'D10'}") & (old_df['qflag'] != "{'D11'}") & (old_df['qflag'] != "{'G'}")]

            old_d06 = old_df.loc[old_df['qflag'] == "{'D06'}"]
            old_d07 = old_df.loc[old_df['qflag'] == "{'D07'}"]
            old_d08 = old_df.loc[old_df['qflag'] == "{'D08'}"]
            old_d09 = old_df.loc[old_df['qflag'] == "{'D09'}"]
            old_d10 = old_df.loc[old_df['qflag'] == "{'D10'}"]
            old_d11 = old_df.loc[old_df['qflag'] == "{'D11'}"]

            lower_df = pd.read_excel(
                '{}_ars_new_window_.0.005.xlsx'.format(key))
            # old_filtered_df = lower_df.loc[lower_df['qflag'] != "{'G'}"]
            lower_other = lower_df.loc[(lower_df['qflag'] != "{'D06'}") & (lower_df['qflag'] != "{'D07'}") & (lower_df['qflag'] != "{'D08'}") & (
                lower_df['qflag'] != "{'D09'}") & (lower_df['qflag'] != "{'D10'}") & (lower_df['qflag'] != "{'D11'}") & (lower_df['qflag'] != "{'G'}")]

            lower_d06 = lower_df.loc[lower_df['qflag'] == "{'D06'}"]
            lower_d07 = lower_df.loc[lower_df['qflag'] == "{'D07'}"]
            lower_d08 = lower_df.loc[lower_df['qflag'] == "{'D08'}"]
            lower_d09 = lower_df.loc[lower_df['qflag'] == "{'D09'}"]
            lower_d10 = lower_df.loc[lower_df['qflag'] == "{'D10'}"]
            lower_d11 = lower_df.loc[lower_df['qflag'] == "{'D11'}"]

            new_df = pd.read_excel(
                '{}_ars_new_window_.0.001.xlsx'.format(key))
            # new_filtered_df = new_df.loc[new_df['qflag'] != "{'G'}"]
            new_other = new_df.loc[(new_df['qflag'] != "{'D06'}") & (new_df['qflag'] != "{'D07'}") & (new_df['qflag'] != "{'D08'}") & (
                new_df['qflag'] != "{'D09'}") & (new_df['qflag'] != "{'D10'}") & (new_df['qflag'] != "{'D11'}") & (new_df['qflag'] != "{'G'}")]

            new_d06 = new_df.loc[new_df['qflag'] == "{'D06'}"]
            new_d07 = new_df.loc[new_df['qflag'] == "{'D07'}"]
            new_d08 = new_df.loc[new_df['qflag'] == "{'D08'}"]
            new_d09 = new_df.loc[new_df['qflag'] == "{'D09'}"]
            new_d10 = new_df.loc[new_df['qflag'] == "{'D10'}"]
            new_d11 = new_df.loc[new_df['qflag'] == "{'D11'}"]

            newest_df = pd.read_excel(
                '{}_ars_new_window_.0005.xlsx'.format(key))
            # new_filtered_df = new_df.loc[new_df['qflag'] != "{'G'}"]
            newest_other = newest_df.loc[(newest_df['qflag'] != "{'D06'}") & (newest_df['qflag'] != "{'D07'}") & (newest_df['qflag'] != "{'D08'}") & (
                newest_df['qflag'] != "{'D09'}") & (newest_df['qflag'] != "{'D10'}") & (newest_df['qflag'] != "{'D11'}") & (newest_df['qflag'] != "{'G'}")]

            newest_d06 = newest_df.loc[newest_df['qflag'] == "{'D06'}"]
            newest_d07 = newest_df.loc[newest_df['qflag'] == "{'D07'}"]
            newest_d08 = newest_df.loc[newest_df['qflag'] == "{'D08'}"]
            newest_d09 = newest_df.loc[newest_df['qflag'] == "{'D09'}"]
            newest_d10 = newest_df.loc[newest_df['qflag'] == "{'D10'}"]
            newest_d11 = newest_df.loc[newest_df['qflag'] == "{'D11'}"]

            newest_point_5_df = pd.read_excel(
                '{}_ars_new_window_.0001.xlsx'.format(key))
            # new_filtered_df = new_df.loc[new_df['qflag'] != "{'G'}"]
            newest_point_5_other = newest_point_5_df.loc[(newest_point_5_df['qflag'] != "{'D06'}") & (newest_point_5_df['qflag'] != "{'D07'}") & (newest_point_5_df['qflag'] != "{'D08'}") & (
                newest_point_5_df['qflag'] != "{'D09'}") & (newest_point_5_df['qflag'] != "{'D10'}") & (newest_point_5_df['qflag'] != "{'D11'}") & (newest_point_5_df['qflag'] != "{'G'}")]

            newest_point_5_d06 = newest_point_5_df.loc[newest_point_5_df['qflag']
                                                       == "{'D06'}"]
            newest_point_5_d07 = newest_point_5_df.loc[newest_point_5_df['qflag']
                                                       == "{'D07'}"]
            newest_point_5_d08 = newest_point_5_df.loc[newest_point_5_df['qflag']
                                                       == "{'D08'}"]
            newest_point_5_d09 = newest_point_5_df.loc[newest_point_5_df['qflag']
                                                       == "{'D09'}"]
            newest_point_5_d10 = newest_point_5_df.loc[newest_point_5_df['qflag']
                                                       == "{'D10'}"]
            newest_point_5_d11 = newest_point_5_df.loc[newest_point_5_df['qflag']
                                                       == "{'D11'}"]

            # new_windows_df = pd.read_excel(
            #     '{}_hourly_new_coeffs_{}.xlsx'.format(code, i))
            # # new_filtered_df = new_df.loc[new_df['qflag'] != "{'G'}"]
            # new_windows_other = new_windows_df.loc[(new_windows_df['qflag'] != "{'D06'}") & (new_windows_df['qflag'] != "{'D07'}") & (new_windows_df['qflag'] != "{'D08'}") & (
            #     new_windows_df['qflag'] != "{'D09'}") & (new_windows_df['qflag'] != "{'D10'}") & (new_windows_df['qflag'] != "{'G'}")]

            # new_windows_d06 = new_windows_df.loc[new_windows_df['qflag']
            #                                      == "{'D06'}"]
            # new_windows_d07 = new_windows_df.loc[new_windows_df['qflag']
            #                                      == "{'D07'}"]
            # new_windows_d08 = new_windows_df.loc[new_windows_df['qflag']
            #                                      == "{'D08'}"]
            # new_windows_d09 = new_windows_df.loc[new_windows_df['qflag']
            #                                      == "{'D09'}"]
            # new_windows_d10 = new_windows_df.loc[new_windows_df['qflag']
            #                                      == "{'D10'}"]

            # new_error_df = pd.read_excel(
            #     '{}_hourly_new_coeffs_{}.xlsx'.format(code, i))
            # # new_filtered_df = new_df.loc[new_df['qflag'] != "{'G'}"]
            # new_error_other = new_error_df.loc[(new_error_df['qflag'] != "{'D06'}") & (new_error_df['qflag'] != "{'D07'}") & (new_error_df['qflag'] != "{'D08'}") & (
            #     new_error_df['qflag'] != "{'D09'}") & (new_error_df['qflag'] != "{'D10'}") & (new_error_df['qflag'] != "{'G'}")]

            # new_error_d06 = new_error_df.loc[new_error_df['qflag']
            #                                  == "{'D06'}"]
            # new_error_d07 = new_error_df.loc[new_error_df['qflag']
            #                                  == "{'D07'}"]
            # new_error_d08 = new_error_df.loc[new_error_df['qflag']
            #                                  == "{'D08'}"]
            # new_error_d09 = new_error_df.loc[new_error_df['qflag']
            #                                  == "{'D09'}"]
            # new_error_d10 = new_error_df.loc[new_error_df['qflag']
            #                                  == "{'D10'}"]

            # scaled_df = pd.read_excel(
            #     '{}_scaled_by_samples_coeffs_{}.xlsx'.format(code, i))
            # scaled_filtered_df = scaled_df.loc[scaled_df['qflag']
            #                                    != "{'G'}"]

            # new_scaled_df = pd.read_excel(
            #     '{}_new_scaled_values_{}.xlsx'.format(code, i))
            # new_scaled_filtered_df = new_scaled_df.loc[new_scaled_df['qflag']
            #                                            != "{'G'}"]

            # hourly_old_df = pd.read_excel(
            #     '{}_hourly_old_coeffs_{}.xlsx'.format(code, i))

            # hourly_old_filtered_df = hourly_old_df.loc[hourly_old_df['qflag']
            #                                            != "{'G'}"]

            # hourly_new_df = pd.read_excel(
            #     '{}_hourly_new_coeffs_{}.xlsx'.format(code, i))

            # hourly_new_filtered_df = hourly_new_df.loc[hourly_new_df['qflag']
            #                                            != "{'G'}"]

            # percentage_flagged = round(new_df.loc[new_df['qflag'] != {
            #     'G'}, 'qflag'].count() / new_df['qflag'].count() * 100, 3)

            axs[0].scatter(old_df['timestamp'].values,
                           old_df['soil_moisture'].values, color='blue')
            # axs[0].scatter(old_filtered_df['timestamp'].values,
            #                old_filtered_df['soil_moisture'].values, color='red')
            axs[0].scatter(old_d06['timestamp'].values,
                           old_d06['soil_moisture'].values, color='red')
            axs[0].scatter(old_d07['timestamp'].values,
                           old_d07['soil_moisture'].values, color='magenta')
            axs[0].scatter(old_d08['timestamp'].values,
                           old_d08['soil_moisture'].values, color='yellow')
            axs[0].scatter(old_d09['timestamp'].values,
                           old_d09['soil_moisture'].values, color='orange')
            axs[0].scatter(old_d10['timestamp'].values,
                           old_d10['soil_moisture'].values, color='black')
            axs[0].scatter(old_d11['timestamp'].values,
                           old_d11['soil_moisture'].values, color='gray')
            axs[0].scatter(old_other['timestamp'].values,
                           old_other['soil_moisture'].values, color='brown')

            axs[0].set_title(
                key + ' var <= 0.05')

            axs[1].scatter(lower_df['timestamp'].values,
                           lower_df['soil_moisture'].values, color='blue')
            # axs[0].scatter(old_filtered_df['timestamp'].values,
            #                old_filtered_df['soil_moisture'].values, color='red')
            axs[1].scatter(lower_d06['timestamp'].values,
                           lower_d06['soil_moisture'].values, color='red')
            axs[1].scatter(lower_d07['timestamp'].values,
                           lower_d07['soil_moisture'].values, color='magenta')
            axs[1].scatter(lower_d08['timestamp'].values,
                           lower_d08['soil_moisture'].values, color='yellow')
            axs[1].scatter(lower_d09['timestamp'].values,
                           lower_d09['soil_moisture'].values, color='orange')
            axs[1].scatter(lower_d10['timestamp'].values,
                           lower_d10['soil_moisture'].values, color='black')
            axs[1].scatter(lower_d11['timestamp'].values,
                           lower_d11['soil_moisture'].values, color='gray')
            axs[1].scatter(lower_other['timestamp'].values,
                           lower_other['soil_moisture'].values, color='brown')

            axs[1].set_title(
                key + ' var <= 0.005')

            axs[2].scatter(new_df['timestamp'].values,
                           new_df['soil_moisture'].values, color='blue')
            # axs[1].scatter(new_filtered_df['timestamp'].values,
            #                new_filtered_df['soil_moisture'].values, color='red')
            axs[2].scatter(new_d06['timestamp'].values,
                           new_d06['soil_moisture'].values, color='red')
            axs[2].scatter(new_d07['timestamp'].values,
                           new_d07['soil_moisture'].values, color='magenta')
            axs[2].scatter(new_d08['timestamp'].values,
                           new_d08['soil_moisture'].values, color='yellow')
            axs[2].scatter(new_d09['timestamp'].values,
                           new_d09['soil_moisture'].values, color='orange')
            axs[2].scatter(new_d10['timestamp'].values,
                           new_d10['soil_moisture'].values, color='black')
            axs[2].scatter(new_d11['timestamp'].values,
                           new_d11['soil_moisture'].values, color='gray')
            axs[2].scatter(new_other['timestamp'].values,
                           new_other['soil_moisture'].values, color='brown')
            axs[2].set_title(
                key + ' var <= 0.001')

            axs[3].scatter(newest_df['timestamp'].values,
                           newest_df['soil_moisture'].values, color='blue')
            # axs[1].scatter(new_filtered_df['timestamp'].values,
            #                new_filtered_df['soil_moisture'].values, color='red')
            axs[3].scatter(newest_d06['timestamp'].values,
                           newest_d06['soil_moisture'].values, color='red')
            axs[3].scatter(newest_d07['timestamp'].values,
                           newest_d07['soil_moisture'].values, color='magenta')
            axs[3].scatter(newest_d08['timestamp'].values,
                           newest_d08['soil_moisture'].values, color='yellow')
            axs[3].scatter(newest_d09['timestamp'].values,
                           newest_d09['soil_moisture'].values, color='orange')
            axs[3].scatter(newest_d10['timestamp'].values,
                           newest_d10['soil_moisture'].values, color='black')
            axs[3].scatter(newest_d11['timestamp'].values,
                           newest_d11['soil_moisture'].values, color='gray')
            axs[3].scatter(newest_other['timestamp'].values,
                           newest_other['soil_moisture'].values, color='brown')
            axs[3].set_title(
                key + ' var <= 0.0005')

            axs[4].scatter(newest_point_5_df['timestamp'].values,
                           newest_point_5_df['soil_moisture'].values, color='blue')
            # axs[1].scatter(new_filtered_df['timestamp'].values,
            #                new_filtered_df['soil_moisture'].values, color='red')
            axs[4].scatter(newest_point_5_d06['timestamp'].values,
                           newest_point_5_d06['soil_moisture'].values, color='red')
            axs[4].scatter(newest_point_5_d07['timestamp'].values,
                           newest_point_5_d07['soil_moisture'].values, color='magenta')
            axs[4].scatter(newest_point_5_d08['timestamp'].values,
                           newest_point_5_d08['soil_moisture'].values, color='yellow')
            axs[4].scatter(newest_point_5_d09['timestamp'].values,
                           newest_point_5_d09['soil_moisture'].values, color='orange')
            axs[4].scatter(newest_point_5_d10['timestamp'].values,
                           newest_point_5_d10['soil_moisture'].values, color='black')
            axs[4].scatter(newest_point_5_d11['timestamp'].values,
                           newest_point_5_d11['soil_moisture'].values, color='gray')
            axs[4].scatter(newest_point_5_other['timestamp'].values,
                           newest_point_5_other['soil_moisture'].values, color='brown')
            axs[4].set_title(
                key + ' var <= 0.0001')

            # axs[3].scatter(new_windows_df['timestamp'].values,
            #                new_windows_df['soil_moisture'].values, color='blue')
            # # axs[1].scatter(new_filtered_df['timestamp'].values,
            # #                new_filtered_df['soil_moisture'].values, color='red')
            # axs[3].scatter(new_windows_d06['timestamp'].values,
            #                new_windows_d06['soil_moisture'].values, color='red')
            # axs[3].scatter(new_windows_d07['timestamp'].values,
            #                new_windows_d07['soil_moisture'].values, color='magenta')
            # axs[3].scatter(new_windows_d08['timestamp'].values,
            #                new_windows_d08['soil_moisture'].values, color='yellow')
            # axs[3].scatter(new_windows_d09['timestamp'].values,
            #                new_windows_d09['soil_moisture'].values, color='orange')
            # axs[3].scatter(new_windows_d10['timestamp'].values,
            #                new_windows_d10['soil_moisture'].values, color='black')
            # axs[3].scatter(new_windows_other['timestamp'].values,
            #                new_windows_other['soil_moisture'].values, color='brown')
            # axs[3].set_title(
            #     code + ' new windows')

            # axs[4].scatter(new_error_df['timestamp'].values,
            #                new_error_df['soil_moisture'].values, color='blue')
            # # axs[1].scatter(new_filtered_df['timestamp'].values,
            # #                new_filtered_df['soil_moisture'].values, color='red')
            # axs[4].scatter(new_error_d06['timestamp'].values,
            #                new_error_d06['soil_moisture'].values, color='red')
            # axs[4].scatter(new_error_d07['timestamp'].values,
            #                new_error_d07['soil_moisture'].values, color='magenta')
            # axs[4].scatter(new_error_d08['timestamp'].values,
            #                new_error_d08['soil_moisture'].values, color='yellow')
            # axs[4].scatter(new_error_d09['timestamp'].values,
            #                new_error_d09['soil_moisture'].values, color='orange')
            # axs[4].scatter(new_error_d10['timestamp'].values,
            #                new_error_d10['soil_moisture'].values, color='black')
            # axs[4].scatter(new_error_other['timestamp'].values,
            #                new_error_other['soil_moisture'].values, color='brown')
            # axs[4].set_title(
            #     code + ' new error')

            # axs[2].scatter(scaled_df['timestamp'].values,
            #                scaled_df['soil_moisture'].values, color='blue')
            # axs[2].scatter(scaled_filtered_df['timestamp'].values,
            #                scaled_filtered_df['soil_moisture'].values, color='red')
            # axs[2].set_title(
            #     code + ' original coeffs divided by samples, windows scaled by samples')

            # axs[3].scatter(new_scaled_df['timestamp'].values,
            #                new_scaled_df['soil_moisture'].values, color='blue')
            # axs[3].scatter(new_scaled_filtered_df['timestamp'].values,
            #                new_scaled_filtered_df['soil_moisture'].values, color='red')
            # axs[3].set_title(
            #     code + ' mikah\'s new coeffs divided by samples, windows scaled by samples')

            # axs[4].scatter(hourly_old_df['timestamp'].values,
            #                hourly_old_df['soil_moisture'].values, color='blue')
            # axs[4].scatter(hourly_old_filtered_df['timestamp'].values,
            #                hourly_old_filtered_df['soil_moisture'].values, color='red')
            # axs[4].set_title(
            #     code + ' old coeffs, original windows')

            # axs[5].scatter(hourly_new_df['timestamp'].values,
            #                hourly_new_df['soil_moisture'].values, color='blue')
            # axs[5].scatter(hourly_new_filtered_df['timestamp'].values,
            #                hourly_new_filtered_df['soil_moisture'].values, color='red')
            # axs[5].set_title(
            #     code + ' new coeffs, original windows')

            # index += 1

            plt.show()

    def read_ars_data(self, version):
        if version == 2:
            ars_data = pd.read_excel(
                r'C:\Users\mspinega\Documents\repos\test\soil-moisture\ars_data\2020 CCSP Rep4 Sample Data More Decimals.xlsx')
        elif version == 1:
            ars_data = pd.read_excel(
                r'C:\Users\mspinega\Documents\repos\test\soil-moisture\ars_data\2017 R4S1 10in.xlsx')
        else:
            ars_data = pd.read_excel(
                r'C:\Users\mspinega\Documents\repos\test\soil-moisture\ars_data\2019 R3S2 10 in.xlsx')

        dfs = dict(tuple(ars_data.groupby('uid')))

        self.data_by_serial_number = dfs

        print(dfs)

        self.chart_ars_soil_data()

    def chart_ars_soil_data(self):
        index = 0

        key_list = []
        # for each key and value in self.data_by_serial_number create a new dataframe and process it
        for key, value in self.data_by_serial_number.items():
            # create dataframe from the current value (one serial number)
            # print(len(value))
            if self.chart_moisture:
                # fig, axs = plt.subplots(1, 1)
                fig, axs = plt.subplots(1, 2)

            df = pd.DataFrame(value)
            df = df.dropna()
            df['soil_moisture'] = 100 * df['soil_moisture']
            print(df)
            if df.empty:
                continue
            # print(df)
            df = df.sort_values(by='index')
            df = df.set_index('index')

            try:
                df['timestamp'] = pd.to_datetime(df.index)
            except Exception:
                print('hello')
                print(df)

            depth = df['depth'].iloc[0]

            interface = flagit.Interface(
                df, depth=depth, frequency=0.25)
            new_df = interface.run()

            if self.chart_moisture:
                other = new_df.loc[(new_df['qflag'] != {'D06'}) & (new_df['qflag'] != {'D07'}) & (new_df['qflag'] != {
                    'D08'}) & (new_df['qflag'] != {'D09'}) & (new_df['qflag'] != {'D10'}) & (new_df['qflag'] != {'D11'}) & (new_df['qflag'] != {'G'})]

                d06 = new_df.loc[new_df['qflag'] == {'D06'}]
                d07 = new_df.loc[new_df['qflag'] == {'D07'}]
                d08 = new_df.loc[new_df['qflag'] == {'D08'}]
                d09 = new_df.loc[new_df['qflag'] == {'D09'}]
                d10 = new_df.loc[new_df['qflag'] == {'D10'}]
                d11 = new_df.loc[new_df['qflag'] == {'D11'}]

            if '{}_-{}'.format(str(key), str(depth)) not in key_list:
                key_list.append('{}_-{}'.format(str(key), str(depth)))

            if self.save_as_excel:
                new_df.to_excel('{}_-{}_ars_new_window_.0.05.xlsx'.format(
                    str(key), str(depth)))

            if self.chart_moisture:
                percentage_flagged = round(new_df.loc[new_df['qflag'] != {
                    'G'}, 'qflag'].count() / new_df['qflag'].count() * 100, 3)
                print(percentage_flagged)

                axs[1].scatter(new_df['timestamp'].values,
                               new_df['soil_moisture'].values, color='blue')

                axs[1].scatter(d06['timestamp'].values,
                               d06['soil_moisture'].values, color='red')
                axs[1].scatter(d07['timestamp'].values,
                               d07['soil_moisture'].values, color='green')
                axs[1].scatter(d08['timestamp'].values,
                               d08['soil_moisture'].values, color='yellow')
                axs[1].scatter(d09['timestamp'].values,
                               d09['soil_moisture'].values, color='orange')
                axs[1].scatter(d10['timestamp'].values,
                               d10['soil_moisture'].values, color='black')
                axs[1].scatter(d11['timestamp'].values,
                               d11['soil_moisture'].values, color='gray')
                axs[1].scatter(other['timestamp'].values,
                               other['soil_moisture'].values, color='brown')

                axs[1].set_title(str(key) + ' flagit' +
                                 ' %flag ' + str(percentage_flagged))

                axs[0].scatter(new_df['timestamp'].values,
                               new_df['precipitation'].values, color='blue')
                axs[0].set_title(str(key) + ' precipitation events')

                # increase timestamp
                index += 1
                # col_index += 1

                plt.show()
        # plt.show()
        print(key_list)

    def chart_soil_data(self):
        # used to distinguish excel files
        index = 0
        # col_index = 0
        # row_index = 0
        # obj_length = len(self.data_by_serial_number)
        # print(obj_length)

        # for i in range(0, obj_length):

        # print(self.data_by_serial_number)
        # print(len(self.data_by_serial_number))

        key_list = []
        # for each key and value in self.data_by_serial_number create a new dataframe and process it
        for key, value in self.data_by_serial_number.items():
            # create dataframe from the current value (one serial number)
            # print(len(value))
            if self.chart_moisture:
                fig, axs = plt.subplots(1, 2)
            # print(value)

            # if index % 2 != 0 and index != 0:
            #     col_index = 0
            #     row_index += 1

            # print(row_index, col_index)

            df = pd.DataFrame(value)
            if df.empty:
                continue
            # print(df)
            df = df.sort_values(by='index')
            df = df.set_index('index')
            # df = df.iloc[::4, :]
            # print(df)

            # date_index = pd.DatetimeIndex(data=value['timestamp'], freq='infer')
            # print(date_index)

            # sorted_dates = sorted(datetime.strptime(
            #     d, '%Y-%m-%d %H:%M:%S') for d in value['timestamp'])

            # time_difference = timedelta(0)
            # counter = 0
            # for i in range(1, len(sorted_dates), 1):
            #     counter += 1
            #     time_difference += sorted_dates[i] - sorted_dates[i-1]

            # frequency = time_difference / counter
            # print('Frequency is ' + str(frequency.seconds / 3600))  # freq in hours

            # instantiate the Iterface class from flagit using the dataframe and run processing
            # print(df)
            # print(index)
            try:
                df['timestamp'] = pd.to_datetime(df.index)
            except Exception:
                print('hello')
                print(df)

            interface = flagit.Interface(
                df, depth=float(key.split(' ')[1]), frequency=0.25)
            # interface = flagit.Interface(
            #     df, depth=df['depth'].iloc(0), frequency=0.25)
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
