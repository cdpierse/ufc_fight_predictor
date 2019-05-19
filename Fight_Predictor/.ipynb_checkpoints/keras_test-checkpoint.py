from keras.models import Sequential
from keras.layers import Dense
from sklearn.model_selection import train_test_split
from sklearn.datasets import mldata
import numpy

numpy.random.seed(7)

dataset = numpy.loadtxt("pima-indians-diabetes.csv",delimiter=',')
X = dataset[0:,0:8]
Y = dataset[:,8]
x_train, x_test, y_train, y_test = train_test_split(X,Y, test_size=0.1)


model = Sequential()
model.add(Dense(12,input_dim=8,activation='relu'))
model.add(Dense(12,activation='relu'))
model.add(Dense(1,activation='sigmoid'))


model.compile(loss='binary_crossentropy', optimizer='adam',metrics=['accuracy'])

model.fit(x_train,y_train, epochs= 100, batch_size= 10)

scores = model.evaluate(x_test,y_test)
print(scores)
predictions = model.predict(x_test)
rounded = [round(x[0]) for x in predictions]

print(predictions)

print("\n%s: %.2f%%" % (model.metrics_names[1], scores[1]*100))
# prediction = model.predict(x_test[1])
# print('prediction is %s and actual is %s' %(prediction,y_test[1]))


