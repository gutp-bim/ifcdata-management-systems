FROM continuumio/miniconda3

WORKDIR /app
COPY . .

EXPOSE 8080

ARG env_name=myenv
RUN conda create -yn ${env_name} python=3.9

ENV CONDA_DEFAULT_ENV ${env_name}

RUN echo "conda activate ${env_name}" >> ~/.bashrc
ENV PATH /opt/conda/envs/${env_name}/bin:$PATH

RUN conda install -c conda-forge -c dlr-sc -c pythonocc -c oce pythonocc-core
RUN conda install -c conda-forge ifcopenshell 
RUN pip3 install --upgrade pip
RUN pip3 install  flask
RUN pip3 instaall flask_cors
RUN pip3 install flask-swagger-ui
RUN pip3 install python-arango
RUN pip3 install inject
RUN pip3 install rdflib

CMD ["python", "main.py"]