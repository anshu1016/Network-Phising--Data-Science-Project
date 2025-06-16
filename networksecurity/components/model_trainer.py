import os
import sys
from dotenv import load_dotenv
from urllib.parse import urlparse

from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.entity.artifact_entity import DataTransformationArtifact, ModelTrainerArtifact
from networksecurity.entity.config_entity import ModelTrainerConfig
from networksecurity.utils.ml_utils.model.estimator import NetworkModel
from networksecurity.utils.main_utils.utils import save_object, load_object, load_numpy_array_data, evaluate_models
from networksecurity.utils.ml_utils.metric.classification_metric import get_classification_score

from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, AdaBoostClassifier
import mlflow
import mlflow.sklearn
import dagshub


# Load environment variables and initialize Dagshub
load_dotenv()
dagshub.init(repo_owner='anshu1016', repo_name='Network-Phising--Data-Science-Project', mlflow=True)

# Setup MLflow environment
mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI"))
os.environ["MLFLOW_TRACKING_USERNAME"] = os.getenv("MLFLOW_TRACKING_USERNAME")
os.environ["MLFLOW_TRACKING_PASSWORD"] = os.getenv("MLFLOW_TRACKING_PASSWORD")


class ModelTrainer:
    def __init__(self, model_trainer_config: ModelTrainerConfig, data_transformation_artifact: DataTransformationArtifact):
        try:
            self.model_trainer_config = model_trainer_config
            self.data_transformation_artifact = data_transformation_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def track_mlflow(self, best_model, classification_metric):
        try:
            tracking_url_type_store = urlparse(mlflow.get_tracking_uri()).scheme
            with mlflow.start_run():
                mlflow.log_metric("f1_score", classification_metric.f1_score)
                mlflow.log_metric("precision", classification_metric.precision_score)
                mlflow.log_metric("recall_score", classification_metric.recall_score)
                
                mlflow.sklearn.log_model(best_model, "model")
                if tracking_url_type_store != "file":
                    mlflow.sklearn.log_model(best_model, "model", registered_model_name="NetworkPhishingModel")
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def train_model(self, X_train, y_train, X_test, y_test) -> ModelTrainerArtifact:
        try:
            models = {
                "Random Forest": RandomForestClassifier(),
                "Decision Tree": DecisionTreeClassifier(),
                "Gradient Boosting": GradientBoostingClassifier(),
                "Logistic Regression": LogisticRegression(),
                "AdaBoost": AdaBoostClassifier(),
            }

            params = {
                "Decision Tree": {'criterion': ['gini', 'entropy']},
                "Random Forest": {'n_estimators': [8, 16, 32]},
                "Gradient Boosting": {'learning_rate': [0.1, 0.01], 'n_estimators': [16, 32]},
                "Logistic Regression": {},
                "AdaBoost": {'learning_rate': [0.1, 0.01], 'n_estimators': [16, 32]}
            }

            model_report = evaluate_models(X_train=X_train, y_train=y_train, X_test=X_test, y_test=y_test, models=models, param=params)

            best_model_name = max(model_report, key=model_report.get)
            best_model = models[best_model_name]

            best_model.fit(X_train, y_train)
            y_train_pred = best_model.predict(X_train)
            y_test_pred = best_model.predict(X_test)

            classification_train_metric = get_classification_score(y_true=y_train, y_pred=y_train_pred)
            classification_test_metric = get_classification_score(y_true=y_test, y_pred=y_test_pred)

            # Track metrics in MLflow
            self.track_mlflow(best_model, classification_train_metric)
            self.track_mlflow(best_model, classification_test_metric)

            # Save model pipeline
            preprocessor = load_object(self.data_transformation_artifact.transformed_object_file_path)
            final_model = NetworkModel(preprocessor=preprocessor, model=best_model)
            os.makedirs(os.path.dirname(self.model_trainer_config.trained_model_file_path), exist_ok=True)

            save_object(self.model_trainer_config.trained_model_file_path, obj=final_model)
            save_object("final_model/model.pkl", obj=final_model)

            return ModelTrainerArtifact(
                trained_model_file_path=self.model_trainer_config.trained_model_file_path,
                train_metric_artifact=classification_train_metric,
                test_metric_artifact=classification_test_metric
            )

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def initiate_model_trainer(self) -> ModelTrainerArtifact:
        try:
            train_arr = load_numpy_array_data(self.data_transformation_artifact.transformed_train_file_path)
            test_arr = load_numpy_array_data(self.data_transformation_artifact.transformed_test_file_path)

            X_train, y_train = train_arr[:, :-1], train_arr[:, -1]
            X_test, y_test = test_arr[:, :-1], test_arr[:, -1]

            return self.train_model(X_train, y_train, X_test, y_test)

        except Exception as e:
            raise NetworkSecurityException(e, sys)
