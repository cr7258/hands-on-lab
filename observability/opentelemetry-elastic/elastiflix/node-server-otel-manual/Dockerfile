FROM node:18.17.0

WORKDIR /app

COPY ["package.json", "./"]
RUN ls
RUN npm install --production
COPY . .

# the package.json contains these already so we don't have to 
# install them individually
# RUN npm install --save @opentelemetry/api
# RUN npm install --save @opentelemetry/resources
# RUN npm install --save @opentelemetry/semantic-conventions
# RUN npm install --save @opentelemetry/sdk-trace-node 
# RUN npm install --save @opentelemetry/sdk-trace-base
# RUN npm install --save @opentelemetry/exporter-trace-otlp-grpc 
# RUN npm install --save @opentelemetry/instrumentation
# RUN npm install --save @opentelemetry/instrumentation-http
# RUN npm install --save @opentelemetry/instrumentation-express 

EXPOSE 3001

CMD ["node", "index.js"]