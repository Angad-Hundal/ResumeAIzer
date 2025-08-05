FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

RUN npm install axios

COPY . .

RUN npm run build

# Install serve to run the production build
RUN npm install -g serve

EXPOSE 3000

CMD ["serve", "-s", "build", "-l", "tcp://0.0.0.0:3000"]