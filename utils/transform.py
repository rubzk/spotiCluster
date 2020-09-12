import pandas as pd 
import numpy as np
from sklearn.preprocessing import MinMaxScaler

def concat_data(df_info_tracks, df_audio_ft):

    df_info_tracks.reset_index(drop=True, inplace=True)
    df_audio_ft.reset_index(drop=True, inplace=True)

    df_join = pd.concat([df_info_tracks, df_audio_ft], axis =1)

    return df_join


def scale_data(df, features):

    scaler = MinMaxScaler()

    scaled_df = pd.DataFrame(scaler.fit_transform(df[features]))

    scaled_df.columns = features

    return scaled_df
