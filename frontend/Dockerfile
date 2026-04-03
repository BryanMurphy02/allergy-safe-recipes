# using the node image and naming the first part of the build "builder"
FROM node:20-alpine AS builder

WORKDIR /app

# copy the dependencies into the container
# they live in the files starting with package
COPY frontend/package*.json ./

# install dependencies
RUN npm install

# copy everything into the container
COPY frontend/ .

# build the npm project
RUN npm run build


# moving on to use Node build and build Nginx
FROM nginx:alpine

# getting the Node.js build output and copying it into the container
COPY --from=builder /app/dist /usr/share/nginx/html

COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf