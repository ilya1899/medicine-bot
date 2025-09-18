module.exports = {
  apps: [{
    name: 'medicine-bot-docker',
    script: './start.sh',
    interpreter: 'bash',
    instances: 1,
    autorestart: true,
    watch: false,
    env: {
      COMPOSE_PROJECT_NAME: 'medicine-bot'
    },
    error_file: './logs/pm2-error.log',
    out_file: './logs/pm2-out.log',
    log_file: './logs/pm2-combined.log'
  }]
};