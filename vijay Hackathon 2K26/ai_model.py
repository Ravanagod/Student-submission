from sklearn.linear_model import LogisticRegression
import numpy as np

X=np.array([[1],[2],[3],[4],[5]])
y=np.array([0,0,0,1,1])

model=LogisticRegression()
model.fit(X,y)

def predict_late(days_before_deadline):

    prediction=model.predict([[days_before_deadline]])

    return "Likely Late" if prediction[0]==1 else "On Time"