FROM python:3.8

WORKDIR /issuer

RUN pip install --upgrade pip

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt /issuer/requirements.txt

RUN pip install --no-cache-dir -r /issuer/requirements.txt

COPY ./app /issuer/app

CMD bash -c "python app/setup.py && python app/service.py"
