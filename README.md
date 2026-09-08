# Student Depression Risk Prediction System

A machine learning application that predicts depression risk among students using academic, lifestyle, and personal factors.

I initially focused on training and evaluating the models, then extended the project into a small application with a desktop interface, REST API, prediction history, and Docker support.

> **Note:** This project is for educational purposes only. It is not a medical diagnostic tool.

## What it does

The system takes student-related inputs and predicts a depression risk score. The result is grouped into:

* Low Risk
* Moderate Risk
* High Risk

The application also displays a short recommendation based on the predicted risk level.

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

## Machine Learning

I used Logistic Regression as a baseline and a small PyTorch neural network for comparison.

### Preprocessing

The data pipeline includes:

* One-hot encoding for categorical features
* Scaling of numerical features
* Interaction features
* Train-test splitting

### Neural Network

The neural network uses:

* Fully connected layers
* ReLU activation
* Dropout (0.3)
* Adam optimizer
* Learning-rate scheduling
* Early stopping

## Results

The models were evaluated on a held-out 20% test set.

| Metric   | Neural Network | Logistic Regression |
| -------- | -------------: | ------------------: |
| Accuracy |           0.85 |                0.85 |
| F1 Score |           0.87 |                0.87 |
| ROC-AUC  |           0.92 |                0.92 |

Both models gave almost identical results, so the neural network did not offer a clear advantage over Logistic Regression on this dataset. I kept the neural network as part of the project to experiment with PyTorch and compare it with a simpler baseline.

## Application

The trained model is connected to a desktop application built with CustomTkinter.

The application allows users to:

* Enter the required student information
* Get a depression risk prediction
* View the predicted probability and risk category
* View the recommendation associated with the result
* Access previous predictions

The project also includes a FastAPI service that exposes the prediction functionality through a REST API.

Prediction history is stored locally using SQLite.

## Project Structure

```text
main.py
│
├── src/
│   ├── GUI.py              # Desktop interface
│   ├── api.py              # FastAPI application
│   ├── config.py           # Configuration
│   ├── database.py         # SQLite operations
│   ├── evaluate.py         # Model evaluation and comparison
│   ├── logging_config.py   # Logging setup
│   ├── model_definition.py # Neural network and training
│   └── validation.py       # Input validation
│
├── tests/                  # Project tests
├── model_files/            # Saved model files
├── data/                   # Dataset
│
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Tech Stack

* **Python**
* **PyTorch**
* **Scikit-learn**
* **FastAPI**
* **CustomTkinter**
* **SQLite**
* **Docker**

## Running the Project

Clone the repository:

```bash
git clone https://github.com/AradhyaStuti/Machine-Learning-Based-Student-Depression-Risk-Prediction-System.git
cd Machine-Learning-Based-Student-Depression-Risk-Prediction-System
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

Run the desktop application:

```bash
python main.py
```

The API can be run separately using the FastAPI application in `src/api.py`.

## Dataset

The project uses the Student Depression Dataset from Kaggle, with around 28,000 student records covering demographic, academic, lifestyle, and mental-health-related factors.

## Limitations

This model should not be used as a clinical diagnosis. It was trained on a specific dataset, so its performance may not generalize to different student populations or real-world clinical settings.

The recommendations shown by the application are simple rule-based messages based on the predicted risk category.

## Author

**Aradhya Stuti**

GitHub: [@AradhyaStuti](https://github.com/AradhyaStuti)
