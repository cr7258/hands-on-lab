FROM node:18.17.0

WORKDIR /app

COPY ["package.json", "./"]
RUN ls
RUN npm install --production
COPY . .

RUN npm install --save @opentelemetry/api
RUN npm install --save @opentelemetry/auto-instrumentations-node


EXPOSE 3001

CMD ["node", "--require", "@opentelemetry/auto-instrumentations-node/register", "index.js"]