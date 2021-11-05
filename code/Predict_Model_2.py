import pandas as pd
from fbprophet.diagnostics import cross_validation
from fbprophet.diagnostics import performance_metrics
from matplotlib import pyplot as plt
from matplotlib.dates import MonthLocator, num2date
from matplotlib.ticker import FuncFormatter

import numpy as np

import Model_Class as MC


def Model_2(months, train_time):
    #PandasでDBの値を読み込み
    df_db = pd.read_csv('./DB/Phishing.csv')
    

    df_db = df_db.astype({'y': int})
                
    #ハイパーパラメータに合わせたモデル作成
    cap = int(np.percentile(df_db.y,95))
    floor = int(np.percentile(df_db.y,5))
    
    #モデル作成
    Hyper_model = MC.hyper_search_model(months, train_time)
    Hyper_model.Create_Model(df_db)

    
    df_db['cap']=cap
    df_db['floor']=floor

    #モデルフィット
    model_on_code = Hyper_model.model
    model_on_code.fit(df_db)
    
    #予測していく
    future_data_on_code = Hyper_model.Hyper_FutureFrame()
    future_data_on_code['cap'] =cap
    future_data_on_code['floor'] =floor
    forecast_data_on_code = model_on_code.predict(future_data_on_code)

    
    #プロット
    fig0 = model_on_code.plot(forecast_data_on_code, xlabel='Date', ylabel='Phishing_Count') 
    fig1 = model_on_code.plot_components(forecast_data_on_code)
    

