FROM ubuntu

ENV USERNAME=curso
ENV GROUP=curso
ENV ID=1001

RUN apt-get update && apt-get upgrade -y
RUN apt-get install python3 -y
RUN groupadd -g $ID $GROUP
RUN useradd -mu $ID -g $ID $USERNAME

USER $USERNAME

CMD [ "bash" ]
