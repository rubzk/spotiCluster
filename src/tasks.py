import json
from src.extract import DataExtractor
import credentials
from src.transform import TransformDataFrame
from src.plot import Plot3D
from plotly.utils import PlotlyJSONEncoder
from celery import shared_task


@shared_task(bind=True,name='app.lala')
def tarea(self,auth_code):
    self.update_state(state='PROGRESS', 
    meta={'current': 0, 'total': 100, 'status': 'Getting Auth'})
    extractor = DataExtractor(credentials.client_id, credentials.client_secret, credentials.redirect_uri, 50, auth_code)
    self.update_state(state='PROGRESS', 
    meta={'current': 33, 'total': 100, 'status': 'Transforming data'})
    transform = TransformDataFrame(extractor.df_tracks_info, extractor.df_audio_ft)
    self.update_state(state='PROGRESS', 
    meta={'current': 66, 'total': 100, 'status': 'Generating the plots'})
    plotter = Plot3D(transform.final_df, transform.n_clusters, transform.cluster_stats)

    form_data = {'polar': plotter.radar_chart(),
                 'scatter3d': {
                     1: plotter.scatter_3d('danceability', 'valence', 'energy'),
                     2: plotter.scatter_3d('loudness', 'tempo', 'acousticness'),
                     3: plotter.scatter_3d('speechiness', 'acousticness', 'instrumentalness'),
                     4: plotter.scatter_3d('tempo', 'energy', 'loudness')
                 },
                 'keys_bar': plotter.bar_chart({'x':plotter.df['key'].value_counts().values ,
                                                'y': plotter.df['key'].value_counts().index.to_list(),
                                                'color': plotter.df['key'].value_counts().index.to_list(),
                                                'orientation': 'h',
                                                'width': 450,
                                                'height': 450,
                                                'layout': {
                                                    'title': 'Key Appearence',
                                                    'xaxis': 'Number of keys',
                                                    'yaxis': 'Keys'
                                                }}),
                 'mode_bar': plotter.bar_chart({'x':plotter.df['mode'].value_counts().index.to_list() ,
                                                'y': plotter.df['mode'].value_counts().values,
                                                'color': plotter.df['mode'].value_counts().index.to_list(),
                                                'orientation': 'v',
                                                'width': 450,
                                                'height': 450,
                                                'layout': {
                                                    'title': 'Mode of songs',
                                                    'xaxis': 'Mode type ',
                                                    'yaxis': 'Count'
                                                }}),
                 'cluster_bar': plotter.bar_chart({'x':plotter.df['cluster_name'].value_counts().values ,
                                                'y': plotter.df['cluster_name'].value_counts().index.to_list(),
                                                'color': plotter.df['cluster_name'].value_counts().index.to_list(),
                                                'orientation': 'h',
                                                'width': 450,
                                                'height': 450,
                                                'layout': {
                                                    'title': 'Cluster Classes',
                                                    'xaxis': 'Count',
                                                    'yaxis': 'Cluster number'
                                                }}),
                 'user_data': [plotter.n_clusters, transform.n_tracks],
                 'scatter_matrix': plotter.scatter_matrix({'dimensions': ['danceability', 'valence','tempo','energy'],
                                                           'color': 'cluster'})}

    form_data = json.dumps(form_data, cls=PlotlyJSONEncoder)

    return {'current': 100, 'total': 100, 'status': 'DONE!', 'plots': form_data}
