from db import db
import pandas as pd

'''
INSERT INTO location(location_id, location_name)
VALUES (row1[col1], row2[col2]);
'''

def populate_db(csvfile):
    df = pd.read_csv(csvfile, low_memory=False)
    # low_memory is a quick fix, would usually specify dtypes but want function to process both files

    if 'locationData' in csvfile:
        # rename columns (otherwise unit of measurement row has no use)
        # actually no need to do this since columns are already named in MySQL
        old = list(df)  # list of old column names
        num_cols = df.shape[1]
        for col in range(1, num_cols):  # skip 1st column
            df.rename(columns={old[col]: old[col] + '_' + df.iloc[0][col]}, inplace=True)
        df.drop(0, inplace=True)  # delete unit of measurement row
        df.reset_index(drop=True, inplace=True)  # reset index after deletion

        # for col in df.columns:
        #     if df[col].isnull().values.any():
        #         print(col, '\n', df[col].value_counts(dropna=False))
        """
        - locationMap.csv contains no Nans
        - locationData.csv contains Nans in all columns except time and locationID
        We cannot just drop all rows with NaNs as this would be deleting a large portion of our dataset.
        e.g Gust column has over 100k NaNs
        could fill with 0s but this may result in less accurate analysis when calculating statistics such as
        location with highest atmospheric pressure, instead we will set to the average
        """
        df.fillna(0, inplace=True)
        float_cols = ['AtmosphericPressure_mb', 'WindSpeed_kn', 'Gust_kn']
        for col in float_cols:
            df[col] = df[col].astype(float)
            avg = df[col].mean()
            # df = df.mask(df == 0).fillna(df.mean()) # using mask make all 0 to np.nan, then fillna
            df.replace({col: {0: avg}}, inplace=True)

        col = 'WindDirection_degrees_true'
        df[col] = df[col].astype(int)
        avg = df[col].mean()
        df.replace({col: {0: avg}}, inplace=True)

        col = 'time_UTC'
        df[col] = pd.to_datetime(df[col])  # Conversion from string to datetime

    for i, row in df.iterrows():
        if 'Map' in csvfile:
            sql = "INSERT INTO location VALUES(%s,%s);"
        else:
            sql = "INSERT INTO weather VALUES (%s,%s,%s,%s,%s,%s);"
        cursor = db.connection.cursor()
        cursor.execute(sql, tuple(row))
        db.connection.commit()


populate_db("data/locationMap.csv")
#populate_db("data/locationData.csv")




