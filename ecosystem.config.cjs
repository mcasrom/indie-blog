module.exports = {
  apps: [
    {
      name: 'indie-blog',
      cwd: '/home/deploy/indie-blog',
      script: 'node',
      args: 'dist/server/entry.mjs',
      env: {
        PORT: '3020',
        HOST: '127.0.0.1',
        NODE_ENV: 'production',
      },
    },
  ],
};
