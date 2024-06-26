import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.feature_extraction.text import TfidfVectorizer
import tensorflow as tf
import numpy as np
import streamlit as st
import joblib
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.feature_extraction.text import TfidfVectorizer
import tensorflow as tf
from dateutil.parser import parse
import matplotlib.pyplot as plt
import re
import os
import zipfile
import tensorflow as tf
from tensorflow.keras.layers import LSTM, Bidirectional, Dropout, Dense
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, SGDRegressor, LogisticRegression, SGDClassifier
from sklearn.tree import DecisionTreeRegressor, DecisionTreeClassifier
from sklearn.ensemble import RandomForestRegressor, AdaBoostRegressor, RandomForestClassifier, AdaBoostClassifier
from xgboost import XGBRegressor, XGBClassifier
from sklearn.metrics import accuracy_score
from sklearn.metrics import mean_squared_error
import json
from sklearn.preprocessing import LabelEncoder
import tensorflow as tf

global epoch,batch,drop,returseq,bidi
epoch=0
batch=0
drop=0
returnseq=0
bidi=0

url = "sisi.csv"
dataset = pd.read_csv(url)
import numpy as np

class LazyPredict:
    def __init__(self, df, x_columns, y_column):
        self.data = df
        self.target_column = y_column
        self.X = self.data[x_columns]
        self.y = self.data[y_column]
        self.is_regression = self.is_regression()
        self.models = {}  # Dictionary to store trained models

    def is_regression(self):
        # Calculate the number of unique values in the target column
        num_unique_values = self.y.nunique()
        
        # If the number of unique values is below a threshold, consider it as classification
        classification_threshold = 10  # You can adjust this threshold as needed
        if num_unique_values <= classification_threshold:
            return False  # It's a classification problem
        else:
            return True 

    def fit_predict(self):
        if self.is_regression:
            models = {
                "Linear Regression": LinearRegression(),
                "Decision Tree": DecisionTreeRegressor(),
                "Random Forest": RandomForestRegressor(),
                "XGBoost": XGBRegressor(),
                "AdaBoost": AdaBoostRegressor(),
                "SGDRegressor": SGDRegressor()
            }
            results = {}
            for name, model in models.items():
                X_train, X_test, y_train, y_test = train_test_split(self.X, self.y, test_size=0.2, random_state=42)
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)
                mse = mean_squared_error(y_test, y_pred)
                variance = np.var(y_test)
                accuracy = (1 - (mse / variance))*100
                results[name] = accuracy

                if accuracy > 80:  # Save the model if accuracy is greater than 80%
                    self.models[name] = model
        else:
            models = {
                "Logistic Regression": LogisticRegression(),
                "Decision Tree": DecisionTreeClassifier(),
                "Random Forest": RandomForestClassifier(),
                "XGBoost": XGBClassifier(),
                "AdaBoost": AdaBoostClassifier(),
                "SGDClassifier": SGDClassifier()
            }
            results = {}
            for name, model in models.items():
                X_train, X_test, y_train, y_test = train_test_split(self.X, self.y, test_size=0.2, random_state=42)
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)
                accuracy = accuracy_score(y_test, y_pred)*100
                results[name] = accuracy

                if accuracy > 80:  # Save the model if accuracy is greater than 80%
                    self.models[name] = model

        return results

    


    def predict_new_data(self, new_data):
        if self.is_regression:
            model = LinearRegression()
        else:
            model = LogisticRegression()

        model.fit(self.X, self.y)
        predictions = model.predict(new_data)

        return predictions


class KNNUnsupervised:
    def __init__(self, k):
        self.k = k

    def fit(self, X, y):
        self.X_train = tf.constant(X, dtype=tf.float32)
        self.y_train = tf.constant(y, dtype=tf.float32)

    def predict(self, X):
        X_test = tf.constant(X, dtype=tf.float32)
        distances = tf.reduce_sum(tf.square(tf.expand_dims(X_test, axis=1) - self.X_train), axis=2)
        top_k_indices = tf.argsort(distances, axis=1)[:, :self.k]
        nearest_neighbor_labels = tf.gather(self.y_train, top_k_indices, axis=0)

        # Calculate average values of specified columns for nearest neighbors
        avg_values = tf.reduce_mean(nearest_neighbor_labels, axis=1)

        return avg_values.numpy()

