FROM ubuntu:22.04

WORKDIR /cdmo


# Install dependencies
RUN apt update && apt install -y python3 python3-pip wget unzip

# Install MiniZinc
RUN apt install -y libglu1-mesa-dev libegl1
RUN wget https://github.com/MiniZinc/MiniZincIDE/releases/download/2.8.4/MiniZincIDE-2.8.4-bundle-linux-x86_64.tgz &&\
tar -xf MiniZincIDE-2.8.4-bundle-linux-x86_64.tgz &&\
mv MiniZincIDE-2.8.4-bundle-linux-x86_64 minizinc &&\
cp -r minizinc/bin/* /usr/local/bin &&\
cp -r minizinc/lib/* /usr/local/lib &&\
cp -r minizinc/share/* /usr/local/share &&\
cp -r minizinc/lib/* /usr/local/lib

# Install CVC5
RUN wget https://github.com/cvc5/cvc5/releases/download/cvc5-1.2.0/cvc5-Linux-x86_64-static.zip &&\
unzip cvc5-Linux-x86_64-static.zip -d cvc5 &&\
cp -r cvc5/cvc5-Linux-x86_64-static/bin/* /usr/local/bin &&\
cp -r cvc5/cvc5-Linux-x86_64-static/include/* /usr/local/include &&\
cp -r cvc5/cvc5-Linux-x86_64-static/lib/* /usr/local/lib

# Install OpenSMT
RUN wget https://github.com/usi-verification-and-security/opensmt/releases/download/v2.7.0/opensmt-2.7.0-x64-linux.tar.bz2 &&\
tar -xf opensmt-2.7.0-x64-linux.tar.bz2 &&\
cp opensmt /usr/local/bin/opensmt

# Install SMTInterpol
RUN apt install -y openjdk-21-jre-headless
RUN wget http://ultimate.informatik.uni-freiburg.de/smtinterpol/smtinterpol-2.5-1384-g98f115aa.jar &&\
mv smtinterpol-2.5-1384-g98f115aa.jar /usr/local/share/smtinterpol.jar

# Install Yices
RUN wget https://github.com/SRI-CSL/yices2/releases/download/Yices-2.6.5/yices-2.6.5-x86_64-pc-linux-gnu-static-gmp.tar.gz &&\
tar -xf yices-2.6.5-x86_64-pc-linux-gnu-static-gmp.tar.gz &&\
cp -r yices-2.6.5/bin/* /usr/local/bin &&\
cp -r yices-2.6.5/etc/* /usr/local/etc &&\
cp -r yices-2.6.5/include/* /usr/local/include &&\
cp -r yices-2.6.5/lib/* /usr/local/lib

# Install amplpy and all necessary amplpy.modules:
# ARG AMPL_KEY 
# RUN python3 -m pip install amplpy --no-cache-dir # Install amplpy
# RUN python3 -m amplpy.modules install highs cbc scip --no-cache-dir # Install modules
# RUN python3 -m amplpy.modules activate ${AMPL_KEY}

# For Windows EOL char
RUN apt install -y dos2unix

COPY . .
RUN pip3 install -r requirements.txt
RUN dos2unix ./entrypoint.sh

RUN chmod +x ./entrypoint.sh
ENTRYPOINT [ "./entrypoint.sh" ]