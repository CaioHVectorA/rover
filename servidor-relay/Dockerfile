FROM node:20-alpine

WORKDIR /app

# Instala apenas dependências de produção para imagem mínima e rápida
COPY package*.json ./
RUN npm ci --only=production

# Copia código-fonte e interface estática
COPY server.js ./
COPY public/ ./public/

ENV PORT=8080
ENV NODE_ENV=production

EXPOSE 8080

CMD ["node", "server.js"]
