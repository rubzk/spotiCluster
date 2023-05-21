import pandas as pd
import numpy as np


class TransformDataFrame:
    def __init__(self, df_tracks, df_audio_ft):
        self.df_tracks = df_tracks
        self.df_audio_ft = df_audio_ft

    def concat_data(self):
        self.df_tracks.reset_index(drop=True, inplace=True)
        self.df_audio_ft.reset_index(drop=True, inplace=True)

        # df_join = pd.concat([self.df_tracks, self.df_audio_ft], axis=1) OLD WAY

        df_join = self.df_tracks.merge(self.df_audio_ft, on="id", how="inner")

        df_join["title"] = df_join["name"] + " - " + df_join["artist"]

        df_join["key"], df_join["is_major"] = self._key_normalization(df_join)

        return df_join

    def _remove_unnecessary_columns(self):
        pass

    def rename_and_reindex_columns(self, concat_data):
        renamed_columns = {
            "id": "song_id",
            "name": "song_name",
            "key": "song_key",
            "mode": "song_mode",
            "uri": "song_uri",
        }

        reindex_columns = [
            "spotify_user_id",
            "song_id",
            "song_name",
            "artist",
            "title",
            "song_uri",
            "song_key",
            "is_major",
            "danceability",
            "energy",
            "loudness",
            "speechiness",
            "acousticness",
            "instrumentalness",
            "liveness",
            "valence",
            "tempo",
            "time_signature",
            "duration_ms",
            "track_href",
            "analysis_url",
            "created",
        ]

        concat_data = concat_data.rename(columns=renamed_columns)

        return concat_data.reindex(columns=reindex_columns)

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
