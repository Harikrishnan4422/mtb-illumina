#FROM aai_mdd:v1_base

FROM asia-south1-docker.pkg.dev/aai-migration-july25/aai-base-images/aai_mdd:v1_base
COPY . /usr/app
WORKDIR /usr/app

RUN apt-get update && apt-get -y upgrade
RUN chmod -R +x .
ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "myenv", "python3", "mdd_results.py"]
