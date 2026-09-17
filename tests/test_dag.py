from airflow.models import DagBag


def load_financial_dag():
    dag_bag = DagBag(dag_folder="airflow/dags", include_examples=False)
    assert dag_bag.import_errors == {}
    return dag_bag.dags.get("financial_data_pipeline")


def test_dag_imports():
    assert load_financial_dag() is not None


def test_dag_tasks():
    dag = load_financial_dag()
    assert set(dag.task_ids) == {"extract", "transform", "load"}


def test_dag_dependencies():
    dag = load_financial_dag()
    assert dag.get_task("extract").downstream_task_ids == {"transform"}
    assert dag.get_task("transform").downstream_task_ids == {"load"}
    assert dag.get_task("load").downstream_task_ids == set()
