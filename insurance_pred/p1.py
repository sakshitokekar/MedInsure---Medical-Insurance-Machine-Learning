#import libraries
import pandas as pd
from sklearn import preprocessing
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import pickle

#load the data
data = pd.read_csv('insurance.csv')

#understand the data
print(data.info())
print(data.isnull().sum())

#Droping unwanted data
data.drop(columns = ['region'], axis = 1, inplace = True)
print(data.head())

#Dividing feature and target
features = data[['age','sex','bmi','children','smoker']]
target = data['charges']
print(features.head())
print(target.head())

#handling categorical data
new_features = pd.get_dummies(features,drop_first = True)
print(new_features)

#train test
x_train,x_test,y_train,y_test = train_test_split(new_features, target, random_state = 625)

#model
model = RandomForestRegressor(n_estimators = 100)
model.fit(x_train,y_train)

#score
mtr = model.score(x_train,y_train)
mt = model.score(x_test,y_test)
print("Training Score --->", round(mtr,3),"%")
print("Testing Score ---->", round(mt,3),"%")

#save the model
with open("db.model","wb") as f:
	pickle.dump(model, f)