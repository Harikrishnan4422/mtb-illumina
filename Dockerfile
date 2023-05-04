FROM aai_mdd_base:latest

COPY . /usr/app
WORKDIR /usr/app

RUN apt-get update && apt-get -y upgrade
RUN chmod -R +x .
ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "myenv", "python3", "mdd_results.py"]