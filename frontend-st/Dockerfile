FROM python:3.11-slim

WORKDIR /app
ADD . ./

RUN pip install -r requirements.txt

RUN mkdir ~/.streamlit
RUN cp .streamlit/config.toml ~/.streamlit/config.toml

EXPOSE 8501

WORKDIR /app

ENTRYPOINT ["streamlit", "run", "app.py"]