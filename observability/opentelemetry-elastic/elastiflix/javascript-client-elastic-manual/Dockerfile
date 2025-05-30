FROM node:14 as build-deps
WORKDIR /usr/src/app
COPY package.json yarn.lock ./
RUN yarn
COPY ./ ./
RUN yarn build

FROM nginx:1.25.1-alpine
RUN apk --no-cache add curl
COPY --from=build-deps /usr/src/app/build /usr/share/nginx/html
COPY ./nginx/nginx.conf /etc/nginx/conf.d/default.conf
# Copy .env file and shell script to container
WORKDIR /usr/share/nginx/html
COPY --from=build-deps /usr/src/app/scripts ./
#COPY .env .
RUN chmod +x ./*.sh
# EXPOSE 8080
# Add bash
RUN apk add --no-cache bash
# CMD ["/bin/bash", "-c", "/usr/share/nginx/html/retrieve-credentials.sh && nginx -g \"daemon off;\""]
CMD [ "/bin/bash", "./docker-entrypoint.sh" ]
# CMD ["nginx", "-g", "daemon off;"]
