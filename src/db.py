from sqlmodel import Session,create_engine,SQLModel
from .db_models import TaskResults
import os 
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


def generate_and_commit_task_results_db(plots, task_id):

    results = []

    for result in plots:
        results.append(TaskResults(
            task_id=task_id,
            plot_id=result.plot_id,
            result=result.data
        ))
    
    commit_results(results)

