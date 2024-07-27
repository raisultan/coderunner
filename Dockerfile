FROM golang:1.22

WORKDIR /coderunner

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

COPY . .

RUN go mod download
RUN go build -o coderunner ./coderunner

EXPOSE 8000

CMD ["./coderunner/coderunner"]
