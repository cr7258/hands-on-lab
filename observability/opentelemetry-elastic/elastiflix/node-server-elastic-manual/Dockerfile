FROM node:18.17.0

WORKDIR /app

COPY ["package.json", "./"]
RUN ls
RUN npm install --production
COPY . .

EXPOSE 3001

CMD ["node", "index.js"]

