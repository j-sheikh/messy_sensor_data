# -*- coding: utf-8 -*-
"""
Automatically generated by Colaboratory.
"""
!pip install scikit-learn==0.24

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.model_selection import cross_validate
from sklearn.metrics import r2_score, mean_squared_error
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import RandomizedSearchCV
from sklearn.feature_selection import RFECV, RFE
import seaborn as sns
np.random.seed(42)

"""## init and eda ##"""

data = np.load('/content/drive/MyDrive/Intro_ML/final_project_2/data_signals.npz')

data.files

df = pd.DataFrame(data=data['X'])
df['y'] = data['y']

df['index'] = df.index

print("Number of rows: {0:,}".format(len(df)))
print("Number of columns: {0:,}".format(len(df.columns)))

display(df.head())
print('\n Data Types:')
print(df.dtypes)


def color(val): #to get some nice colors in the pandas dataframe for missing values
    color = "green"
    if val > 0:
        color = "lightcoral"
    if val > 10:
        color = "red"
    return 'background-color: %s' % color

describe = df.describe().transpose() #aggregating important data statistics
null_values = pd.DataFrame(df.isna().sum()).rename(columns={0:"num missing"}, inplace=False) 
null_values["pct missing in data"] = null_values["num missing"] / len(df) * 100 #calculate percentage of null values

describe_null = describe.join(null_values, how="left")

display(describe_null[["count", "min", "25%", "mean", "50%", "75%", "max", "std", "pct missing in data"]].round(3).style.applymap(color, subset=["pct missing in data"]))


def display_distribution(values_in, title, min_value=None, max_value=None):
    """Plot histograms of the data"""
    values = list(values_in.dropna())
    
    num_bins   = min(20, len(set(values)))
    log_prefix = ""
    
    if min_value != None:
        values = [max(min_value,x) for x in values]
    if max_value != None:
        values = [min(max_value,x) for x in values]
    
    if (min(values) > 0) & ((np.mean(values) > 2*np.median(values)) | (np.mean(values) < .75*np.median(values))):
        log_prefix = "Log of Values"
        values     = [np.log(x) for x in values] 
        
    plt.figure(figsize=(12,5))
    plt.hist(values, bins=num_bins)
    plt.xlabel("{0}Value".format(log_prefix))
    plt.ylabel("Frequency")
    plt.title("{0}\n {1}".format(title, log_prefix))
    plt.tight_layout()
    plt.show()
    
print("Short EDA:")
for ff in df.columns: #plot a histogram of the numeric data columns
    if (df[ff].dtype == "float64") | (df[ff].dtype == "int64"):
        display_distribution(df[ff], "Feature Distribution of {0}".format(ff))
        
    
plt.figure(figsize=(20,10))
sns.heatmap(df.corr(), annot=True) #correlation matrix
plt.show()

df.columns = df.columns.astype(str)

plt.figure(figsize=(17, 12))
df.plot()
plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
plt.show()

for i in range(len(df.columns)):
  plt.figure(figsize=(17, 10))
  df.iloc[:,i].plot()
  plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
  plt.show()

df.isna().sum()

df.duplicated().sum()

missing_data_first_feature = df['1'].isna()
missing_data_fifth_feature = df['5'].isna()
missing_data_seventh_feature = df['7'].isna()

df[missing_data_first_feature]

df[missing_data_fifth_feature]

df[missing_data_seventh_feature]

df1 = df.drop(columns='0')

df1[(df1.index >= 300) & (df1.index < 390)]['5'].plot()

df1[df1.index>300].head(50)

for column in df1.columns:
  df1[column].interpolate('index', inplace = True)

df1[(df1.index >= 300) & (df1.index < 390)]['5'].plot()

df1[df1.index>315].head(50)

plt.figure(figsize=(17, 10))
df1.plot()
plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
plt.show()

for i in range(len(df1.columns)):
  plt.figure(figsize=(17, 10))
  df1.iloc[:,i].plot()
  plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
  plt.show()

df1.isna().sum()

df1[df1['10']< 0]