class KNNUnsupervisedLSTM:
    def __init__(self, k):
        self.k = k

    def fit(self, X, y):
        # Convert string representation of LSTM units to numeric arrays
        max_layers = 0
        y_processed = []
        for units in y[:, 0]:  # Assuming LSTM units are in the 5th column
            units_array = eval(units) if isinstance(units, str) else [units]
            max_layers = max(max_layers, len(units_array))
            y_processed.append(units_array)
        
        # Pad arrays with zeros to ensure uniform length
        for i in range(len(y_processed)):
            y_processed[i] += [0] * (max_layers - len(y_processed[i]))

        # Convert input and output arrays to TensorFlow constant tensors
        self.X_train = tf.constant(X, dtype=tf.float32)
        self.y_train = tf.constant(y_processed, dtype=tf.float32)

    def predict(self, X):
        X_test = tf.constant(X, dtype=tf.float32)
        distances = tf.reduce_sum(tf.square(tf.expand_dims(X_test, axis=1) - self.X_train), axis=2)
        top_k_indices = tf.argsort(distances, axis=1)[:, :self.k]
        nearest_neighbor_labels = tf.gather(self.y_train, top_k_indices, axis=0)
        neighbor_indices = top_k_indices.numpy()

        # Calculate average values of specified columns for nearest neighbors
        avg_values = tf.reduce_mean(nearest_neighbor_labels, axis=1)
        
        return avg_values.numpy(), neighbor_indices

def handle_date_columns(dat, col):
    # Convert the column to datetime
    dat[col] = pd.to_datetime(dat[col], errors='coerce')
    # Extract date components
    dat[f'{col}_year'] = dat[col].dt.year
    dat[f'{col}_month'] = dat[col].dt.month
    dat[f'{col}_day'] = dat[col].dt.day
    # Extract time components
    dat[f'{col}_hour'] = dat[col].dt.hour
    dat[f'{col}_minute'] = dat[col].dt.minute
    dat[f'{col}_second'] = dat[col].dt.second
def is_date(string):
    try:
        # Check if the string can be parsed as a date
        parse(string)
        return True
    except ValueError:
        # If parsing fails, also check if the string matches a specific date format
        return bool(re.match(r'^\d{2}-\d{2}-\d{2}$', string))

