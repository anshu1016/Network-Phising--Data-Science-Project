from networksecurity.components.data_ingestion import DataIngestion
from networksecurity.components.data_validation import DataValidation
from networksecurity.components.data_transformation import DataTransformation
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.entity.config_entity import DataIngestionConfig, DataValidationConfig,DataTransformationConfig
from networksecurity.entity.config_entity import TrainingPipelineConfig
from networksecurity.entity.artifact_entity import DataIngestionArtifact
import sys

if __name__ =='__main__':
    try:
        trainingPipelineConfig = TrainingPipelineConfig()

        # DATA INGESTION
        dataIngestionConfig = DataIngestionConfig(trainingPipelineConfig)
        data_ingestion = DataIngestion(dataIngestionConfig)
        logging.info('Initiate the Data Ingestion')
        dataingestionartifact = data_ingestion.initiate_data_ingestion()
        print(dataingestionartifact)
        logging.info('Initiate the Data Ingestion Completed')


        # DATA VALIDATION

        dataValidationConfig = DataValidationConfig(trainingPipelineConfig)
        data_validation = DataValidation(dataingestionartifact,dataValidationConfig)
        logging.info('Initiate the Data Validation')
        datavalidationartifact = data_validation.initiate_data_validation()
        print(datavalidationartifact)
        logging.info('the Data Validation Completed')


        # DATA TRANSFORMATION
        dataTransformationConfig = DataTransformationConfig(trainingPipelineConfig)
        data_transformation = DataTransformation(datavalidationartifact,dataTransformationConfig)
        logging.info('Initiate the Data Transformation')
        data_transformation_artifact = data_transformation.initiate_data_transformation()
        print(data_transformation_artifact)
        logging.info('the Data Transformation Completed')        

    except Exception as e:
        raise NetworkSecurityException(e,sys)


