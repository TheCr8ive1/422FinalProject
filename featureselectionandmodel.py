import pandas as pd
import csv
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import SelectFromModel
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
from sklearn.metrics import classification_report,confusion_matrix

data = []
labels = []
y = []
with open('./data/webkb/out.csv') as csvfile:
    inputData = csv.reader(csvfile, delimiter=',', quotechar='"')
    for row in inputData:
        newRow = []
        for cell in row[3:]:
            newRow.append(float(cell))
        data.append(newRow)
        labels.append(row[1])

columns = ['sentiment','linecount','wordcount','languagevariety','avgWordLength','tagCount','UniqueTags','tagVariety','imageCount','emailCount','linkCount','weekdayCount','monthCount','courseLexScore','depLexScore','facLexScore','staffLexScore','proLexScore','stuLexScore']
classMapping = {'faculty': 1, 'staff': 2, 'student': 3, 'department': 4, 'project': 5, 'course': 6, 'other': 7}
for element in labels:
    y.append(classMapping[element])

df = pd.DataFrame(data, columns=columns)

X_train,X_test,y_train,y_test = train_test_split(df,y,test_size=0.2)

scaler = StandardScaler()
scaler.fit(X_train)

X_train = scaler.transform(X_train)
X_test = scaler.transform(X_test)

classifier = RandomForestClassifier(n_estimators = 100)
classifier.fit(X_train, y_train)
print(classifier.feature_importances_)
sel = SelectFromModel(classifier, prefit=True)
print(sel.get_support())

# This section is a manual removal of some features based on the accepted features in the print statement immediately above. 
# It would need updates if anything changed in the dataset. This is done to take some load off KNN computation
# The current feature approval is [False  True  True  True  True  True  True  True False  True False False False  True  True  True False False  True]
throwout = [1,9,11,12,13,17,18]
# The array will shorten as we step through
adjust = 0
for feature in throwout:
    # Throwout this column in every row of data
    for row in data:
        row.pop(feature - 1 - adjust)
    # Throwout the column title
    columns.pop(feature - 1 - adjust)
    adjust = adjust + 1
# Reinitialize dataframe
df = pd.DataFrame(data, columns=columns)
# Resplit
X_train,X_test,y_train,y_test = train_test_split(df,y,test_size=0.2)
# Renormalize
scaler = StandardScaler()
scaler.fit(X_train)
X_train = scaler.transform(X_train)
X_test = scaler.transform(X_test)

# Run K-Nearest Neighbor Computation in format of Elbow Plot to find best value for K
elbowMaxK = 250
elbow_y = []
for i in range(1,elbowMaxK):
    #Create KNN Classifier
    knn = KNeighborsClassifier(n_neighbors=i)

    #Train the model using the training sets
    knn.fit(X_train, y_train)

    #Predict the response for test dataset
    y_pred = knn.predict(X_test)
    elbow_y.append(np.mean(y_pred != y_test))
# Generate a plot of the elbow
plt.figure(figsize=(12, 6))
plt.plot(range(1,elbowMaxK), elbow_y, color='red', linestyle='dashed', marker='o',
        markerfacecolor='red', markersize=5)

plt.ylabel('Mean Error')
plt.title('Mean Error vs. K Value')
plt.xlabel('K')

plt.savefig('k vs mean error')

print('Minimum Error Rate:', str(min(elbow_y)))
print('Max Accuracy:', str((1 - min(elbow_y)) * 100))
print('Best K:', elbow_y.index(min(elbow_y)))


# Get metrics for the model with the optimal hyperparameter, K
#Create KNN Classifier
knn = KNeighborsClassifier(n_neighbors=elbow_y.index(min(elbow_y)))

#Train the model using the training sets
knn.fit(X_train, y_train)

#Predict the response for test dataset
y_pred = knn.predict(X_test)
print(confusion_matrix(y_test,y_pred))
print(classification_report(y_test,y_pred))