def analyze_csv(df):
    # Get the number of records
    num_records = len(df)

    # Get the number of columns
    num_columns = len(df.columns)
    
    # Initialize counters for textual, numeric, and date columns
    num_textual_columns = 0
    num_numeric_columns = 0
    num_date_columns = 0

    # Identify textual, numeric, and date columns
    for col in df.columns:
        if pd.api.types.is_string_dtype(df[col]):
            if all(df[col].apply(is_date)):
                handle_date_columns(df, col)
                num_date_columns += 1
            else:
                num_textual_columns += 1
        elif pd.api.types.is_numeric_dtype(df[col]):
            num_numeric_columns += 1
    
    textual_columns = df.select_dtypes(include=['object']).columns
    label_encoders = {}
    for col in textual_columns:
        if col not in df.columns:
            continue
        le = LabelEncoder()
        df[col] = df[col].fillna("")  # Fill missing values with empty strings
        df[col] = le.fit_transform(df[col])
        # Store the label encoder for inverse transformation
        label_encoders[col] = le

        # Add another column for reverse inverse label encoding
        #df[f'{col}_inverse'] = le.inverse_transform(df[col])

   

    
    highly_dependent_columns = set()
    correlation_matrix = df.corr()
    for i in range(len(correlation_matrix.columns)):
        for j in range(i):
            if abs(correlation_matrix.iloc[i, j]) > 0.8:
                col1 = correlation_matrix.columns[i]
                col2 = correlation_matrix.columns[j]
                highly_dependent_columns.add(col1)
                highly_dependent_columns.add(col2)

    num_highly_dependent_columns = len(highly_dependent_columns)

        ##Output the results
    st.write("Number Of Records:", num_records)
    st.write("Number Of Columns:", num_columns)
    st.write("Number of Date Columns:", num_date_columns)

    st.write("Number of Textual Columns:", num_textual_columns)
    st.write("Number of Numeric Columns:", num_numeric_columns)

    st.write("Total Number of highly dependent columns:", num_highly_dependent_columns)
    X = dataset[['Number Of Records', 'Number Of Columns',
                 'Number of Textual Columns', 'Number of Numeric Columns', 'Total Number of highly dependent columns']].values
    y = dataset[['Optimizer','Dropout', 'Epochs', 'Batch Size']].values

    knn = KNNUnsupervised(k=3)
    knn.fit(X, y)

    # Input data for which we want to predict the average values
    q1 = np.array([[num_records,num_columns,num_textual_columns,num_numeric_columns,num_highly_dependent_columns]])  # Example input data, 1 row, 6 columns
    avg_neighbors = knn.predict(q1)

    # Apply sigmoid to the first two elements
    for i in range(len(avg_neighbors)):
        # avg_neighbors[i][0] = 1 / (1 + np.exp(-avg_neighbors[i][0]))
        # avg_neighbors[i][1] = 1 / (1 + np.exp(-avg_neighbors[i][1]))
        avg_neighbors[i][0] = 1 if avg_neighbors[i][0] >= 0.5 else 0
        # avg_neighbors[i][1] = 1 if avg_neighbors[i][1] >= 0.5 else 0

    # st.write("Output using KNN of info 1-Bidirectional,Return Sequence,Dropout,Epochs,BatchSize:")
    # st.write(avg_neighbors)
    # st.write(avg_neighbors.shape)
    global epoch,batch,drop,returseq,bidi,opi
    #poch,batch,drop,returseq,bidi
    epoch=avg_neighbors[0][2]
    batch=avg_neighbors[0][3]
    drop=avg_neighbors[0][1]
    opi=avg_neighbors[0][0]

   

    # #Dense Layer thing
    X = dataset[['Number Of Records', 'Number Of Columns', 
                 'Number of Textual Columns', 'Number of Numeric Columns', 'Total Number of highly dependent columns']].values
    y = dataset[['Hidden units']].values
    knn = KNNUnsupervisedLSTM(k=3)
    knn.fit(X, y)
    
    
    avg_neighbors, neighbor_indices = knn.predict(q1)

    # Extract Dense layers of k-nearest neighbors
    dense_layers = y[neighbor_indices[:, 0], 0]  # Extract Dense layers corresponding to the indices of k-nearest neighbors
    dense_layers_array = []
    for layers in dense_layers:
        layers_list = [int(x) for x in layers.strip('[]').split(',')]
        dense_layers_array.append(layers_list)

    # Get the maximum length of nested lists
    max_length = max(len(layers) for layers in dense_layers_array)

    # Pad shorter lists with zeros to match the length of the longest list
    padded_dense_layers_array = [layers + [0] * (max_length - len(layers)) for layers in dense_layers_array]

    # Convert the padded list of lists to a numpy array
    dense_layers_array_transpose = np.array(padded_dense_layers_array).T

    # Calculate the average of each element in the nested lists
    avg_dense_layers = np.mean(dense_layers_array_transpose, axis=1)

    global output_array_d
    # Print the output in the form of an array
    output_array_d = np.array(list(avg_dense_layers))
    # st.write("Dense layer output:")
    # st.write(output_array_d)





def load_data(file):
    df = pd.read_csv(file)
    st.subheader("1. Show first 10 records of the dataset")
    st.dataframe(df.head(10))
    analyze_csv(df)
    df.dropna(inplace=True)
    
    # Handle textual columns using label encoding
 
     # Call analyze_csv function here

    return df

def show_correlation(df):
    st.subheader("3. Show the correlation matrix and heatmap")
    numeric_columns = df.select_dtypes(include=['number']).columns
    correlation_matrix = df[numeric_columns].corr()
    st.dataframe(correlation_matrix)

    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', linewidths=.5, ax=ax)
    st.pyplot(fig)

def show_missing_values(df):
    st.subheader("2. Show the number of missing values in each column")
    missing_values = df.isnull().sum()
    st.dataframe(missing_values)
   # st.write(output_array_d)

