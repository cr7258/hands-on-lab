FROM node:14

WORKDIR /app

COPY ["package.json", "./"]
RUN ls
RUN npm install --production
COPY . .

CMD ["node", "index.js"]
