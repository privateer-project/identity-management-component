FROM python:3.8

WORKDIR /verifier

RUN pip install --upgrade pip

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt /verifier/requirements.txt

RUN pip install --no-cache-dir -r /verifier/requirements.txt

COPY ./app /verifier/app

CMD bash -c "python app/setup.py && python app/service.py"