def handle_missing_values(df):
    st.subheader("4. Handle missing values")
    numeric_columns = df.select_dtypes(include=['number']).columns
  
    textual_columns = df.select_dtypes(include=['object']).columns

    fill_option = st.radio("Choose a method to handle missing values:", ('Mean', 'Median', 'Mode', 'Drop'))

    if fill_option == 'Drop':
        df = df.dropna(subset=numeric_columns)
    else:
        fill_value = (
            df[numeric_columns].mean() if fill_option == 'Mean'
            else (df[numeric_columns].median() if fill_option == 'Median'
                  else df[numeric_columns].mode().iloc[0])
        )
        df[numeric_columns] = df[numeric_columns].fillna(fill_value)

  
    return df

def drop_column(df):
    st.subheader("5. Drop a column")
    columns_to_drop = st.multiselect("Select columns to drop:", df.columns)
    if columns_to_drop:
        df = df.drop(columns=columns_to_drop)
        st.dataframe(df)

    return df

def build_model(dense_layers,dropout):
    model = tf.keras.Sequential()
    
    for i, size in enumerate(dense_layers):
        size = int(size) 
        if i == 0:
            # For the first layer, we need to specify input_shape
            # model.add(LSTM(size, return_sequences=bool(return_sequence))) then did  model.add(LSTM(size,input_shape=(c,d), return_sequences=True))
            model.add(Dense(size,input_shape=(X_train.shape[1], 1)))
        else:
            model.add(Dense(size))
        
        
            
        
  
        if dropout > 0:  # Dropout
            model.add(Dropout(dropout))

    for nodes in dense_layers:
        model.add(Dense(nodes, activation='relu'))

    model.add(Dense(1))  # Example output layer, adjust as needed
    if(opi==0):
      model.compile(optimizer='adam', loss='mse')  # Compile the model
    else:
      model.compile(optimizer='sgd', loss='mse') 

    model.build()  # Explicitly build the model

    return model

