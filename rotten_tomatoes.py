import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
from google.colab import files
import io

# File upload for Google Colab
uploaded = files.upload()

# Load dataset from uploaded file
uploaded_file_name = next(iter(uploaded.keys()))
data = pd.read_csv(io.BytesIO(uploaded[uploaded_file_name]))

# Handle missing target values
data = data.dropna(subset=['audience_rating'])

# Select features and target
features = ['rating', 'genre', 'runtime_in_minutes', 'tomatometer_rating', 'tomatometer_count']
target = 'audience_rating'
X = data[features]
y = data[target]

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Preprocessing for numerical and categorical features
numeric_features = ['runtime_in_minutes', 'tomatometer_rating', 'tomatometer_count']
numeric_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='median')),
    ('scaler', StandardScaler())
])

categorical_features = ['rating', 'genre']
categorical_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='most_frequent')),
    ('onehot', OneHotEncoder(handle_unknown='ignore'))
])

# Combine preprocessors in a column transformer
preprocessor = ColumnTransformer(
    transformers=[
        ('num', numeric_transformer, numeric_features),
        ('cat', categorical_transformer, categorical_features)
    ]
)

# Define the model
model = RandomForestRegressor(random_state=42)

# Create and train the pipeline
pipeline = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('model', model)
])

# Hyperparameter tuning using GridSearchCV to optimize the model
param_grid = {
    'model__n_estimators': [100, 200, 300],
    'model__max_depth': [10, 20, 30],
    'model__min_samples_split': [2, 5, 10],
    'model__min_samples_leaf': [1, 2, 4]
}
grid_search = GridSearchCV(pipeline, param_grid, cv=5, n_jobs=-1, scoring='neg_mean_squared_error')

# Fit the model using GridSearchCV
grid_search.fit(X_train, y_train)

best_model = grid_search.best_estimator_

#predictions
y_pred = best_model.predict(X_test)

# Validating the model
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

# Calculate accuracy
accuracy_within_10_percent = np.mean(np.abs((y_test - y_pred) / y_test) <= 0.1) * 100

print(f'Mean Squared Error: {mse:.2f}')
print(f'R-squared: {r2:.2f}')
print(f'Accuracy within 10% of actual: {accuracy_within_10_percent:.2f}%')

# Visualize predictions
plt.scatter(y_test, y_pred, alpha=0.5)
plt.xlabel('Actual Audience Rating')
plt.ylabel('Predicted Audience Rating')
plt.title('Actual vs Predicted Audience Rating')
plt.show()
