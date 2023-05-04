import pandas as pd
import numpy as np


class TransformDataFrame:
    def __init__(self, df_tracks, df_audio_ft):
        self.df_tracks = df_tracks
        self.df_audio_ft = df_audio_ft
    

    def concat_data(self):

        self.df_tracks.reset_index(drop=True, inplace=True)
        self.df_audio_ft.reset_index(drop=True, inplace=True)

        #df_join = pd.concat([self.df_tracks, self.df_audio_ft], axis=1) OLD WAY

        df_join = self.df_tracks.merge(self.df_audio_ft, on='id', how='inner')

        df_join["title"] = df_join["name"] + " - " + df_join["artist"]



        df_join.to_csv("output.csv")

        return df_join
    

    def _remove_unnecessary_columns(self):
        pass

    def _rename_and_organize_columns(self,concat_data):

        renamed_columns = {
            'id' : 'song_id',
            'name' : 'song_name',
            'key' : 'song_key',
            'mode' : 'song_mode',
            'uri' : 'song_uri',
            
        }

        return concat_data.rename(columns=renamed_columns)


    def _key_normalization(self):

        self.final_df["key"] = self.final_df["key"].map(
            {
                0: "C",
                1: "C#",
                2: "D",
                3: "D#",
                4: "E",
                5: "F",
                6: "F#",
                7: "G",
                8: "G#",
                9: "A",
                10: "A#",
                11: "B",
            }
        )

        self.final_df["mode"] = self.final_df["mode"].map({1: "Major", 0: "Minor"})

        return self.final_df["key"], self.final_df["mode"]



    
