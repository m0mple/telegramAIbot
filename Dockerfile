FROM python:3.10
WORKDIR /python-app
RUN pip install aiogram
RUN pip install requests
RUN pip install python-dotenv
COPY . .
ENV PYTHONUNBUFFERED=1
CMD ["python", "code.py"]