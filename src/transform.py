import pandas as pd
import numpy as np


class TransformDataFrame:
    def __init__(self, df_tracks, df_audio_ft):
        self.df_tracks = df_tracks
        self.df_audio_ft = df_audio_ft

    def _key_normalization(self, final_df):
        final_df["key"] = final_df["key"].map(
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

        final_df["is_major"] = final_df["mode"].map({1: True, 0: False})

        return final_df["key"], final_df["is_major"]
