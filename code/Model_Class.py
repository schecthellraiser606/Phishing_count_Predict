from fbprophet import Prophet
from matplotlib import pyplot as plt
from matplotlib.dates import MonthLocator, num2date
from matplotlib.ticker import FuncFormatter

import numpy as np
import optuna
from sklearn.model_selection import train_test_split


#簡易なデフォルトモデル
class Model_Nomal_Prophet(object):
  
    def __init__(self, days):
      self.__days = days
      self.model = Prophet(mcmc_samples=300)
      
      
    #グラフプロット関数のラベル変更
    def plot(self, fcst, ax=None, uncertainty=True, plot_cap=True, xlabel='ds', ylabel='y', figsize=...):
        xlabel = 'Date'
        ylabel = 'Phishing_Count'
        return self.model.plot(fcst, ax=ax, uncertainty=uncertainty, plot_cap=plot_cap, xlabel=xlabel, ylabel=ylabel, figsize=figsize)
    
    #予測期間における、土日を抜いたフレーム作成
    def Nomal_FutureFrame(self):
        future = self.model.make_future_dataframe(periods=self.__days, freq = 'm')
        future = future[future["ds"].dt.weekday < 5]
        
        return future

  
#簡易評価グラフプロット
class figure_draw(object):
  
  #MSE、MAPEのプロット
  def plot_MSE_MAPE(self, data):
        fig = plt.figure()
        ax1 = fig.add_subplot(2, 1, 1)
        ax1.plot(data['horizon'], data['mse'])
        ax1.set_xlabel("days elapsed")
        ax1.set_ylabel("MSE")
        
        ax2 = fig.add_subplot(2, 1, 2)
        ax2.plot(data['horizon'], data['mape']);
        ax2.set_xlabel("days elapsed")
        ax2.set_ylabel("MAPE")
        
        return fig
      
      

#ハイパーパラメータ探索モデル
class hyper_search_model(object):
  
  def __init__(self, days, train_time):
      self.__days = days
      self.__train_time = train_time 
  
  def __objective_variable(self, train,valid):
      '''`ハイパーパラメータ策定関数
      '''  
      train = train.astype({'y': int})
      valid = valid.astype({'y': int})
      cap = int(np.percentile(train.y,95))
      floor = int(np.percentile(train.y,5))
      


      def objective(trial):
              #ハイパーパラメータ定義
              params = {#探索範囲指定
                      'changepoint_range' : trial.suggest_discrete_uniform('changepoint_range',0.8,0.95,0.001),
                      'n_changepoints' : trial.suggest_int('n_changepoints',20,35),
                      'mcmc_samples' : trial.suggest_int('mcmc_samples',30,66),
                      'changepoint_prior_scale' : trial.suggest_discrete_uniform('changepoint_prior_scale',0.001,0.5,0.001),
                      'seasonality_prior_scale' : trial.suggest_discrete_uniform('seasonality_prior_scale',1,25,0.5),
                      'yearly_fourier' : trial.suggest_int('yearly_fourier',5,15),
                      'quaterly_fourier' : trial.suggest_int('quaterly_fourier',3,10),
                      'yearly_prior' : trial.suggest_discrete_uniform('yearly_prior',1,25,0.5),
                      'quaterly_prior' : trial.suggest_discrete_uniform('quaterly_prior',1,25,0.5)
                      }
              # モデル作成
              m=Prophet(
                      changepoint_range = params['changepoint_prior_scale'],
                      n_changepoints=params['n_changepoints'],
                      changepoint_prior_scale=params['changepoint_prior_scale'],
                      seasonality_prior_scale = params['seasonality_prior_scale'],
                      yearly_seasonality=False,
                      weekly_seasonality=False,
                      daily_seasonality=False,
                      growth='logistic',
                      seasonality_mode='additive',
                      mcmc_samples=params['mcmc_samples'])
              m.add_seasonality(name='yearly', period=365.25, fourier_order=params['yearly_fourier'],prior_scale=params['yearly_prior'])
              m.add_seasonality(name='quaterly', period=365.25/4, fourier_order=params['quaterly_fourier'],prior_scale=params['quaterly_prior'])

              train['cap']=cap
              train['floor']=floor
              
              #モデルフィット
              m.fit(train)
              #予測範囲のフレーム作成
              future = m.make_future_dataframe(periods=len(valid))

              future['cap']=cap
              future['floor']=floor  
              
              #モデルでの予測
              forecast = m.predict(future)
              valid_forecast = forecast.tail(len(valid))
              
              #MAPEに従って実値と比較評価
              val_mape = np.mean(np.abs((valid_forecast.yhat-valid.y)/valid.y))*100
              return val_mape

      return objective
    
  def __optuna_parameter(self, train,valid):
    #optunaクラス定義
    study = optuna.create_study(sampler=optuna.samplers.RandomSampler(seed=42))
    #指定したtrain_timeの間探索する
    study.optimize(self.__objective_variable(train,valid), timeout=self.__train_time)
    #最適なハイパーパラメータのセッティング
    optuna_best_params = study.best_params

    return study
  
  def Create_Model(self, df_tmp):
    #train, testで分割し、ハイパーパラメータを適用したモデル作成
    df_train, df_test = train_test_split(df_tmp)
    study = self.__optuna_parameter(df_train, df_test)
  
    model = Prophet(
            changepoint_range = study.best_params['changepoint_prior_scale'],
            n_changepoints=study.best_params['n_changepoints'],
            seasonality_prior_scale = study.best_params['seasonality_prior_scale'],
          changepoint_prior_scale=study.best_params['changepoint_prior_scale'],
            yearly_seasonality=False,
            weekly_seasonality=False,
            daily_seasonality=False,
            growth='logistic',
            seasonality_mode='additive',
            mcmc_samples = study.best_params['mcmc_samples'])
    model.add_seasonality(name='yearly', period=365.25, fourier_order=study.best_params['yearly_fourier'],prior_scale=study.best_params['yearly_prior'])
    model.add_seasonality(name='quaterly', period=365.25/4, fourier_order=study.best_params['quaterly_fourier'],prior_scale=study.best_params['quaterly_prior'])
    
    self.model = model
    
  def Hyper_FutureFrame(self):
    future = self.model.make_future_dataframe(periods=self.__days, freq = 'm')
    future = future[future["ds"].dt.weekday < 5]

    return future

    
 
  
    
      
    
      
      
    
      