def train_regression_model(df):
    st.subheader("6. Train a model")

    if df.empty:
        st.warning("Please upload a valid dataset.")
        return

    st.write("Select columns for X (features):")
    x_columns = st.multiselect("Select columns for X:", df.columns)

    if not x_columns:
        st.warning("Please select at least one column for X.")
        return

    st.write("Select the target column for Y:")
    y_column = st.selectbox("Select column for Y:", df.columns)

    if not y_column:
        st.warning("Please select a column for Y.")
        return
    lp = LazyPredict(df, x_columns, y_column)
    results = lp.fit_predict()

    # Check if any model's accuracy is less than 80 percent
    proceed_with_ann = any(accuracy >= 80.0 for accuracy in results.values())

    df = df.dropna(subset=[y_column])

    X = df[x_columns]
    y = df[y_column]

    # Handle textual data
    textual_columns = X.select_dtypes(include=['object']).columns
    if not textual_columns.empty:
        for col in textual_columns:
            X[col] = X[col].fillna("")  # Fill missing values with empty strings
            vectorizer = TfidfVectorizer()  # You can use any other vectorization method here
            X[col] = vectorizer.fit_transform(X[col])

    numeric_columns = X.select_dtypes(include=['number']).columns
    scaler_option = st.selectbox("Choose a scaler for numerical data:", ('None', 'StandardScaler', 'MinMaxScaler'))

    if scaler_option == 'StandardScaler':
        scaler = StandardScaler()
        X[numeric_columns] = scaler.fit_transform(X[numeric_columns])
    elif scaler_option == 'MinMaxScaler':
        scaler = MinMaxScaler()
        X[numeric_columns] = scaler.fit_transform(X[numeric_columns])
    global X_train,y_train,a,b,c,d
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    a = X_train.shape
    b = y_train.shape

    c=a[0]
    d=b[0]
    
    st.subheader("6.1-Information About Training")
    
    st.write("We have dynamically determined the Architecture of your model using an KNN model trained on our CSV properties vs architecture dataset ")
    # lstm = [int(x) for x in output_array_l]
    dense = [int(x) for x in output_array_d]
    
    # Use LazyPredict to get model accuracies
   
    if proceed_with_ann:
        st.write("One or more models from LazyPredict have accuracy more than 80%. Skipping ANN training.")
        sorted_results = {k: v for k, v in sorted(results.items(), key=lambda item: item[1], reverse=True)}
       
        for model, accuracy in sorted_results.items():
            st.write(f"- {model}: {accuracy:.2f}%")
        max_accuracy_model = max(results, key=results.get)
        best_lp_model = lp.models[max_accuracy_model]

        # Save the best LazyPredict model
        lp_model_filename = f"best_lp_model.pkl"
        joblib.dump(best_lp_model, lp_model_filename)
        st.write("Yayyyy yipeee!! Now we`re done with processing and training the model!🥳🎉")
        # Provide a download button for the best LazyPredict model
        st.subheader("7.Download Best LazyPredict Model")
        st.write("Click the button below to download the best LazyPredict model:")
        st.download_button(label="Download LazyPredict Model", data=open(lp_model_filename, "rb").read(), file_name=lp_model_filename)
        
        
    else:
        model = build_model(dense, drop)
        model.summary()
        st.write("We are going to be training your dataset from our dynamically determined hyperparameters!")
        st.write("The Parameters for your CSV are:")
        st.write("Batch Size", int(batch)) 
        st.write("Epochs", int(epoch))
        st.write("Dropout Value", drop)
        if opi == 0:
            st.write("Adam Optimizer Chosen")
        else:
            st.write("SGD Optimizer Chosen")
        st.write("Dense Layers", output_array_d)
        st.write("While we train, here`s a video that should keep you entertained while our algorithm works behind the scenes🎞️!")
        st.write("I mean, who doesn`t like a friends episode?🤔👬🏻👭🏻🫂")
        video_url = "https://www.youtube.com/watch?v=nvzkHGNdtfk&pp=ygUcZnJpZW5kcyBlcGlzb2RlIGZ1bm55IHNjZW5lcw%3D%3D"  # Example YouTube video URL
        st.video(video_url)

        history = model.fit(X_train, y_train, validation_data=(X_test, y_test), epochs=int(epoch), batch_size=int(batch))

        global train_loss
        global val_loss
        train_loss = history.history['loss']
        val_loss = history.history['val_loss']

        st.subheader("Training Information➕➖")
        st.write("Final Training loss is-", train_loss[-1])
        st.write("Final Validation loss is-", val_loss[-1])
        st.write("Training losses", train_loss)
        st.write("Validation losses", val_loss)
      

        ploty()

        model_filename = "model.h5"
        model.save(model_filename)
        st.success(f"Model saved as {model_filename}")

        st.subheader("7.Download the trained model")
        st.download_button(label="Download Model", data=open(model_filename, "rb").read(), file_name=model_filename)
        # Save LazyPredict models


def ploty():
  st.subheader("Plotting the loss vs epoch graph")
  epochsi = range(1, len(train_loss) + 1)

  plt.plot(epochsi, train_loss, 'bo', label='Training loss') # 'bo' = blue dots
  plt.plot(epochsi, val_loss, 'r', label='Validation loss') # 'r' = red line   
  plt.title('Training and Validation Loss')
  plt.xlabel('Epochs')
  plt.ylabel('Loss')
  plt.legend()
  st.write("Yayyyy yipeee!! Now we`re done with processing and training the model!🥳🎉")

# Optionally, you can save the plot or display it
# plt.savefig('loss_plot.png')  # Save the plot as a PNG file
# plt.show()  # Display the plot
#newest
  st.pyplot(plt)


def download_updated_dataset(df):
    st.subheader("8. Download the updated dataset")
    csv_file = df.to_csv(index=False)
    st.download_button("Download CSV", csv_file, "Updated_Dataset.csv", key="csv_download")

def main():
    st.title("CSV Dataset Analysis and Model Training App")
    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

    if uploaded_file is not None:
        st.info("File uploaded successfully!")
        df = load_data(uploaded_file)
        
        if not df.select_dtypes(include=['number']).empty or df.select_dtypes(include=['object']).empty :
            show_missing_values(df)#hi
            show_correlation(df)
            df = handle_missing_values(df)
            
        
        
        df = drop_column(df)
        train_regression_model(df)
  
        download_updated_dataset(df)

if __name__ == "__main__":
    main()
