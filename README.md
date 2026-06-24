# Student Depression Risk Prediction System

## Overview

The Student Depression Risk Prediction System is a machine learning application designed to estimate the likelihood of depression among students based on academic, lifestyle, and personal factors. The objective of the project is to demonstrate how data-driven approaches can be used to analyze mental health indicators and provide meaningful insights.

The system predicts a depression risk score and classifies users into Low, Moderate, or High Risk categories. In addition to the prediction, the application provides brief recommendations tailored to the identified risk level.

The project consists of:

* A desktop application built using CustomTkinter
* A FastAPI-based REST API
* A PyTorch machine learning model
* SQLite-based prediction history storage

---

## Problem Statement

Students often experience challenges related to academic pressure, financial stress, sleep patterns, and overall well-being. These factors can contribute significantly to mental health concerns. This project aims to analyze such factors and estimate depression risk using machine learning techniques.

The system serves as an educational and analytical tool for exploring predictive modeling in the mental health domain.

---

## Features

* Depression risk prediction based on student-related attributes
* Risk categorization into Low, Moderate, and High levels
* Recommendation messages corresponding to the predicted risk level
* Desktop graphical user interface for data entry and predictions
* REST API for external integrations
* Prediction history management using SQLite
* Docker support for API deployment

---

## Input Features

The model uses the following inputs:

| Feature            | Description                      |
| ------------------ | -------------------------------- |
| Gender             | Male / Female                    |
| Age                | Student age                      |
| Work/Study Hours   | Daily study duration             |
| Academic Pressure  | Academic stress level            |
| Financial Stress   | Financial stress level           |
| Study Satisfaction | Satisfaction with studies        |
| Sleep Duration     | Average sleep duration           |
| Dietary Habits     | Quality of dietary habits        |
| Suicidal Thoughts  | Presence of suicidal thoughts    |
| Family History     | Family history of mental illness |

---

## Machine Learning Pipeline

The prediction workflow includes:

1. Data preprocessing and validation
2. One-hot encoding of categorical features
3. Feature scaling
4. Feature engineering through interaction features
5. Prediction using a neural network model

### Model Architecture

The neural network consists of:

* Three fully connected layers
* ReLU activation functions
* Dropout regularization (0.3)

### Training Strategy

The model is trained using:

* Adam Optimizer
* Learning Rate Scheduler
* Early Stopping

---

## Dataset

The model was trained using the Student Depression Dataset available on Kaggle, containing approximately 28,000 records.

The dataset includes demographic, academic, lifestyle, and mental health-related attributes that are used to predict depression risk.

---

## Model Performance

Performance was evaluated on a 20% held-out test dataset.

| Metric   | Neural Network | Logistic Regression |
| -------- | -------------- | ------------------- |
| Accuracy | 0.85           | 0.85                |
| F1 Score | 0.87           | 0.87                |
| ROC-AUC  | 0.92           | 0.92                |

The Logistic Regression baseline achieved performance comparable to the Neural Network model, indicating that the dataset is largely linearly separable. The neural network was retained primarily for experimentation and learning purposes.

---

## Technology Stack

* Python
* PyTorch
* Scikit-Learn
* FastAPI
* CustomTkinter
* SQLite
* Docker

---

## Project Structure

```text
main.py               Launches the desktop application

src/
├── GUI.py              User Interface
├── api.py              FastAPI application
├── config.py           Configuration settings
├── database.py         SQLite database operations
├── evaluate.py         Model evaluation and baseline comparison
├── logging_config.py   Logging configuration
├── model_definition.py Neural network architecture and training
├── validation.py       Input validation

tests/
model_files/
data/
```

---

## Learning Outcomes

This project provided practical experience in:

* Data preprocessing and feature engineering
* Neural network development using PyTorch
* Model evaluation and comparison
* REST API development with FastAPI
* Database integration using SQLite
* Containerization using Docker
* End-to-end machine learning application development

---

## Author

**Aradhya Stuti**

This project was developed to explore the application of machine learning techniques in mental health risk assessment while gaining hands-on experience with model development, deployment, and software engineering practices.