df1[(df1.index >= 6637) & (df1.index < 6650)]

df2 = df1.drop(df1[df1['10']< 0].index)

df2 = df2.reset_index()
df2 = df2.drop(columns=['level_0'])

df2[(df2.index >= 6615) & (df2.index < 6650)]

df2.describe()

df2[np.isfinite(df2)].count()

for column in df2.columns[:-2]:
  x = df2[column].skew().round(3)
  if (x >= -0.5) and (x <= 0.5):
    print(f'column {str(column)}: {df2[column].skew().round(3)}, we are good')
  else:
    print(f'column {str(column)}: {df2[column].skew().round(3)}, need to fix')

"""8, 10 and 11 is good without chaning anything"""

for column in df2.columns[:-2]:
  x = np.log(df2[column].skew()).round(3)
  if (x >= -0.5) and (x <= 0.5):
    print(f'column {str(column)}: {np.log(df2[column].skew()).round(3)}, we are good')
  else:
    print(f'column {str(column)}: {np.log(df2[column].skew()).round(3)}, need to fix')

"""log transofrm fixes 1, 2, 3 and 6"""

for column in df2.columns[:-2]:
  x = (df2[column]** (1. / 3)).skew().round(3)
  if (x >= -0.5) and (x <= 0.5):
    print(f'column {str(column)}: {(df2[column]** (1. / 3)).skew().round(3)}, we are good')
  else:
    print(f'column {str(column)}: {(df2[column]** (1. / 3)).skew().round(3)}, need to fix')

"""with cube root transformation all features besides 10 are fixed. 10 was already good without any transformation!"""

#applying transformation on data
df3 = pd.DataFrame()
col = ['1', '2', '3', '4', '5', '6', '7', '9', '11']
for c in col:
  df3[c] = df2[c] ** (1. / 3)
df3['8'] = df2['8']
df3['10'] = df2['10']

df3



for ff in df3.columns: #plot a histogram of the numeric data columns
    if (df3[ff].dtype == "float64") | (df3[ff].dtype == "int64"):
        display_distribution(df3[ff], "Feature Distribution of {0}".format(ff))

df3.columns = df3.columns.astype(int)
df3 = df3.reindex(sorted(df3.columns), axis=1)
df3.columns = df3.columns.astype(str)

"""## model ##"""

df3

X_train, X_test, y_train, y_test = train_test_split(df3, df2['y'], random_state = 42, test_size = 0.3)
scaler = StandardScaler().fit(X_train)
X_train_scaled = scaler.transform(X_train)
X_test_scaled = scaler.transform(X_test)

linear_reg = LinearRegression()
scoring = ['neg_mean_squared_error','r2']
scores_linear = cross_validate(linear_reg, X_train_scaled, y_train.ravel(),cv=10, scoring=scoring)
print("10 fold cross validated scores model:")
print(f"Linear Regression \nMSE: {-scores_linear['test_neg_mean_squared_error'].mean().round(3)}, R2: {scores_linear['test_r2'].mean().round(3)}")

linear_reg.fit(X_train_scaled, y_train)
y_pred = linear_reg.predict(X_test_scaled)
r2 = r2_score(y_test, y_pred)
mse = mean_squared_error(y_test, y_pred)
print(f'Test Set Score without Feature Selection: R2 {r2.round(3)} and MSE {mse.round(3)}')

selector = RFECV(linear_reg, step=1, cv= 10)
selector = selector.fit(X_train_scaled, y_train)
selector.ranking_

selector.get_support()

y_pred = selector.predict(X_train_scaled)
r2 = r2_score(y_train, y_pred)
mse = mean_squared_error(y_train, y_pred)
print(f'Train Set Score with cross validation feature selection: R2 {r2.round(3)} and MSE {mse.round(3)}')

y_pred = selector.predict(X_test_scaled)
r2 = r2_score(y_test, y_pred)
mse = mean_squared_error(y_test, y_pred)
print(f'Test Set Score with cross validation and feature selection: R2 {r2.round(3)} and MSE {mse.round(3)}')
