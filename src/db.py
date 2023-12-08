from sqlmodel import Session,create_engine,SQLModel, select
from .db_models import TaskResults, TaskRuns, PlotTypes
import os 
from datetime import datetime, timedelta

def create_db_engine():
    try:
        db_url  = f'postgresql://{os.environ["POSTGRES_USER"]}:{os.environ["POSTGRES_PASSWORD"]}@{os.environ["POSTGRES_HOST"]}/{os.environ["POSTGRES_DB"]}'
        engine = create_engine(db_url, echo=True)
        return engine
    except Exception as e: 
        print(f"Couldn't create the connection: {e}")

def create_db_and_tables():
    engine = create_db_engine()
    SQLModel.metadata.create_all(engine)

def commit_results(results):

    engine = create_db_engine()

    with Session(engine) as session:
        for r in results:
            session.add(r)
        session.commit()

def generate_and_commit_task_metadata_db(user_data, number_of_tracks):

    user_task_metadata = TaskRuns(task_id=user_data.task.id,
                                    user_id=user_data.id,
                                    number_of_tracks=number_of_tracks,
                                    started_at=user_data.task.started_at,
                                    finished_at=datetime.today())
            
    commit_results([user_task_metadata])

def generate_and_commit_task_results_db(plots, task_id):

    results = []

    for result in plots:
        results.append(TaskResults(
            task_id=task_id,
            plot_id=result.plot_id,
            result=result.data,
            created=datetime.today()
        ))
    
    commit_results(results)



def select_user_runs(user_id):
    
    engine = create_db_engine()

    current_date = datetime.today()

    current_date_minus_30 = datetime.today() + timedelta(-30)

    with Session(engine) as session:
        statement = select(TaskRuns).where(TaskRuns.user_id==user_id).where(TaskRuns.finished_at >= current_date_minus_30).where(TaskRuns.finished_at <= current_date)
        results = session.exec(statement).first()

    if results:
        return results.task_id
    else:
        return None
    

def select_results(task_id):

    engine = create_db_engine()

    with Session(engine) as session:
        statement = select(TaskResults, PlotTypes).join(PlotTypes).where(TaskResults.task_id == task_id)

        results = session.exec(statement).all()



    if results:
        data = {"plots": {}}
        for task_result, plot_type in results:
            data["plots"][plot_type.name] = task_result.result
        return data

    
    return {"plots" : None}

    



def create_plot_types():

    engine = create_db_engine()

    with Session(engine) as session:
        statement = select(PlotTypes)

        results = session.exec(statement).first()

    
    if not results:

        ## Create rows

        plot_types = [PlotTypes(id=1,name="radar_chart"),PlotTypes(id=2,name="pie_chart"),PlotTypes(id=3,name="top_3_artist"),
                      PlotTypes(id=4, name="saved_tracks_timeline"),PlotTypes(id=5,name="scatter_chart"),PlotTypes(id=6, name="table_tracks")]

        with Session(engine) as session:

            for t in plot_types:
                session.add(t)

            session.commit()

