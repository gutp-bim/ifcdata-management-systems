FROM continuumio/miniconda3

WORKDIR /app
COPY . .

EXPOSE 8000

ARG env_name=myenv
RUN conda create -yn ${env_name} python=3.9

ENV CONDA_DEFAULT_ENV ${env_name}

RUN echo "conda activate ${env_name}" >> ~/.bashrc
ENV PATH /opt/conda/envs/${env_name}/bin:$PATH

RUN apt-get update --allow-releaseinfo-change

RUN apt-get install -y libgl1-mesa-dev

RUN conda install -c conda-forge -c dlr-sc -c pythonocc -c oce pythonocc-core
RUN pip3 install --upgrade pip
RUN pip3 install flask
RUN pip3 install flask_cors
RUN pip3 install flask-swagger-ui
RUN pip3 install trimesh
RUN pip3 install networkx
RUN pip3 install scipy
RUN pip3 install install-ifcopenshell-python
RUN python -m install_ifcopenshell_python
RUN pip3 install psycopg2-binary

CMD ["python", "main.py"]