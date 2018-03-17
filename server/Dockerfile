
    FROM ubuntu:16.04
    RUN apt-get update -y
    RUN apt-get upgrade -y
    RUN apt-get install -y openssh-server
    RUN apt-get install nodejs -y
    RUN mkdir /var/run/sshd
    RUN echo 'root:qwe123' | chpasswd
    RUN sed -ri 's/^PermitRootLogin\s+.*/PermitRootLogin yes/' /etc/ssh/sshd_config
    RUN sed -ri 's/UsePAM yes/#UsePAM yes/g' /etc/ssh/sshd_config
    EXPOSE 22 80
    CMD ["/usr/sbin/sshd", "-D"]
    