# 1. Install dependencies only when needed
FROM node:18-alpine AS deps

WORKDIR /app

# Copy only the yarn.lock and package.json to install dependencies
COPY package.json ./

# Install dependencies
RUN yarn install --frozen-lockfile

# 2. Build the application
FROM node:18-alpine AS builder

WORKDIR /app

# Copy dependencies from previous stage
COPY --from=deps /app/node_modules ./node_modules

# Copy the rest of the app's source code
COPY . .

# Build the Next.js app
RUN yarn build

# 3. Final image for running the app
FROM node:18-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production

# Copy the necessary files from the builder stage
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json

# Expose the port Next.js runs on
EXPOSE 3000

# Start the Next.js app
CMD ["yarn", "start"]
