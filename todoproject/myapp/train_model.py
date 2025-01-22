# import numpy as np
# import pandas as pd
# from sklearn.ensemble import RandomForestRegressor
# from sklearn.model_selection import train_test_split, cross_val_score
# from sklearn.metrics import mean_squared_error, r2_score
# import pickle

# # Step 1: Generate Realistic Data
# def generate_training_data():
#     np.random.seed(42)  # For reproducibility
    
#     # Generate sample data
#     distances = np.random.uniform(5, 500, 1000)  # Distances in km
#     traffic_levels = np.random.choice([1, 2, 3], 1000)  # Traffic levels: 1=low, 2=medium, 3=high
#     vehicle_types = np.random.choice([1, 2, 3], 1000)  # 1=Car, 2=Bike, 3=Truck

#     # Generate fuel efficiency (km per liter) based on vehicle type
#     fuel_efficiency = np.where(vehicle_types == 1, 
#                                 np.random.uniform(10, 15, 1000),  # Cars
#                                 np.where(vehicle_types == 2, 
#                                          np.random.uniform(25, 35, 1000),  # Bikes
#                                          np.random.uniform(5, 8, 1000)))  # Trucks
    
#     # Calculate fuel consumption (liters) = distance / fuel efficiency + traffic factor
#     traffic_factor = traffic_levels * np.random.uniform(0.1, 0.5, 1000)
#     fuel_consumption = (distances / fuel_efficiency) + traffic_factor

#     # Create a DataFrame
#     data = pd.DataFrame({
#         "distance": distances,
#         "traffic_level": traffic_levels,
#         "vehicle_type": vehicle_types,
#         "fuel_consumption": fuel_consumption
#     })

#     return data

# # Step 2: Prepare Training Data
# data = generate_training_data()
# X = data[["distance", "traffic_level", "vehicle_type"]]
# y = data["fuel_consumption"]

# # Step 3: Train-Test Split
# X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# # Step 4: Train a Random Forest Model
# model = RandomForestRegressor(n_estimators=100, random_state=42)
# model.fit(X_train, y_train)

# # Step 5: Evaluate Model
# y_pred = model.predict(X_test)
# mse = mean_squared_error(y_test, y_pred)
# r2 = r2_score(y_test, y_pred)

# print(f"Model Performance:")
# print(f"Mean Squared Error: {mse:.2f}")
# print(f"R^2 Score: {r2:.2f}")

# # Step 6: Cross-Validation
# cv_scores = cross_val_score(model, X, y, cv=5, scoring="r2")
# print(f"Cross-Validation R^2 Scores: {cv_scores}")
# print(f"Average R^2 Score: {cv_scores.mean():.2f}")

# # Step 7: Save the Model
# with open('fuel_model.pkl', 'wb') as file:
#     pickle.dump(model, file)

# print("Model trained and saved as fuel_model.pkl")



# train_model.py
import googlemaps
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestRegressor

# Initialize Google Maps client with your API key
gmaps = googlemaps.Client(key='AIzaSyCDbkU7RW7-ZaUyhVfuqvOyB-QvAtX-yWk')

# Function to fetch route details from Google Maps API
def get_route_details(source, destination):
    directions = gmaps.directions(source, destination, mode="driving", departure_time="now")
    if directions:
        route = directions[0]['legs'][0]
        distance = route['distance']['value'] / 1000  # Convert meters to kilometers
        duration = route['duration']['value'] / 60  # Convert seconds to minutes
        return distance, duration
    else:
        return None, None

# Function to train the model and save it
def train_model():
    # Sample data: Replace this with your actual dataset
    data = {
        'distance': [10, 50, 100, 150, 200],
        'traffic': [1, 2, 3, 4, 5],
        'vehicle_type': [1, 2, 1, 2, 1],
        'fuel_consumption': [8, 12, 18, 24, 30]  # Example fuel consumption values
    }

    df = pd.DataFrame(data)

    # Features and target
    X = df[['distance', 'traffic', 'vehicle_type']]
    y = df['fuel_consumption']

    # Initialize and train the model
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)

    # Save the trained model to a file
    joblib.dump(model, 'fuel_prediction_model.pkl')
    print("Model trained and saved as 'fuel_prediction_model.pkl'")

# Function to predict fuel consumption based on input data
def predict_fuel(distance, traffic, vehicle_type):
    # Load the trained model
    model = joblib.load('fuel_prediction_model.pkl')

    # Prepare input data in the correct format for prediction
    input_data = pd.DataFrame({'distance': [distance], 'traffic': [traffic], 'vehicle_type': [vehicle_type]})

    # Predict fuel consumption
    fuel_prediction = model.predict(input_data)
    return fuel_prediction[0]

# Example usage
if __name__ == '__main__':
    # Train and save the model (you can run this separately when you first train the model)
    # Uncomment the line below to train the model:
    # train_model()

    # Example: Get route details from Google Maps and predict fuel consumption
    source = "New York, NY"
    destination = "Los Angeles, CA"
    
    distance, traffic = get_route_details(source, destination)
    
    if distance is None or traffic is None:
        print("Error: Unable to fetch route details.")
    else:
        print(f"Distance: {distance} km, Traffic Duration: {traffic} minutes")

        # Predict fuel consumption based on the fetched route details
        vehicle_type = 1  # Example vehicle type
        predicted_fuel = predict_fuel(distance, traffic, vehicle_type)
        print(f"Predicted Fuel Consumption: {predicted_fuel} liters")


