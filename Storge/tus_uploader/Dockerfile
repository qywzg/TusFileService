FROM golang:1.8

# WORKDIR /go/
ADD ./ ./

# uuid
RUN mkdir -p /go/src/github.com/google/
RUN mv ./packages/uuid /go/src/github.com/google/
# tusd
RUN mkdir -p /go/src/github.com/tus/
RUN mv ./packages/tusd /go/src/github.com/tus/
# lockfile
RUN mkdir -p /go/src/gopkg.in/Acconut/
RUN mv ./packages/lockfile.v1 /go/src/gopkg.in/Acconut/

RUN go get -d -v ./
RUN go build
# RUN go install  
# FROM golang:onbuild
