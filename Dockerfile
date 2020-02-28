FROM python:3.7.3

# Copy dependency definitions
ADD docker_environment /tmp/docker_environment

# Install Python Dependencies
RUN pip install -r /tmp/docker_environment/python_packages.txt

# Install Linux Dependencies
RUN apt-get update; apt-get install -y $(awk '{print $1'} /tmp/docker_environment/linux_packages.txt)
RUN bash /tmp/docker_environment/custom.sh

# Copy scripts
COPY api/*.py /home/
COPY startup.sh /home/

EXPOSE 5035
EXPOSE 8500

WORKDIR /home/

CMD ["bash", "./startup.sh"]
