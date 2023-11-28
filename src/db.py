from sqlmodel import Session,create_engine,SQLModel, select
from .db_models import TaskResults, TaskRuns
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

        with Session(engine) as session:
            statement = select(TaskResults).where(TaskResults.task_id ==results.task_id)

            plots = session.exec(statement).first()

        return plots.json()
    else:
        return None