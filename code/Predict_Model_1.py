import pandas as pd
from fbprophet.diagnostics import cross_validation
from fbprophet.diagnostics import performance_metrics
from matplotlib import pyplot as plt
from matplotlib.dates import MonthLocator, num2date
from matplotlib.ticker import FuncFormatter

import Model_Class as MC

def Model_1(months):    
    #PandasでDBの値を読み込み
    df_db = pd.read_csv('./DB/Phishing.csv')
    
    #モデル作成
    Nomal_model = MC.Model_Nomal_Prophet(months)
    #モデルフィット
    model_on_code = Nomal_model.model.fit(df_db)
    
    #予測していく
    future_data_on_code = Nomal_model.Nomal_FutureFrame()
    
    forecast_data_on_code = model_on_code.predict(future_data_on_code)
    
    #プロット
    fig0 = model_on_code.plot(forecast_data_on_code)
    fig1 = model_on_code.plot_components(forecast_data_on_code)
    