<<<<<<< HEAD
FROM aai_mdd_base:latest
=======
FROM aai_mdd:v1_base
>>>>>>> b38db8b (Initial commit for v2 prod version)

COPY . /usr/app
WORKDIR /usr/app

RUN apt-get update && apt-get -y upgrade
RUN chmod -R +x .
<<<<<<< HEAD
ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "myenv", "python3", "mdd_results.py"]
=======
ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "myenv", "python3", "mdd_results.py"]
>>>>>>> b38db8b (Initial commit for v2 prod version)
