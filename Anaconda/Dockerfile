FROM continuumio/anaconda3:2021.05

RUN mkdir /code && \
    pip install --upgrade pip && \
    conda update conda && \
    conda install -c conda-forge pystan && \
    conda install -c conda-forge fbprophet && \
    pip install pysqlite3 && \
    pip install optuna 

WORKDIR /code

EXPOSE 8888

ENTRYPOINT ["jupyter-lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root", "--NotebookApp.token=''"]
 
CMD ["--notebook-dir=/code"]

